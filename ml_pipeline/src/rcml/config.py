from __future__ import annotations

from pathlib import Path

import yaml

from rcml.data.schema import (
    BackendConfig,
    CoolingProxyConfig,
    DesignSpaceConfig,
    SpectrumConfig,
    StructureConfig,
    TargetBandsConfig,
    ThicknessRange,
    WavelengthGridConfig,
)


def load_design_space(config_path: str | Path) -> DesignSpaceConfig:
    path = Path(config_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    structure_raw = raw["structure"]
    thickness_raw = structure_raw["thickness_nm"]
    spectrum_raw = raw["spectrum"]["wavelength_um"]
    target_raw = raw["targets"]
    cooling_raw = target_raw["cooling_proxy"]

    config = DesignSpaceConfig(
        project_name=raw["project_name"],
        seed=int(raw.get("seed", 0)),
        backend=BackendConfig(default=str(raw["backend"]["default"])),
        structure=StructureConfig(
            functional_layers=int(structure_raw["functional_layers"]),
            dielectric_materials=[str(item) for item in structure_raw["dielectric_materials"]],
            reflector_material=str(structure_raw["reflector_material"]),
            reflector_thickness_nm=float(structure_raw.get("reflector_thickness_nm", 150.0)),
            thickness_nm=ThicknessRange(
                min_nm=float(thickness_raw["min"]),
                max_nm=float(thickness_raw["max"]),
            ),
            allow_adjacent_duplicates=bool(structure_raw.get("allow_adjacent_duplicates", False)),
        ),
        spectrum=SpectrumConfig(
            wavelength_um=WavelengthGridConfig(
                start_um=float(spectrum_raw["start"]),
                stop_um=float(spectrum_raw["stop"]),
                points=int(spectrum_raw["points"]),
            )
        ),
        targets=TargetBandsConfig(
            solar_band_um=(float(target_raw["solar_band_um"][0]), float(target_raw["solar_band_um"][1])),
            atmospheric_window_um=(
                float(target_raw["atmospheric_window_um"][0]),
                float(target_raw["atmospheric_window_um"][1]),
            ),
            cooling_proxy=CoolingProxyConfig(
                solar_penalty_weight=float(cooling_raw["solar_penalty_weight"]),
                window_gain_weight=float(cooling_raw["window_gain_weight"]),
                thickness_penalty_weight=float(cooling_raw["thickness_penalty_weight"]),
            ),
        ),
    )
    config.validate()
    return config