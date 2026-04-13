from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np


SCALAR_TARGETS = [
    "solar_reflectance",
    "window_emissivity",
    "cooling_power_proxy_w_m2",
    "total_thickness_nm",
]


@dataclass(frozen=True)
class LoadedDataset:
    manifest: dict[str, object]
    records: list[dict[str, object]]
    wavelengths_um: np.ndarray
    reflectance: np.ndarray
    emissivity: np.ndarray
    feature_matrix: np.ndarray
    feature_names: list[str]

    def target_vector(self, target_name: str) -> np.ndarray:
        if target_name not in SCALAR_TARGETS:
            raise ValueError(f"Unsupported target: {target_name}")
        values = [float(record[target_name]) for record in self.records]
        return np.asarray(values, dtype=np.float64)

    def spectrum_matrix(self, spectrum_kind: str) -> np.ndarray:
        normalized = spectrum_kind.lower()
        if normalized == "reflectance":
            return self.reflectance.astype(np.float64, copy=False)
        if normalized == "emissivity":
            return self.emissivity.astype(np.float64, copy=False)
        raise ValueError(f"Unsupported spectrum kind: {spectrum_kind}")

    def band_mask(self, band_name: str) -> np.ndarray:
        targets = self.manifest["config"]["targets"]
        if band_name == "solar":
            lower, upper = targets["solar_band_um"]
        elif band_name == "window":
            lower, upper = targets["atmospheric_window_um"]
        else:
            raise ValueError(f"Unsupported band name: {band_name}")
        mask = (self.wavelengths_um >= float(lower)) & (self.wavelengths_um <= float(upper))
        if not np.any(mask):
            raise ValueError(f"No wavelength points found for band: {band_name}")
        return mask


def load_dataset_bundle(bundle_dir: str | Path) -> LoadedDataset:
    root = Path(bundle_dir)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))

    records = [json.loads(line) for line in (root / "records.jsonl").read_text(encoding="utf-8").splitlines() if line]
    wavelengths_um = np.load(root / manifest["wavelengths_file"])
    reflectance = np.load(root / manifest["reflectance_file"])
    emissivity = np.load(root / manifest["emissivity_file"])

    dielectric_materials = list(manifest["config"]["structure"]["dielectric_materials"])
    feature_matrix, feature_names = encode_structure_features(records, dielectric_materials)

    return LoadedDataset(
        manifest=manifest,
        records=records,
        wavelengths_um=wavelengths_um,
        reflectance=reflectance,
        emissivity=emissivity,
        feature_matrix=feature_matrix,
        feature_names=feature_names,
    )


def encode_structure_features(
    records: list[dict[str, object]],
    dielectric_materials: list[str],
) -> tuple[np.ndarray, list[str]]:
    if not records:
        raise ValueError("No records found in dataset bundle.")

    material_to_index = {material: index for index, material in enumerate(dielectric_materials)}
    layer_count = len(records[0]["layer_materials"])
    feature_names: list[str] = []

    for layer_index in range(layer_count):
        for material in dielectric_materials:
            feature_names.append(f"layer_{layer_index + 1}_material_{material}")
        feature_names.append(f"layer_{layer_index + 1}_thickness_nm")
    feature_names.append("total_thickness_nm")

    rows: list[list[float]] = []
    for record in records:
        row: list[float] = []
        materials = [str(item) for item in record["layer_materials"]]
        thicknesses = [float(item) for item in record["layer_thicknesses_nm"]]
        for material, thickness in zip(materials, thicknesses, strict=True):
            if material not in material_to_index:
                raise ValueError(f"Unknown material in record: {material}")
            for candidate in dielectric_materials:
                row.append(1.0 if material == candidate else 0.0)
            row.append(thickness)
        row.append(float(record["total_thickness_nm"]))
        rows.append(row)

    return np.asarray(rows, dtype=np.float64), feature_names