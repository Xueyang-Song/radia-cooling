from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import numpy as np


@dataclass(frozen=True)
class ThicknessRange:
    min_nm: float
    max_nm: float

    def validate(self) -> None:
        if self.min_nm <= 0 or self.max_nm <= 0:
            raise ValueError("Thickness bounds must be positive.")
        if self.min_nm >= self.max_nm:
            raise ValueError("Minimum thickness must be smaller than maximum thickness.")


@dataclass(frozen=True)
class StructureConfig:
    functional_layers: int
    dielectric_materials: list[str]
    reflector_material: str
    reflector_thickness_nm: float
    thickness_nm: ThicknessRange
    allow_adjacent_duplicates: bool = False

    def validate(self) -> None:
        if self.functional_layers <= 0:
            raise ValueError("functional_layers must be greater than zero.")
        if not self.dielectric_materials:
            raise ValueError("At least one dielectric material is required.")
        if self.reflector_material in self.dielectric_materials:
            raise ValueError("reflector_material must not also appear in dielectric_materials.")
        if self.reflector_thickness_nm <= 0:
            raise ValueError("reflector_thickness_nm must be positive.")
        self.thickness_nm.validate()


@dataclass(frozen=True)
class WavelengthGridConfig:
    start_um: float
    stop_um: float
    points: int

    def validate(self) -> None:
        if self.start_um <= 0 or self.stop_um <= 0:
            raise ValueError("Wavelength bounds must be positive.")
        if self.start_um >= self.stop_um:
            raise ValueError("Wavelength start must be smaller than wavelength stop.")
        if self.points < 8:
            raise ValueError("Wavelength grid must contain at least 8 points.")


@dataclass(frozen=True)
class SpectrumConfig:
    wavelength_um: WavelengthGridConfig

    def validate(self) -> None:
        self.wavelength_um.validate()


@dataclass(frozen=True)
class CoolingProxyConfig:
    solar_penalty_weight: float
    window_gain_weight: float
    thickness_penalty_weight: float


@dataclass(frozen=True)
class TargetBandsConfig:
    solar_band_um: tuple[float, float]
    atmospheric_window_um: tuple[float, float]
    cooling_proxy: CoolingProxyConfig

    def validate(self, spectrum: SpectrumConfig) -> None:
        lower, upper = self.solar_band_um
        if lower >= upper:
            raise ValueError("solar_band_um must be an increasing interval.")
        lower, upper = self.atmospheric_window_um
        if lower >= upper:
            raise ValueError("atmospheric_window_um must be an increasing interval.")
        wl = spectrum.wavelength_um
        if self.solar_band_um[0] < wl.start_um or self.atmospheric_window_um[1] > wl.stop_um:
            raise ValueError("Target bands must fit within the wavelength grid.")


@dataclass(frozen=True)
class BackendConfig:
    default: str


@dataclass(frozen=True)
class DesignSpaceConfig:
    project_name: str
    seed: int
    backend: BackendConfig
    structure: StructureConfig
    spectrum: SpectrumConfig
    targets: TargetBandsConfig

    def validate(self) -> None:
        self.structure.validate()
        self.spectrum.validate()
        self.targets.validate(self.spectrum)

    def wavelengths_um(self) -> np.ndarray:
        grid = self.spectrum.wavelength_um
        return np.linspace(grid.start_um, grid.stop_um, grid.points, dtype=np.float64)


@dataclass(frozen=True)
class StructureSample:
    sample_id: str
    layer_materials: list[str]
    layer_thicknesses_nm: list[float]
    reflector_material: str
    reflector_thickness_nm: float

    @property
    def total_thickness_nm(self) -> float:
        return float(sum(self.layer_thicknesses_nm) + self.reflector_thickness_nm)


@dataclass(frozen=True)
class SimulationMetrics:
    solar_reflectance: float
    window_emissivity: float
    cooling_power_proxy_w_m2: float
    total_thickness_nm: float


@dataclass(frozen=True)
class SimulationOutput:
    reflectance: np.ndarray
    emissivity: np.ndarray
    metrics: SimulationMetrics


def _serialize_record(structure: StructureSample, simulation: SimulationOutput) -> dict[str, object]:
    return {
        "sample_id": structure.sample_id,
        "layer_materials": structure.layer_materials,
        "layer_thicknesses_nm": structure.layer_thicknesses_nm,
        "reflector_material": structure.reflector_material,
        "reflector_thickness_nm": structure.reflector_thickness_nm,
        "solar_reflectance": simulation.metrics.solar_reflectance,
        "window_emissivity": simulation.metrics.window_emissivity,
        "cooling_power_proxy_w_m2": simulation.metrics.cooling_power_proxy_w_m2,
        "total_thickness_nm": simulation.metrics.total_thickness_nm,
    }


def write_dataset_bundle(
    output_dir: str | Path,
    config: DesignSpaceConfig,
    structures: list[StructureSample],
    simulations: list[SimulationOutput],
    backend_name: str,
    seed: int,
) -> Path:
    if len(structures) != len(simulations):
        raise ValueError("structures and simulations must have the same length.")
    if not structures:
        raise ValueError("At least one sample is required.")

    bundle_dir = Path(output_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    reflectance = np.stack([sample.reflectance for sample in simulations], axis=0)
    emissivity = np.stack([sample.emissivity for sample in simulations], axis=0)
    wavelengths = config.wavelengths_um()

    np.save(bundle_dir / "wavelengths_um.npy", wavelengths)
    np.save(bundle_dir / "reflectance.npy", reflectance)
    np.save(bundle_dir / "emissivity.npy", emissivity)

    records_path = bundle_dir / "records.jsonl"
    with records_path.open("w", encoding="utf-8") as handle:
        for structure, simulation in zip(structures, simulations, strict=True):
            handle.write(json.dumps(_serialize_record(structure, simulation), ensure_ascii=True) + "\n")

    manifest = {
        "project_name": config.project_name,
        "backend": backend_name,
        "seed": seed,
        "num_samples": len(structures),
        "wavelength_points": int(wavelengths.shape[0]),
        "records_file": "records.jsonl",
        "reflectance_file": "reflectance.npy",
        "emissivity_file": "emissivity.npy",
        "wavelengths_file": "wavelengths_um.npy",
        "config": asdict(config),
    }
    manifest_path = bundle_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    return manifest_path