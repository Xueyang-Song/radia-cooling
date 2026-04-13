from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import torch

from rcml.data.dataset import load_dataset_bundle
from rcml.eval.verify import load_proposals, structure_from_payload
from rcml.models.generative_core import conditioning_spec_from_dataset, feature_tensor_to_target_matrix
from rcml.models.rank_calibration import build_rank_calibration_features
from rcml.models.torch_forward import _resolve_device
from rcml.proposals import (
    build_proposal_payloads,
    canonical_feature_matrix,
    decode_candidate_structures,
    generate_feature_matrix,
    load_targets,
)


def rank_generated_candidates(
    model_path: str | Path,
    targets_json: str,
    dataset_dir: str | Path,
    reflectance_forward_path: str | Path,
    emissivity_forward_path: str | Path,
    num_samples: int,
    top_k: int,
    device: str,
    seed: int | None,
    diversity_pool_size: int | None = None,
    diversity_min_distance: float | None = None,
    calibrator_path: str | Path | None = None,
) -> list[dict[str, object]]:
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    with Path(model_path).open("rb") as handle:
        model_bundle = pickle.load(handle)

    targets = load_targets(targets_json)
    missing = [name for name in model_bundle.target_names if name not in targets]
    if missing:
        raise ValueError(f"Missing target values for: {missing}")

    target_vector = np.asarray([[float(targets[name]) for name in model_bundle.target_names]], dtype=np.float64)
    raw_feature_matrix = generate_feature_matrix(
        model_bundle=model_bundle,
        target_vector=target_vector,
        num_samples=num_samples,
        device=device,
        seed=seed,
    )
    structures = decode_candidate_structures(raw_feature_matrix, model_bundle.structure_layout)
    canonical_features = canonical_feature_matrix(structures, model_bundle.structure_layout.dielectric_materials)

    dataset = load_dataset_bundle(dataset_dir)
    spec = conditioning_spec_from_dataset(dataset, model_bundle.target_names)
    resolved_device = _resolve_device(device)

    reflectance_bundle = torch.load(reflectance_forward_path, weights_only=False)
    emissivity_bundle = torch.load(emissivity_forward_path, weights_only=False)
    reflectance_bundle.model = reflectance_bundle.model.to(resolved_device)
    emissivity_bundle.model = emissivity_bundle.model.to(resolved_device)

    feature_tensor = torch.as_tensor(canonical_features, dtype=torch.float32, device=resolved_device)
    with torch.no_grad():
        predicted_targets = feature_tensor_to_target_matrix(
            feature_tensor=feature_tensor,
            reflectance_bundle=reflectance_bundle,
            emissivity_bundle=emissivity_bundle,
            spec=spec,
        ).cpu().numpy()
    target_matrix = np.repeat(target_vector.astype(np.float32), canonical_features.shape[0], axis=0)
    absolute_error = np.abs(predicted_targets - target_matrix)
    total_error = absolute_error.sum(axis=1)

    payloads = build_proposal_payloads(structures, model_bundle.target_names, targets)
    for candidate_index, payload in enumerate(payloads):
        payload["surrogate_predicted"] = {
            name: float(predicted_targets[candidate_index, column_index])
            for column_index, name in enumerate(model_bundle.target_names)
        }
        payload["surrogate_absolute_error"] = {
            name: float(absolute_error[candidate_index, column_index])
            for column_index, name in enumerate(model_bundle.target_names)
        }
        payload["surrogate_total_absolute_error"] = float(total_error[candidate_index])

    score_values, score_name = _score_payloads(payloads, total_error, calibrator_path)
    ordered_indices = np.argsort(score_values)
    selected_indices = _select_candidate_indices(
        ordered_indices=ordered_indices,
        canonical_features=canonical_features,
        ranking_score=score_values,
        top_k=top_k,
        diversity_pool_size=diversity_pool_size,
        diversity_min_distance=diversity_min_distance,
    )
    ranked_payloads: list[dict[str, object]] = []
    for rank_index, candidate_index in enumerate(selected_indices, start=1):
        payload = dict(payloads[int(candidate_index)])
        payload["surrogate_rank"] = rank_index
        payload["source_sample_index"] = int(candidate_index) + 1
        payload["ranking_mode"] = _ranking_mode(diversity_pool_size, diversity_min_distance)
        payload["ranking_score_name"] = score_name
        payload["surrogate_predicted"] = {
            name: float(predicted_targets[int(candidate_index), column_index])
            for column_index, name in enumerate(model_bundle.target_names)
        }
        payload["surrogate_absolute_error"] = {
            name: float(absolute_error[int(candidate_index), column_index])
            for column_index, name in enumerate(model_bundle.target_names)
        }
        payload["surrogate_total_absolute_error"] = float(total_error[int(candidate_index)])
        if score_name != "surrogate_total_absolute_error":
            payload[score_name] = float(score_values[int(candidate_index)])
        ranked_payloads.append(payload)
    return ranked_payloads


def rank_existing_candidate_pool(
    proposals_paths: list[str | Path],
    dataset_dir: str | Path,
    reflectance_forward_path: str | Path,
    emissivity_forward_path: str | Path,
    top_k: int,
    device: str,
    diversity_pool_size: int | None = None,
    diversity_min_distance: float | None = None,
    calibrator_path: str | Path | None = None,
) -> list[dict[str, object]]:
    if not proposals_paths:
        raise ValueError("At least one proposals path is required.")

    payloads = _load_and_namespace_payloads(proposals_paths)
    if not payloads:
        raise ValueError("No proposal payloads were loaded from the provided files.")

    dataset = load_dataset_bundle(dataset_dir)
    target_names = [str(name) for name in payloads[0]["target_names"]]
    spec = conditioning_spec_from_dataset(dataset, target_names)
    canonical_features = _canonical_features_from_payloads(payloads, spec.structure_layout.dielectric_materials)
    resolved_device = _resolve_device(device)

    reflectance_bundle = torch.load(reflectance_forward_path, weights_only=False)
    emissivity_bundle = torch.load(emissivity_forward_path, weights_only=False)
    reflectance_bundle.model = reflectance_bundle.model.to(resolved_device)
    emissivity_bundle.model = emissivity_bundle.model.to(resolved_device)

    feature_tensor = torch.as_tensor(canonical_features, dtype=torch.float32, device=resolved_device)
    with torch.no_grad():
        predicted_targets = feature_tensor_to_target_matrix(
            feature_tensor=feature_tensor,
            reflectance_bundle=reflectance_bundle,
            emissivity_bundle=emissivity_bundle,
            spec=spec,
        ).cpu().numpy()

    target_vector = np.asarray([[float(payloads[0]["targets"][name]) for name in target_names]], dtype=np.float32)
    target_matrix = np.repeat(target_vector, canonical_features.shape[0], axis=0)
    absolute_error = np.abs(predicted_targets - target_matrix)
    total_error = absolute_error.sum(axis=1)

    for candidate_index, payload in enumerate(payloads):
        payload["surrogate_predicted"] = {
            name: float(predicted_targets[candidate_index, column_index])
            for column_index, name in enumerate(target_names)
        }
        payload["surrogate_absolute_error"] = {
            name: float(absolute_error[candidate_index, column_index])
            for column_index, name in enumerate(target_names)
        }
        payload["surrogate_total_absolute_error"] = float(total_error[candidate_index])

    score_values, score_name = _score_payloads(payloads, total_error, calibrator_path)
    ordered_indices = np.argsort(score_values)
    selected_indices = _select_candidate_indices(
        ordered_indices=ordered_indices,
        canonical_features=canonical_features,
        ranking_score=score_values,
        top_k=top_k,
        diversity_pool_size=diversity_pool_size,
        diversity_min_distance=diversity_min_distance,
    )

    ranked_payloads: list[dict[str, object]] = []
    for rank_index, candidate_index in enumerate(selected_indices, start=1):
        payload = dict(payloads[int(candidate_index)])
        payload["surrogate_rank"] = rank_index
        payload["ranking_mode"] = _ranking_mode(diversity_pool_size, diversity_min_distance)
        payload["ranking_score_name"] = score_name
        if score_name != "surrogate_total_absolute_error":
            payload[score_name] = float(score_values[int(candidate_index)])
        ranked_payloads.append(payload)
    return ranked_payloads


def _select_candidate_indices(
    ordered_indices: np.ndarray,
    canonical_features: np.ndarray,
    ranking_score: np.ndarray,
    top_k: int,
    diversity_pool_size: int | None,
    diversity_min_distance: float | None,
) -> np.ndarray:
    if diversity_min_distance is None:
        return ordered_indices[: min(top_k, ordered_indices.shape[0])]

    if diversity_min_distance < 0.0:
        raise ValueError("diversity_min_distance must be non-negative")

    pool_size = diversity_pool_size or max(top_k, min(ordered_indices.shape[0], top_k * 4))
    pool_indices = ordered_indices[: min(pool_size, ordered_indices.shape[0])]
    normalized_features = _normalize_features_for_distance(canonical_features)

    selected: list[int] = []
    for candidate_index in pool_indices.tolist():
        if not selected:
            selected.append(candidate_index)
            if len(selected) >= top_k:
                break
            continue

        min_distance = min(
            _cosine_distance(normalized_features[candidate_index], normalized_features[chosen_index])
            for chosen_index in selected
        )
        if min_distance >= diversity_min_distance:
            selected.append(candidate_index)
        if len(selected) >= top_k:
            break

    if len(selected) < top_k:
        for candidate_index in ordered_indices.tolist():
            if candidate_index in selected:
                continue
            selected.append(candidate_index)
            if len(selected) >= top_k:
                break

    selected_array = np.asarray(selected[:top_k], dtype=np.int64)
    selected_scores = ranking_score[selected_array]
    return selected_array[np.argsort(selected_scores)]


def _normalize_features_for_distance(feature_matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True)
    std = np.where(std < 1e-6, 1.0, std)
    normalized = (matrix - mean) / std
    norms = np.linalg.norm(normalized, axis=1, keepdims=True)
    norms = np.where(norms < 1e-6, 1.0, norms)
    return normalized / norms


def _cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    similarity = float(np.clip(np.dot(left, right), -1.0, 1.0))
    return 1.0 - similarity


def _ranking_mode(diversity_pool_size: int | None, diversity_min_distance: float | None) -> str:
    if diversity_min_distance is None:
        return "surrogate_topk"
    pool_size = diversity_pool_size if diversity_pool_size is not None else 0
    return f"surrogate_diverse_topk(pool={pool_size},min_dist={diversity_min_distance:.3f})"


def _score_payloads(
    payloads: list[dict[str, object]],
    surrogate_total_error: np.ndarray,
    calibrator_path: str | Path | None,
) -> tuple[np.ndarray, str]:
    if calibrator_path is None:
        return surrogate_total_error, "surrogate_total_absolute_error"
    with Path(calibrator_path).open("rb") as handle:
        calibrator_bundle = pickle.load(handle)
    feature_rows = []
    for payload in payloads:
        row, feature_names = build_rank_calibration_features(payload)
        if list(calibrator_bundle.feature_names) != feature_names:
            raise ValueError("Rank calibrator feature schema does not match the current payload schema.")
        feature_rows.append(row)
    feature_matrix = np.asarray(feature_rows, dtype=np.float64)
    prediction = np.asarray(calibrator_bundle.predict(feature_matrix), dtype=np.float64)
    prediction = np.clip(prediction, 0.0, None)
    return prediction, "calibrated_predicted_total_absolute_error"


def _load_and_namespace_payloads(proposals_paths: list[str | Path]) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for proposals_path in proposals_paths:
        path = Path(proposals_path)
        parent_name = path.parent.name or "pool"
        source_name = f"{parent_name}__{path.stem}"
        for index, payload in enumerate(load_proposals(proposals_path), start=1):
            item = dict(payload)
            item["source_pool"] = source_name
            item["original_sample_id"] = str(payload["sample_id"])
            item["sample_id"] = f"{source_name}_{index:06d}"
            payloads.append(item)
    return payloads


def _canonical_features_from_payloads(payloads: list[dict[str, object]], dielectric_materials: list[str]) -> np.ndarray:
    structures = [structure_from_payload(payload) for payload in payloads]
    return canonical_feature_matrix(structures, dielectric_materials)