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
    StructuredFeatureDecoder,
    conditioning_spec_from_dataset,
    feature_tensor_to_target_matrix,
)
from rcml.models.torch_forward import _resolve_device


DEFAULT_DIFFUSION_TARGETS = [
    "solar_reflectance",
    "window_emissivity",
    "cooling_power_proxy_w_m2",
]


class SinusoidalTimeEmbedding(nn.Module):
    def __init__(self, embedding_dim: int) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim

    def forward(self, timesteps: torch.Tensor) -> torch.Tensor:
        half_dim = self.embedding_dim // 2
        device = timesteps.device
        exponent = -np.log(10000.0) / max(half_dim - 1, 1)
        frequencies = torch.exp(torch.arange(half_dim, device=device, dtype=torch.float32) * exponent)
        angles = timesteps.float().unsqueeze(1) * frequencies.unsqueeze(0)
        embedding = torch.cat([torch.sin(angles), torch.cos(angles)], dim=1)
        if self.embedding_dim % 2 == 1:
            embedding = torch.cat([embedding, torch.zeros((timesteps.shape[0], 1), device=device)], dim=1)
        return embedding


class ConditionalDiffusionModel(nn.Module):
    def __init__(
        self,
        condition_dim: int,
        feature_dim: int,
        structure_layout,
        time_embedding_dim: int = 64,
        hidden_dims: tuple[int, ...] = (256, 192, 128),
    ) -> None:
        super().__init__()
        self.time_embedding = SinusoidalTimeEmbedding(time_embedding_dim)
        layers: list[nn.Module] = []
        current_dim = feature_dim + condition_dim + time_embedding_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(current_dim, hidden_dim))
            layers.append(nn.ReLU())
            current_dim = hidden_dim
        self.backbone = nn.Sequential(*layers)
        self.decoder = StructuredFeatureDecoder(current_dim, structure_layout)

    def forward(
        self,
        noisy_features_norm: torch.Tensor,
        condition_norm: torch.Tensor,
        timesteps: torch.Tensor,
    ) -> torch.Tensor:
        time_embedding = self.time_embedding(timesteps)
        hidden = self.backbone(torch.cat([noisy_features_norm, condition_norm, time_embedding], dim=1))
        return self.decoder(hidden)


@dataclass
class DiffusionBundle:
    model: ConditionalDiffusionModel
    target_mean: np.ndarray
    target_std: np.ndarray
    structure_mean: np.ndarray
    structure_std: np.ndarray
    target_names: list[str]
    structure_layout: object
    diffusion_steps: int
    beta_start: float
    beta_end: float

    @property
    def feature_dim(self) -> int:
        return int(self.structure_mean.shape[0])

    def predict_feature_matrix(self, target_matrix: np.ndarray, device: str = "cpu") -> np.ndarray:
        return self._sample(target_matrix=target_matrix, num_samples=1, device=device, seed=None)[0]

    def sample_feature_matrix(
        self,
        target_matrix: np.ndarray,
        num_samples: int,
        device: str = "cpu",
        seed: int | None = None,
    ) -> np.ndarray:
        return self._sample(target_matrix=target_matrix, num_samples=num_samples, device=device, seed=seed)

    def _sample(self, target_matrix: np.ndarray, num_samples: int, device: str, seed: int | None) -> np.ndarray:
        resolved_device = _resolve_device(device)
        self.model.eval()
        self.model = self.model.to(resolved_device)
        if seed is not None:
            torch.manual_seed(seed)

        target_array = np.asarray(target_matrix, dtype=np.float32)
        target_norm = (target_array - self.target_mean) / self.target_std
        condition_tensor = torch.as_tensor(target_norm, dtype=torch.float32, device=resolved_device)
        structure_mean_t = torch.as_tensor(self.structure_mean, dtype=torch.float32, device=resolved_device)
        structure_std_t = torch.as_tensor(self.structure_std, dtype=torch.float32, device=resolved_device)
        _, _, alpha_bars = _make_diffusion_schedule(
            diffusion_steps=self.diffusion_steps,
            beta_start=self.beta_start,
            beta_end=self.beta_end,
            device=resolved_device,
        )

        outputs: list[np.ndarray] = []
        with torch.no_grad():
            for sample_index in range(num_samples):
                if num_samples == 1 and seed is None:
                    noisy = torch.zeros((condition_tensor.shape[0], self.feature_dim), dtype=torch.float32, device=resolved_device)
                else:
                    if seed is not None:
                        torch.manual_seed(seed + sample_index)
                    noisy = torch.randn((condition_tensor.shape[0], self.feature_dim), dtype=torch.float32, device=resolved_device)

                predicted_raw = None
                for step in reversed(range(self.diffusion_steps)):
                    timestep_tensor = torch.full(
                        (condition_tensor.shape[0],),
                        step,
                        dtype=torch.long,
                        device=resolved_device,
                    )
                    predicted_raw = self.model(noisy, condition_tensor, timestep_tensor)
                    predicted_norm = (predicted_raw - structure_mean_t) / structure_std_t
                    alpha_bar_t = alpha_bars[step]
                    if step > 0:
                        alpha_bar_prev = alpha_bars[step - 1]
                        eps_pred = (noisy - torch.sqrt(alpha_bar_t) * predicted_norm) / torch.sqrt(1.0 - alpha_bar_t)
                        noisy = torch.sqrt(alpha_bar_prev) * predicted_norm + torch.sqrt(1.0 - alpha_bar_prev) * eps_pred
                    else:
                        noisy = predicted_norm

                if predicted_raw is None:
                    raise RuntimeError("Diffusion sampling failed to produce a feature vector.")
                outputs.append(predicted_raw.cpu().numpy())
        return np.stack(outputs, axis=0)


@dataclass(frozen=True)
class DiffusionTrainingResult:
    model: DiffusionBundle
    metrics: dict[str, float]
    split_summary: dict[str, object]


def available_diffusion_targets() -> list[str]:
    return list(SCALAR_TARGETS)


def default_diffusion_targets() -> list[str]:
    return list(DEFAULT_DIFFUSION_TARGETS)


def train_conditional_diffusion(
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
    diffusion_steps: int,
    beta_start: float,
    beta_end: float,
    device: str,
) -> DiffusionTrainingResult:
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

    model = ConditionalDiffusionModel(
        condition_dim=x.shape[1],
        feature_dim=y.shape[1],
        structure_layout=spec.structure_layout,
    ).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    target_mean_t = torch.as_tensor(target_mean, dtype=torch.float32, device=resolved_device)
    target_std_t = torch.as_tensor(target_std, dtype=torch.float32, device=resolved_device)
    structure_mean_t = torch.as_tensor(structure_mean, dtype=torch.float32, device=resolved_device)
    structure_std_t = torch.as_tensor(structure_std, dtype=torch.float32, device=resolved_device)
    _, _, alpha_bars = _make_diffusion_schedule(
        diffusion_steps=diffusion_steps,
        beta_start=beta_start,
        beta_end=beta_end,
        device=resolved_device,
    )

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for target_norm_batch, feature_norm_batch in train_loader:
            target_norm_batch = target_norm_batch.to(resolved_device)
            feature_norm_batch = feature_norm_batch.to(resolved_device)
            optimizer.zero_grad(set_to_none=True)

            timestep_tensor = torch.randint(0, diffusion_steps, (target_norm_batch.shape[0],), device=resolved_device)
            noise = torch.randn_like(feature_norm_batch)
            alpha_bar_t = alpha_bars.index_select(0, timestep_tensor).unsqueeze(1)
            noisy_features = torch.sqrt(alpha_bar_t) * feature_norm_batch + torch.sqrt(1.0 - alpha_bar_t) * noise

            predicted_raw = model(noisy_features, target_norm_batch, timestep_tensor)
            predicted_norm = (predicted_raw - structure_mean_t) / structure_std_t
            predicted_targets = feature_tensor_to_target_matrix(
                feature_tensor=predicted_raw,
                reflectance_bundle=reflectance_bundle,
                emissivity_bundle=emissivity_bundle,
                spec=spec,
            )
            predicted_targets_norm = (predicted_targets - target_mean_t) / target_std_t

            reconstruction_loss = criterion(predicted_norm, feature_norm_batch)
            target_loss = criterion(predicted_targets_norm, target_norm_batch)
            loss = reconstruction_loss_weight * reconstruction_loss + target_loss_weight * target_loss
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item()) * int(target_norm_batch.shape[0])

        if epoch == 0 or (epoch + 1) % max(1, epochs // 5) == 0 or epoch + 1 == epochs:
            avg_loss = epoch_loss / len(train_ds)
            print(f"epoch {epoch + 1:>4}/{epochs} diffusion_loss={avg_loss:.6f}")

    bundle = DiffusionBundle(
        model=model.cpu(),
        target_mean=target_mean.astype(np.float32),
        target_std=target_std.astype(np.float32),
        structure_mean=structure_mean.astype(np.float32),
        structure_std=structure_std.astype(np.float32),
        target_names=list(target_names),
        structure_layout=spec.structure_layout,
        diffusion_steps=diffusion_steps,
        beta_start=float(beta_start),
        beta_end=float(beta_end),
    )

    predicted_features = bundle.predict_feature_matrix(x_test, device=str(resolved_device))
    predicted_targets = feature_tensor_to_target_matrix(
        feature_tensor=torch.as_tensor(predicted_features, dtype=torch.float32, device=resolved_device),
        reflectance_bundle=reflectance_bundle,
        emissivity_bundle=emissivity_bundle,
        spec=spec,
    ).cpu().numpy()

    metrics = _compute_diffusion_metrics(
        target_names=target_names,
        y_true_targets=x_test,
        y_pred_targets=predicted_targets,
        y_true_features=y_test,
        y_pred_features=predicted_features,
        structure_layout=spec.structure_layout,
    )
    metrics["feature_rmse"] = float(np.sqrt(np.mean((predicted_features - y_test) ** 2)))
    return DiffusionTrainingResult(model=bundle, metrics=metrics, split_summary=split.summary)


def _make_diffusion_schedule(
    diffusion_steps: int,
    beta_start: float,
    beta_end: float,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    betas = torch.linspace(beta_start, beta_end, diffusion_steps, dtype=torch.float32, device=device)
    alphas = 1.0 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)
    return betas, alphas, alpha_bars


def _compute_diffusion_metrics(
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
        raise ValueError("At least one diffusion target is required.")
    invalid = [name for name in target_names if name not in SCALAR_TARGETS]
    if invalid:
        raise ValueError(f"Unsupported diffusion targets: {invalid}")