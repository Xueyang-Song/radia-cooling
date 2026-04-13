from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

from rcml.eval.verify import load_proposals


@dataclass
class RankCalibratorBundle:
    model: object
    feature_names: list[str]

    def predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        matrix = np.asarray(feature_matrix, dtype=np.float64)
        return np.asarray(self.model.predict(matrix), dtype=np.float64)


@dataclass(frozen=True)
class RankCalibrationTrainingResult:
    model: RankCalibratorBundle
    metrics: dict[str, float]
    sample_count: int


def train_rank_calibrator(
    ranked_paths: list[str | Path],
    verified_paths: list[str | Path],
) -> RankCalibrationTrainingResult:
    if len(ranked_paths) != len(verified_paths):
        raise ValueError("ranked_paths and verified_paths must have the same length.")
    if not ranked_paths:
        raise ValueError("At least one ranked/verified pair is required.")

    feature_rows: list[list[float]] = []
    target_values: list[float] = []
    feature_names: list[str] | None = None

    for ranked_path, verified_path in zip(ranked_paths, verified_paths, strict=True):
        ranked_payloads = load_proposals(ranked_path)
        verified_payloads = load_proposals(verified_path)
        verified_by_id = {str(item["sample_id"]): item for item in verified_payloads}
        for ranked_payload in ranked_payloads:
            sample_id = str(ranked_payload["sample_id"])
            verified_payload = verified_by_id.get(sample_id)
            if verified_payload is None:
                continue
            row, row_feature_names = build_rank_calibration_features(ranked_payload)
            if feature_names is None:
                feature_names = row_feature_names
            elif feature_names != row_feature_names:
                raise ValueError("Inconsistent rank calibration feature schema across input files.")
            feature_rows.append(row)
            target_values.append(float(verified_payload["total_absolute_error"]))

    if not feature_rows or feature_names is None:
        raise ValueError("No overlapping ranked/verified samples were found for calibration.")

    x = np.asarray(feature_rows, dtype=np.float64)
    y = np.asarray(target_values, dtype=np.float64)
    model = GradientBoostingRegressor(
        random_state=123,
        n_estimators=200,
        learning_rate=0.05,
        max_depth=2,
        min_samples_leaf=2,
    )
    model.fit(x, y)
    prediction = np.asarray(model.predict(x), dtype=np.float64)
    prediction = np.clip(prediction, 0.0, None)

    metrics = {
        "mae": float(mean_absolute_error(y, prediction)),
        "rmse": float(root_mean_squared_error(y, prediction)),
        "r2": float(r2_score(y, prediction)),
    }
    return RankCalibrationTrainingResult(
        model=RankCalibratorBundle(model=model, feature_names=feature_names),
        metrics=metrics,
        sample_count=int(x.shape[0]),
    )


def build_rank_calibration_features(payload: dict[str, object]) -> tuple[list[float], list[str]]:
    target_names = [str(name) for name in payload["target_names"]]
    targets = payload.get("targets") or {}
    surrogate_predicted = payload.get("surrogate_predicted") or {}
    surrogate_absolute_error = payload.get("surrogate_absolute_error") or {}

    row: list[float] = []
    feature_names: list[str] = []
    for name in target_names:
        feature_names.append(f"target::{name}")
        row.append(float(targets[name]))
    for name in target_names:
        feature_names.append(f"surrogate_predicted::{name}")
        row.append(float(surrogate_predicted[name]))
    for name in target_names:
        feature_names.append(f"surrogate_abs::{name}")
        row.append(float(surrogate_absolute_error[name]))
    feature_names.extend(["surrogate_total_absolute_error", "total_thickness_nm"])
    row.extend(
        [
            float(payload["surrogate_total_absolute_error"]),
            float(payload["total_thickness_nm"]),
        ]
    )
    return row, feature_names