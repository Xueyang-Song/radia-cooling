from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from rcml.data.codec import decode_structure_vector, material_accuracy, thickness_mae_nm, target_matrix_from_records
from rcml.data.dataset import LoadedDataset, SCALAR_TARGETS
from rcml.data.splits import make_dataset_split
from rcml.models.generative_core import (
    conditioning_spec_from_dataset,
    feature_tensor_to_target_matrix,
)
from rcml.models.torch_forward import _resolve_device


DEFAULT_CVAE_TARGETS = [
    "solar_reflectance",
    "window_emissivity",
    "cooling_power_proxy_w_m2",
]


class StructuredFeatureDecoder(nn.Module):
    def __init__(self, input_dim: int, feature_dim: int) -> None:
        super().__init__()
        self.output = nn.Linear(input_dim, feature_dim)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.output(hidden)


class CategoricalStructureDecoder(nn.Module):
    def __init__(self, input_dim: int, structure_layout) -> None:
        super().__init__()
        self.layout = structure_layout
        self.material_head = nn.Linear(
            input_dim,
            structure_layout.functional_layers * len(structure_layout.dielectric_materials),
        )
        self.thickness_head = nn.Linear(input_dim, structure_layout.functional_layers)

    def forward(self, hidden: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        batch_size = hidden.shape[0]
        num_materials = len(self.layout.dielectric_materials)
        material_logits = self.material_head(hidden).view(
            batch_size,
            self.layout.functional_layers,
            num_materials,
        )
        material_probs = torch.softmax(material_logits, dim=-1)
        thickness_range = self.layout.max_thickness_nm - self.layout.min_thickness_nm
        thickness_values = self.layout.min_thickness_nm + torch.sigmoid(self.thickness_head(hidden)) * thickness_range

        parts: list[torch.Tensor] = []
        for layer_index in range(self.layout.functional_layers):
            parts.append(material_probs[:, layer_index, :])
            parts.append(thickness_values[:, layer_index : layer_index + 1])
        total_thickness = thickness_values.sum(dim=1, keepdim=True) + self.layout.reflector_thickness_nm
        parts.append(total_thickness)
        feature_vector = torch.cat(parts, dim=1)
        return feature_vector, material_logits, thickness_values


class ConditionalVAE(nn.Module):
    def __init__(
        self,
        condition_dim: int,
        feature_dim: int,
        structure_layout,
        latent_dim: int = 16,
        hidden_dims: tuple[int, ...] = (160, 128, 96),
        decoder_mode: str = "continuous",
    ) -> None:
        super().__init__()
        if decoder_mode not in {"continuous", "categorical"}:
            raise ValueError(f"Unsupported decoder mode: {decoder_mode}")
        encoder_layers: list[nn.Module] = []
        current_dim = condition_dim + feature_dim
        for hidden_dim in hidden_dims:
            encoder_layers.append(nn.Linear(current_dim, hidden_dim))
            encoder_layers.append(nn.ReLU())
            current_dim = hidden_dim
        self.encoder = nn.Sequential(*encoder_layers)
        self.mu_head = nn.Linear(current_dim, latent_dim)
        self.logvar_head = nn.Linear(current_dim, latent_dim)

        decoder_layers: list[nn.Module] = []
        current_dim = condition_dim + latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(current_dim, hidden_dim))
            decoder_layers.append(nn.ReLU())
            current_dim = hidden_dim
        self.decoder_backbone = nn.Sequential(*decoder_layers)
        self.decoder_mode = decoder_mode
        if decoder_mode == "categorical":
            self.structured_decoder = CategoricalStructureDecoder(current_dim, structure_layout)
        else:
            self.structured_decoder = StructuredFeatureDecoder(current_dim, feature_dim)

    def encode(self, features_norm: torch.Tensor, condition_norm: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        hidden = self.encoder(torch.cat([features_norm, condition_norm], dim=1))
        return self.mu_head(hidden), self.logvar_head(hidden)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode_details(
        self,
        latent: torch.Tensor,
        condition_norm: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor | None, torch.Tensor | None]:
        hidden = self.decoder_backbone(torch.cat([latent, condition_norm], dim=1))
        if self.decoder_mode == "categorical":
            feature_vector, material_logits, thickness_values = self.structured_decoder(hidden)
            return feature_vector, material_logits, thickness_values
        feature_vector = self.structured_decoder(hidden)
        return feature_vector, None, None

    def decode(self, latent: torch.Tensor, condition_norm: torch.Tensor) -> torch.Tensor:
        feature_vector, _, _ = self.decode_details(latent, condition_norm)
        return feature_vector

    def forward(
        self,
        features_norm: torch.Tensor,
        condition_norm: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor | None, torch.Tensor | None, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encode(features_norm, condition_norm)
        latent = self.reparameterize(mu, logvar)
        reconstruction, material_logits, thickness_values = self.decode_details(latent, condition_norm)
        return reconstruction, material_logits, thickness_values, mu, logvar


@dataclass
class CVAEBundle:
    model: ConditionalVAE
    target_mean: np.ndarray
    target_std: np.ndarray
    structure_mean: np.ndarray
    structure_std: np.ndarray
    target_names: list[str]
    structure_layout: object
    latent_dim: int
    decoder_mode: str

    def predict_feature_matrix(self, target_matrix: np.ndarray, device: str = "cpu") -> np.ndarray:
        return self._decode(target_matrix=target_matrix, num_samples=1, device=device, seed=None)[0]

    def sample_feature_matrix(
        self,
        target_matrix: np.ndarray,
        num_samples: int,
        device: str = "cpu",
        seed: int | None = None,
    ) -> np.ndarray:
        return self._decode(target_matrix=target_matrix, num_samples=num_samples, device=device, seed=seed)

    def _decode(self, target_matrix: np.ndarray, num_samples: int, device: str, seed: int | None) -> np.ndarray:
        resolved_device = _resolve_device(device)
        self.model.eval()
        self.model = self.model.to(resolved_device)
        target_array = np.asarray(target_matrix, dtype=np.float32)
        target_norm = (target_array - self.target_mean) / self.target_std
        condition_tensor = torch.as_tensor(target_norm, dtype=torch.float32, device=resolved_device)
        if seed is not None:
            torch.manual_seed(seed)
        outputs: list[np.ndarray] = []
        with torch.no_grad():
            for _ in range(num_samples):
                latent = torch.zeros((condition_tensor.shape[0], self.latent_dim), dtype=torch.float32, device=resolved_device)
                if num_samples > 1:
                    latent = torch.randn((condition_tensor.shape[0], self.latent_dim), dtype=torch.float32, device=resolved_device)
                prediction = self.model.decode(latent, condition_tensor).cpu().numpy()
                outputs.append(prediction)
        return np.stack(outputs, axis=0)


@dataclass(frozen=True)
class CVAETrainingResult:
    model: CVAEBundle
    metrics: dict[str, float]
    split_summary: dict[str, object]


def available_cvae_targets() -> list[str]:
    return list(SCALAR_TARGETS)


def default_cvae_targets() -> list[str]:
    return list(DEFAULT_CVAE_TARGETS)


def train_conditional_vae(
    dataset: LoadedDataset,
    target_names: list[str],
    reflectance_forward_path: str,
    emissivity_forward_path: str,
    test_size: float,
    random_seed: int,
    split_mode: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    reconstruction_loss_weight: float,
    target_loss_weight: float,
    kl_weight: float,
    latent_dim: int,
    device: str,
    decoder_mode: str = "continuous",
) -> CVAETrainingResult:
    _validate_target_names(target_names)
    resolved_device = _resolve_device(device)
    torch.manual_seed(random_seed)
    np.random.seed(random_seed)

    split = make_dataset_split(dataset=dataset, split_mode=split_mode, test_size=test_size, random_seed=random_seed)
    spec = conditioning_spec_from_dataset(dataset, target_names)
    x = target_matrix_from_records(dataset.records, target_names).astype(np.float32)
    y = dataset.feature_matrix.astype(np.float32)
    x_train = x[split.train_indices]
    x_test = x[split.test_indices]
    y_train = y[split.train_indices]
    y_test = y[split.test_indices]

    target_mean = x_train.mean(axis=0)
    target_std = x_train.std(axis=0)
    target_std = np.where(target_std < 1e-6, 1.0, target_std)
    structure_mean = y_train.mean(axis=0)
    structure_std = y_train.std(axis=0)
    structure_std = np.where(structure_std < 1e-6, 1.0, structure_std)

    x_train_norm = (x_train - target_mean) / target_std
    y_train_norm = (y_train - structure_mean) / structure_std

    train_ds = TensorDataset(
        torch.as_tensor(x_train_norm, dtype=torch.float32),
        torch.as_tensor(y_train_norm, dtype=torch.float32),
        torch.as_tensor(y_train, dtype=torch.float32),
    )
    train_loader = DataLoader(train_ds, batch_size=min(batch_size, len(train_ds)), shuffle=True)

    reflectance_bundle = torch.load(reflectance_forward_path, weights_only=False)
    emissivity_bundle = torch.load(emissivity_forward_path, weights_only=False)
    reflectance_bundle.model = reflectance_bundle.model.to(resolved_device)
    emissivity_bundle.model = emissivity_bundle.model.to(resolved_device)
    for param in reflectance_bundle.model.parameters():
        param.requires_grad = False
    for param in emissivity_bundle.model.parameters():
        param.requires_grad = False

    model = ConditionalVAE(
        condition_dim=x.shape[1],
        feature_dim=y.shape[1],
        structure_layout=spec.structure_layout,
        latent_dim=latent_dim,
        decoder_mode=decoder_mode,
    ).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    material_criterion = nn.CrossEntropyLoss()

    target_mean_t = torch.as_tensor(target_mean, dtype=torch.float32, device=resolved_device)
    target_std_t = torch.as_tensor(target_std, dtype=torch.float32, device=resolved_device)
    thickness_min = float(spec.structure_layout.min_thickness_nm)
    thickness_range = float(spec.structure_layout.max_thickness_nm - spec.structure_layout.min_thickness_nm)

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for target_norm_batch, feature_norm_batch, feature_raw_batch in train_loader:
            target_norm_batch = target_norm_batch.to(resolved_device)
            feature_norm_batch = feature_norm_batch.to(resolved_device)
            feature_raw_batch = feature_raw_batch.to(resolved_device)
            optimizer.zero_grad(set_to_none=True)
            reconstructed_features, material_logits, thickness_values, mu, logvar = model(feature_norm_batch, target_norm_batch)
            reconstructed_targets = feature_tensor_to_target_matrix(
                feature_tensor=reconstructed_features,
                reflectance_bundle=reflectance_bundle,
                emissivity_bundle=emissivity_bundle,
                spec=spec,
            )
            reconstructed_targets_norm = (reconstructed_targets - target_mean_t) / target_std_t

            if decoder_mode == "categorical":
                if material_logits is None or thickness_values is None:
                    raise RuntimeError("Categorical decoder expected material logits and thickness values.")
                material_targets = _material_target_indices(feature_raw_batch, spec.structure_layout)
                thickness_targets = _thickness_target_values(feature_raw_batch, spec.structure_layout)
                material_loss = torch.stack(
                    [
                        material_criterion(material_logits[:, layer_index, :], material_targets[:, layer_index])
                        for layer_index in range(spec.structure_layout.functional_layers)
                    ]
                ).mean()
                thickness_values_norm = (thickness_values - thickness_min) / thickness_range
                thickness_targets_norm = (thickness_targets - thickness_min) / thickness_range
                reconstruction_loss = material_loss + criterion(thickness_values_norm, thickness_targets_norm)
            else:
                reconstruction_loss = criterion(reconstructed_features, feature_raw_batch)
            target_loss = criterion(reconstructed_targets_norm, target_norm_batch)
            kl_loss = -0.5 * torch.mean(1.0 + logvar - mu.pow(2) - logvar.exp())
            loss = (
                reconstruction_loss_weight * reconstruction_loss
                + target_loss_weight * target_loss
                + kl_weight * kl_loss
            )
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item()) * int(target_norm_batch.shape[0])

        if epoch == 0 or (epoch + 1) % max(1, epochs // 5) == 0 or epoch + 1 == epochs:
            avg_loss = epoch_loss / len(train_ds)
            print(f"epoch {epoch + 1:>4}/{epochs} cvae_loss={avg_loss:.6f}")

    bundle = CVAEBundle(
        model=model.cpu(),
        target_mean=target_mean.astype(np.float32),
        target_std=target_std.astype(np.float32),
        structure_mean=structure_mean.astype(np.float32),
        structure_std=structure_std.astype(np.float32),
        target_names=list(target_names),
        structure_layout=spec.structure_layout,
        latent_dim=latent_dim,
        decoder_mode=decoder_mode,
    )

    predicted_features = bundle.predict_feature_matrix(x_test, device=str(resolved_device))
    predicted_targets = feature_tensor_to_target_matrix(
        feature_tensor=torch.as_tensor(predicted_features, dtype=torch.float32, device=resolved_device),
        reflectance_bundle=reflectance_bundle,
        emissivity_bundle=emissivity_bundle,
        spec=spec,
    ).cpu().numpy()
    feature_rmse = float(np.sqrt(np.mean((predicted_features - y_test) ** 2)))
    metrics = _compute_cvae_metrics(
        target_names=target_names,
        y_true_targets=x_test,
        y_pred_targets=predicted_targets,
        y_true_features=y_test,
        y_pred_features=predicted_features,
        structure_layout=spec.structure_layout,
    )
    metrics["feature_rmse"] = feature_rmse
    return CVAETrainingResult(model=bundle, metrics=metrics, split_summary=split.summary)


def _compute_cvae_metrics(
    target_names: list[str],
    y_true_targets: np.ndarray,
    y_pred_targets: np.ndarray,
    y_true_features: np.ndarray,
    y_pred_features: np.ndarray,
    structure_layout,
) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for index, name in enumerate(target_names):
        metrics[f"{name}_mae"] = float(np.mean(np.abs(y_true_targets[:, index] - y_pred_targets[:, index])))

    true_samples = [
        decode_structure_vector(y_true_features[index], structure_layout, sample_id=f"true_{index:06d}")
        for index in range(y_true_features.shape[0])
    ]
    pred_samples = [
        decode_structure_vector(y_pred_features[index], structure_layout, sample_id=f"pred_{index:06d}")
        for index in range(y_pred_features.shape[0])
    ]
    layer_material_accuracy, exact_combo_accuracy = material_accuracy(true_samples, pred_samples)
    layer_thickness_mae, total_thickness_mae = thickness_mae_nm(true_samples, pred_samples)
    metrics.update(
        {
            "layer_material_accuracy": float(layer_material_accuracy),
            "exact_combo_accuracy": float(exact_combo_accuracy),
            "layer_thickness_mae_nm": float(layer_thickness_mae),
            "total_thickness_mae_nm": float(total_thickness_mae),
        }
    )
    return metrics


def _validate_target_names(target_names: list[str]) -> None:
    if not target_names:
        raise ValueError("At least one CVAE target is required.")
    invalid = [name for name in target_names if name not in SCALAR_TARGETS]
    if invalid:
        raise ValueError(f"Unsupported CVAE targets: {invalid}")


def _material_target_indices(feature_raw_batch: torch.Tensor, structure_layout) -> torch.Tensor:
    num_materials = len(structure_layout.dielectric_materials)
    block_width = structure_layout.block_width
    targets = []
    for layer_index in range(structure_layout.functional_layers):
        offset = layer_index * block_width
        material_slice = feature_raw_batch[:, offset : offset + num_materials]
        targets.append(material_slice.argmax(dim=1))
    return torch.stack(targets, dim=1).long()


def _thickness_target_values(feature_raw_batch: torch.Tensor, structure_layout) -> torch.Tensor:
    num_materials = len(structure_layout.dielectric_materials)
    block_width = structure_layout.block_width
    targets = []
    for layer_index in range(structure_layout.functional_layers):
        offset = layer_index * block_width + num_materials
        targets.append(feature_raw_batch[:, offset])
    return torch.stack(targets, dim=1)