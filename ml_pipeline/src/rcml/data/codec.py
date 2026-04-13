from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rcml.data.dataset import LoadedDataset
from rcml.data.schema import StructureSample


@dataclass(frozen=True)
class StructureFeatureLayout:
    dielectric_materials: list[str]
    functional_layers: int
    reflector_material: str
    reflector_thickness_nm: float
    min_thickness_nm: float
    max_thickness_nm: float

    @property
    def block_width(self) -> int:
        return len(self.dielectric_materials) + 1


def layout_from_dataset(dataset: LoadedDataset) -> StructureFeatureLayout:
    structure = dataset.manifest["config"]["structure"]
    thickness = structure["thickness_nm"]
    return StructureFeatureLayout(
        dielectric_materials=[str(item) for item in structure["dielectric_materials"]],
        functional_layers=int(structure["functional_layers"]),
        reflector_material=str(structure["reflector_material"]),
        reflector_thickness_nm=float(structure.get("reflector_thickness_nm", 150.0)),
        min_thickness_nm=float(thickness["min_nm"]),
        max_thickness_nm=float(thickness["max_nm"]),
    )


def decode_structure_vector(
    feature_vector: np.ndarray,
    layout: StructureFeatureLayout,
    sample_id: str,
) -> StructureSample:
    vector = np.asarray(feature_vector, dtype=np.float64).ravel()
    expected_size = layout.functional_layers * layout.block_width + 1
    if vector.size != expected_size:
        raise ValueError(f"Expected feature vector size {expected_size}, got {vector.size}.")

    materials: list[str] = []
    thicknesses: list[float] = []
    offset = 0
    for _ in range(layout.functional_layers):
        material_scores = vector[offset : offset + len(layout.dielectric_materials)]
        thickness_value = vector[offset + len(layout.dielectric_materials)]
        material_index = int(np.argmax(material_scores))
        materials.append(layout.dielectric_materials[material_index])
        clipped = float(np.clip(thickness_value, layout.min_thickness_nm, layout.max_thickness_nm))
        thicknesses.append(round(clipped, 3))
        offset += layout.block_width

    return StructureSample(
        sample_id=sample_id,
        layer_materials=materials,
        layer_thicknesses_nm=thicknesses,
        reflector_material=layout.reflector_material,
        reflector_thickness_nm=layout.reflector_thickness_nm,
    )


def target_matrix_from_records(records: list[dict[str, object]], target_names: list[str]) -> np.ndarray:
    rows = []
    for record in records:
        rows.append([float(record[name]) for name in target_names])
    return np.asarray(rows, dtype=np.float64)


def material_accuracy(true_samples: list[StructureSample], pred_samples: list[StructureSample]) -> tuple[float, float]:
    if len(true_samples) != len(pred_samples):
        raise ValueError("true_samples and pred_samples must have the same length.")
    total_layers = 0
    matched_layers = 0
    exact_matches = 0
    for true_sample, pred_sample in zip(true_samples, pred_samples, strict=True):
        pairs = zip(true_sample.layer_materials, pred_sample.layer_materials, strict=True)
        layer_matches = [int(true_name == pred_name) for true_name, pred_name in pairs]
        total_layers += len(layer_matches)
        matched_layers += sum(layer_matches)
        exact_matches += int(all(layer_matches))
    return matched_layers / total_layers, exact_matches / len(true_samples)


def thickness_mae_nm(true_samples: list[StructureSample], pred_samples: list[StructureSample]) -> tuple[float, float]:
    if len(true_samples) != len(pred_samples):
        raise ValueError("true_samples and pred_samples must have the same length.")
    layer_errors: list[float] = []
    total_errors: list[float] = []
    for true_sample, pred_sample in zip(true_samples, pred_samples, strict=True):
        for true_value, pred_value in zip(true_sample.layer_thicknesses_nm, pred_sample.layer_thicknesses_nm, strict=True):
            layer_errors.append(abs(float(true_value) - float(pred_value)))
        total_errors.append(abs(true_sample.total_thickness_nm - pred_sample.total_thickness_nm))
    return float(np.mean(layer_errors)), float(np.mean(total_errors))