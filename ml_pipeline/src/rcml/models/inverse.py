from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from rcml.data.codec import (
    decode_structure_vector,
    layout_from_dataset,
    material_accuracy,
    target_matrix_from_records,
    thickness_mae_nm,
)
from rcml.data.dataset import LoadedDataset, SCALAR_TARGETS
from rcml.data.splits import make_dataset_split


DEFAULT_INVERSE_TARGETS = [
    "solar_reflectance",
    "window_emissivity",
    "cooling_power_proxy_w_m2",
]


@dataclass
class InverseModelBundle:
    input_scaler: StandardScaler
    output_scaler: StandardScaler
    regressor: MLPRegressor
    target_names: list[str]
    structure_layout: object

    def predict_feature_matrix(self, target_matrix: np.ndarray) -> np.ndarray:
        scaled_inputs = self.input_scaler.transform(target_matrix)
        scaled_outputs = self.regressor.predict(scaled_inputs)
        return self.output_scaler.inverse_transform(scaled_outputs)


@dataclass(frozen=True)
class InverseTrainingResult:
    model: InverseModelBundle
    metrics: dict[str, float]
    split_summary: dict[str, object]


def available_inverse_targets() -> list[str]:
    return list(SCALAR_TARGETS)


def default_inverse_targets() -> list[str]:
    return list(DEFAULT_INVERSE_TARGETS)


def train_inverse_mlp(
    dataset: LoadedDataset,
    target_names: list[str],
    test_size: float,
    random_seed: int,
    split_mode: str,
) -> InverseTrainingResult:
    _validate_target_names(target_names)
    split = make_dataset_split(
        dataset=dataset,
        split_mode=split_mode,
        test_size=test_size,
        random_seed=random_seed,
    )

    x = target_matrix_from_records(dataset.records, target_names)
    y = dataset.feature_matrix
    x_train = x[split.train_indices]
    x_test = x[split.test_indices]
    y_train = y[split.train_indices]
    y_test = y[split.test_indices]

    input_scaler = StandardScaler()
    output_scaler = StandardScaler()
    x_train_scaled = input_scaler.fit_transform(x_train)
    y_train_scaled = output_scaler.fit_transform(y_train)

    regressor = MLPRegressor(
        hidden_layer_sizes=(96, 96),
        activation="relu",
        solver="adam",
        early_stopping=True,
        max_iter=500,
        random_state=random_seed,
    )
    regressor.fit(x_train_scaled, y_train_scaled)

    bundle = InverseModelBundle(
        input_scaler=input_scaler,
        output_scaler=output_scaler,
        regressor=regressor,
        target_names=list(target_names),
        structure_layout=layout_from_dataset(dataset),
    )

    predicted_features = bundle.predict_feature_matrix(x_test)
    feature_rmse = float(np.sqrt(np.mean((predicted_features - y_test) ** 2)))

    true_samples = [
        decode_structure_vector(y_test[index], bundle.structure_layout, sample_id=f"true_{index:06d}")
        for index in range(y_test.shape[0])
    ]
    pred_samples = [
        decode_structure_vector(predicted_features[index], bundle.structure_layout, sample_id=f"pred_{index:06d}")
        for index in range(predicted_features.shape[0])
    ]

    layer_material_accuracy, exact_combo_accuracy = material_accuracy(true_samples, pred_samples)
    layer_thickness_mae, total_thickness_mae = thickness_mae_nm(true_samples, pred_samples)

    metrics = {
        "feature_rmse": feature_rmse,
        "layer_material_accuracy": float(layer_material_accuracy),
        "exact_combo_accuracy": float(exact_combo_accuracy),
        "layer_thickness_mae_nm": float(layer_thickness_mae),
        "total_thickness_mae_nm": float(total_thickness_mae),
    }
    return InverseTrainingResult(model=bundle, metrics=metrics, split_summary=split.summary)


def _validate_target_names(target_names: list[str]) -> None:
    if not target_names:
        raise ValueError("At least one inverse target is required.")
    invalid = [name for name in target_names if name not in SCALAR_TARGETS]
    if invalid:
        raise ValueError(f"Unsupported inverse targets: {invalid}")