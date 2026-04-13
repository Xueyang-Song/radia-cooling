from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from rcml.data.dataset import LoadedDataset
from rcml.data.splits import make_dataset_split


@dataclass
class TorchForwardBundle:
    model: nn.Module
    input_mean: np.ndarray
    input_std: np.ndarray
    output_mean: np.ndarray
    output_std: np.ndarray
    spectrum_kind: str
    wavelengths_um: np.ndarray
    split_summary: dict[str, object]
    metrics: dict[str, float]

    def predict(self, feature_matrix: np.ndarray, device: str = "cpu") -> np.ndarray:
        self.model.eval()
        x = np.asarray(feature_matrix, dtype=np.float32)
        normalized = (x - self.input_mean) / self.input_std
        with torch.no_grad():
            tensor = torch.as_tensor(normalized, dtype=torch.float32, device=device)
            pred = self.model.to(device)(tensor).cpu().numpy()
        denormalized = pred * self.output_std + self.output_mean
        return np.clip(denormalized, 0.0, 1.0)

    def predict_tensor(self, feature_tensor: torch.Tensor) -> torch.Tensor:
        device = feature_tensor.device
        self.model = self.model.to(device)
        self.model.eval()
        input_mean = torch.as_tensor(self.input_mean, dtype=torch.float32, device=device)
        input_std = torch.as_tensor(self.input_std, dtype=torch.float32, device=device)
        output_mean = torch.as_tensor(self.output_mean, dtype=torch.float32, device=device)
        output_std = torch.as_tensor(self.output_std, dtype=torch.float32, device=device)
        normalized = (feature_tensor - input_mean) / input_std
        pred = self.model(normalized)
        denormalized = pred * output_std + output_mean
        return torch.clamp(denormalized, 0.0, 1.0)


class ForwardMLP(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, hidden_dims: tuple[int, ...] = (256, 256, 128)) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        current_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(current_dim, hidden_dim))
            layers.append(nn.ReLU())
            current_dim = hidden_dim
        layers.append(nn.Linear(current_dim, output_dim))
        self.network = nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def train_torch_forward_surrogate(
    dataset: LoadedDataset,
    spectrum_kind: str,
    test_size: float,
    random_seed: int,
    split_mode: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: str,
) -> TorchForwardBundle:
    if epochs <= 0:
        raise ValueError("epochs must be positive")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")

    torch.manual_seed(random_seed)
    np.random.seed(random_seed)

    split = make_dataset_split(dataset=dataset, split_mode=split_mode, test_size=test_size, random_seed=random_seed)
    x = np.asarray(dataset.feature_matrix, dtype=np.float32)
    y = np.asarray(dataset.spectrum_matrix(spectrum_kind), dtype=np.float32)

    x_train = x[split.train_indices]
    x_test = x[split.test_indices]
    y_train = y[split.train_indices]
    y_test = y[split.test_indices]

    input_mean = x_train.mean(axis=0)
    input_std = x_train.std(axis=0)
    input_std = np.where(input_std < 1e-6, 1.0, input_std)
    output_mean = y_train.mean(axis=0)
    output_std = y_train.std(axis=0)
    output_std = np.where(output_std < 1e-6, 1.0, output_std)

    x_train_norm = (x_train - input_mean) / input_std
    x_test_norm = (x_test - input_mean) / input_std
    y_train_norm = (y_train - output_mean) / output_std
    y_test_norm = (y_test - output_mean) / output_std

    train_ds = TensorDataset(
        torch.as_tensor(x_train_norm, dtype=torch.float32),
        torch.as_tensor(y_train_norm, dtype=torch.float32),
    )
    train_loader = DataLoader(train_ds, batch_size=min(batch_size, len(train_ds)), shuffle=True)

    resolved_device = _resolve_device(device)
    model = ForwardMLP(input_dim=x.shape[1], output_dim=y.shape[1]).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for features, target in train_loader:
            features = features.to(resolved_device)
            target = target.to(resolved_device)
            optimizer.zero_grad(set_to_none=True)
            prediction = model(features)
            loss = criterion(prediction, target)
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item()) * int(features.shape[0])
        if epoch == 0 or (epoch + 1) % max(1, epochs // 5) == 0 or epoch + 1 == epochs:
            avg_loss = epoch_loss / len(train_ds)
            print(f"epoch {epoch + 1:>4}/{epochs} train_mse={avg_loss:.6f}")

    model.eval()
    with torch.no_grad():
        pred_norm = model(torch.as_tensor(x_test_norm, dtype=torch.float32, device=resolved_device)).cpu().numpy()
    predictions = np.clip(pred_norm * output_std + output_mean, 0.0, 1.0)

    metrics = _compute_metrics(dataset=dataset, y_true=y_test, y_pred=predictions)
    return TorchForwardBundle(
        model=model.cpu(),
        input_mean=input_mean.astype(np.float32),
        input_std=input_std.astype(np.float32),
        output_mean=output_mean.astype(np.float32),
        output_std=output_std.astype(np.float32),
        spectrum_kind=spectrum_kind,
        wavelengths_um=np.asarray(dataset.wavelengths_um, dtype=np.float32),
        split_summary=split.summary,
        metrics=metrics,
    )


def _compute_metrics(dataset: LoadedDataset, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    error = y_true - y_pred
    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(error**2)))
    solar_mask = dataset.band_mask("solar")
    window_mask = dataset.band_mask("window")
    solar_mae = float(np.mean(np.abs(error[:, solar_mask])))
    window_mae = float(np.mean(np.abs(error[:, window_mask])))
    return {
        "mae": mae,
        "rmse": rmse,
        "solar_band_mae": solar_mae,
        "window_band_mae": window_mae,
    }


def _resolve_device(device: str) -> torch.device:
    requested = device.lower()
    if requested == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but not available.")
        return torch.device("cuda")
    return torch.device("cpu")