from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from rcml.data.dataset import LoadedDataset
from rcml.data.splits import make_dataset_split


@dataclass(frozen=True)
class SpectralTrainingResult:
    model: object
    metrics: dict[str, float]
    split_summary: dict[str, object]


def train_spectral_surrogate(
    dataset: LoadedDataset,
    spectrum_kind: str,
    test_size: float,
    random_seed: int,
    split_mode: str,
) -> SpectralTrainingResult:
    target = dataset.spectrum_matrix(spectrum_kind)
    split = make_dataset_split(
        dataset=dataset,
        split_mode=split_mode,
        test_size=test_size,
        random_seed=random_seed,
    )
    x_train = dataset.feature_matrix[split.train_indices]
    x_test = dataset.feature_matrix[split.test_indices]
    y_train = target[split.train_indices]
    y_test = target[split.test_indices]

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPRegressor(
                    hidden_layer_sizes=(128, 128),
                    activation="relu",
                    solver="adam",
                    early_stopping=True,
                    max_iter=400,
                    random_state=random_seed,
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)
    predictions = np.asarray(model.predict(x_test), dtype=np.float64)

    overall_mae = float(mean_absolute_error(y_test, predictions))
    overall_rmse = float(root_mean_squared_error(y_test, predictions))

    solar_mask = dataset.band_mask("solar")
    window_mask = dataset.band_mask("window")
    solar_mae = float(mean_absolute_error(y_test[:, solar_mask], predictions[:, solar_mask]))
    window_mae = float(mean_absolute_error(y_test[:, window_mask], predictions[:, window_mask]))

    metrics = {
        "mae": overall_mae,
        "rmse": overall_rmse,
        "solar_band_mae": solar_mae,
        "window_band_mae": window_mae,
    }
    return SpectralTrainingResult(model=model, metrics=metrics, split_summary=split.summary)