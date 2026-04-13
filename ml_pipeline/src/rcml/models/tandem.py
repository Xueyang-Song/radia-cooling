from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from rcml.data.codec import decode_structure_vector, material_accuracy, thickness_mae_nm
from rcml.data.codec import target_matrix_from_records
from rcml.data.dataset import LoadedDataset, SCALAR_TARGETS
from rcml.data.splits import make_dataset_split
from rcml.models.generative_core import (
    StructuredFeatureDecoder,
    conditioning_spec_from_dataset,
    feature_tensor_to_target_matrix,
)
from rcml.models.torch_forward import _resolve_device


DEFAULT_TANDEM_TARGETS = [
    "solar_reflectance",
    "window_emissivity",
    "cooling_power_proxy_w_m2",
]


@dataclass
class TandemBundle:
    inverse_model: nn.Module
    target_mean: np.ndarray
    target_std: np.ndarray
    structure_mean: np.ndarray
    structure_std: np.ndarray
    target_names: list[str]
    structure_layout: object

    def predict_feature_matrix(self, target_matrix: np.ndarray, device: str = "cpu") -> np.ndarray:
        self.inverse_model.eval()
        resolved_device = _resolve_device(device)
        x = np.asarray(target_matrix, dtype=np.float32)
        normalized = (x - self.target_mean) / self.target_std
        with torch.no_grad():
            tensor = torch.as_tensor(normalized, dtype=torch.float32, device=resolved_device)
            prediction = self.inverse_model.to(resolved_device)(tensor).cpu().numpy()
        return prediction


@dataclass(frozen=True)
class TandemTrainingResult:
    model: TandemBundle
    metrics: dict[str, float]
    split_summary: dict[str, object]


class TandemInverseNet(nn.Module):
    def __init__(self, condition_dim: int, structure_layout, hidden_dims: tuple[int, ...] = (128, 128, 96)) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        current_dim = condition_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(current_dim, hidden_dim))
            layers.append(nn.ReLU())
            current_dim = hidden_dim
        self.backbone = nn.Sequential(*layers)
        self.decoder = StructuredFeatureDecoder(current_dim, structure_layout)

    def forward(self, condition: torch.Tensor) -> torch.Tensor:
        hidden = self.backbone(condition)
        return self.decoder(hidden)


def available_tandem_targets() -> list[str]:
    return list(SCALAR_TARGETS)


def default_tandem_targets() -> list[str]:
    return list(DEFAULT_TANDEM_TARGETS)


def train_tandem_model(
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
    target_loss_weight: float,
    structure_loss_weight: float,
    device: str,
) -> TandemTrainingResult:
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
        torch.as_tensor(x_train, dtype=torch.float32),
        torch.as_tensor(y_train, dtype=torch.float32),
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

    inverse_model = TandemInverseNet(condition_dim=x.shape[1], structure_layout=spec.structure_layout).to(resolved_device)
    optimizer = torch.optim.Adam(inverse_model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    target_mean_t = torch.as_tensor(target_mean, dtype=torch.float32, device=resolved_device)
    target_std_t = torch.as_tensor(target_std, dtype=torch.float32, device=resolved_device)
    structure_mean_t = torch.as_tensor(structure_mean, dtype=torch.float32, device=resolved_device)
    structure_std_t = torch.as_tensor(structure_std, dtype=torch.float32, device=resolved_device)

    for epoch in range(epochs):
        inverse_model.train()
        epoch_loss = 0.0
        for target_norm_batch, target_raw_batch, feature_raw_batch, feature_norm_batch in train_loader:
            target_norm_batch = target_norm_batch.to(resolved_device)
            target_raw_batch = target_raw_batch.to(resolved_device)
            feature_norm_batch = feature_norm_batch.to(resolved_device)
            optimizer.zero_grad(set_to_none=True)
            predicted_features = inverse_model(target_norm_batch)
            predicted_targets = feature_tensor_to_target_matrix(
                feature_tensor=predicted_features,
                reflectance_bundle=reflectance_bundle,
                emissivity_bundle=emissivity_bundle,
                spec=spec,
            )
            predicted_targets_norm = (predicted_targets - target_mean_t) / target_std_t
            predicted_features_norm = (predicted_features - structure_mean_t) / structure_std_t

            target_loss = criterion(predicted_targets_norm, target_norm_batch)
            structure_loss = criterion(predicted_features_norm, feature_norm_batch)
            loss = target_loss_weight * target_loss + structure_loss_weight * structure_loss
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item()) * int(target_norm_batch.shape[0])

        if epoch == 0 or (epoch + 1) % max(1, epochs // 5) == 0 or epoch + 1 == epochs:
            avg_loss = epoch_loss / len(train_ds)
            print(f"epoch {epoch + 1:>4}/{epochs} tandem_loss={avg_loss:.6f}")

    bundle = TandemBundle(
        inverse_model=inverse_model.cpu(),
        target_mean=target_mean.astype(np.float32),
        target_std=target_std.astype(np.float32),
        structure_mean=structure_mean.astype(np.float32),
        structure_std=structure_std.astype(np.float32),
        target_names=list(target_names),
        structure_layout=spec.structure_layout,
    )

    predicted_features = bundle.predict_feature_matrix(x_test, device=str(resolved_device))
    predicted_targets = feature_tensor_to_target_matrix(
        feature_tensor=torch.as_tensor(predicted_features, dtype=torch.float32, device=resolved_device),
        reflectance_bundle=reflectance_bundle,
        emissivity_bundle=emissivity_bundle,
        spec=spec,
    ).cpu().numpy()

    metrics = _compute_tandem_metrics(
        target_names=target_names,
        y_true_targets=x_test,
        y_pred_targets=predicted_targets,
        y_true_features=y_test,
        y_pred_features=predicted_features,
        structure_layout=spec.structure_layout,
    )
    return TandemTrainingResult(model=bundle, metrics=metrics, split_summary=split.summary)


def _compute_tandem_metrics(
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
        raise ValueError("At least one tandem target is required.")
    invalid = [name for name in target_names if name not in SCALAR_TARGETS]
    if invalid:
        raise ValueError(f"Unsupported tandem targets: {invalid}")