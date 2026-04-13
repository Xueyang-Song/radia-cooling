from __future__ import annotations

from dataclasses import dataclass

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.neighbors import KNeighborsRegressor

from rcml.data.dataset import LoadedDataset, SCALAR_TARGETS
from rcml.data.splits import make_dataset_split


@dataclass(frozen=True)
class BaselineTrainingResult:
    model: object
    metrics: dict[str, float]
    split_summary: dict[str, object]


def available_targets() -> list[str]:
    return list(SCALAR_TARGETS)


def train_scalar_baseline(
    dataset: LoadedDataset,
    model_name: str,
    target_name: str,
    test_size: float,
    random_seed: int,
    split_mode: str,
) -> BaselineTrainingResult:
    target = dataset.target_vector(target_name)
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

    model = _build_model(model_name=model_name, random_seed=random_seed)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(root_mean_squared_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }
    return BaselineTrainingResult(model=model, metrics=metrics, split_summary=split.summary)


def _build_model(model_name: str, random_seed: int):
    if model_name == "random_forest":
        return RandomForestRegressor(
            n_estimators=200,
            min_samples_leaf=2,
            random_state=random_seed,
            n_jobs=-1,
        )
    if model_name == "knn":
        return KNeighborsRegressor(n_neighbors=5, weights="distance")
    raise ValueError(f"Unsupported baseline model: {model_name}")