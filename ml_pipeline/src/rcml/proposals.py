from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rcml.data.codec import decode_structure_vector
from rcml.data.dataset import encode_structure_features
from rcml.data.schema import StructureSample


def load_targets(raw_value: str) -> dict[str, float]:
    path = Path(raw_value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(raw_value)


def generate_feature_matrix(
    model_bundle,
    target_vector: np.ndarray,
    num_samples: int,
    device: str,
    seed: int | None,
) -> np.ndarray:
    if num_samples < 1:
        raise ValueError("num_samples must be at least 1")
    if num_samples == 1:
        prediction = predict_feature_matrix(model_bundle, target_vector, device=device)
        return np.asarray(prediction, dtype=np.float64)
    if not hasattr(model_bundle, "sample_feature_matrix"):
        raise ValueError("The selected model bundle does not support stochastic sampling. Use num_samples=1.")

    sampled = np.asarray(
        model_bundle.sample_feature_matrix(target_vector, num_samples=num_samples, device=device, seed=seed),
        dtype=np.float64,
    )
    if sampled.ndim == 3:
        if sampled.shape[1] != target_vector.shape[0]:
            raise ValueError("Sampled feature matrix batch dimension does not match the target batch size.")
        return sampled[:, 0, :]
    if sampled.ndim == 2:
        return sampled
    raise ValueError(f"Unsupported sampled feature matrix shape: {sampled.shape}")


def predict_feature_matrix(model_bundle, target_vector: np.ndarray, device: str) -> np.ndarray:
    try:
        return model_bundle.predict_feature_matrix(target_vector, device=device)
    except TypeError:
        return model_bundle.predict_feature_matrix(target_vector)


def decode_candidate_structures(feature_matrix: np.ndarray, structure_layout) -> list[StructureSample]:
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError(f"Expected a 2D feature matrix, got shape {matrix.shape}.")
    return [
        decode_structure_vector(matrix[index], structure_layout, sample_id=f"proposal_{index + 1:06d}")
        for index in range(matrix.shape[0])
    ]


def canonical_feature_matrix(structures: list[StructureSample], dielectric_materials: list[str]) -> np.ndarray:
    records = []
    for structure in structures:
        records.append(
            {
                "layer_materials": list(structure.layer_materials),
                "layer_thicknesses_nm": list(structure.layer_thicknesses_nm),
                "total_thickness_nm": float(structure.total_thickness_nm),
            }
        )
    feature_matrix, _ = encode_structure_features(records, dielectric_materials)
    return feature_matrix.astype(np.float64)


def build_proposal_payloads(
    structures: list[StructureSample],
    target_names: list[str],
    targets: dict[str, float],
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for structure in structures:
        payloads.append(
            {
                "sample_id": structure.sample_id,
                "target_names": list(target_names),
                "targets": {name: float(targets[name]) for name in target_names},
                "reflector_material": structure.reflector_material,
                "reflector_thickness_nm": float(structure.reflector_thickness_nm),
                "layer_materials": list(structure.layer_materials),
                "layer_thicknesses_nm": [float(value) for value in structure.layer_thicknesses_nm],
                "total_thickness_nm": float(structure.total_thickness_nm),
            }
        )
    return payloads