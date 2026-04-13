from __future__ import annotations

import numpy as np

from rcml.data.schema import DesignSpaceConfig, SimulationMetrics, SimulationOutput, StructureSample


MATERIAL_TRAITS: dict[str, dict[str, float]] = {
    "SiO2": {"solar_boost": 0.10, "window_boost": 0.12, "contrast": 0.14},
    "TiO2": {"solar_boost": 0.15, "window_boost": 0.08, "contrast": 0.24},
    "HfO2": {"solar_boost": 0.12, "window_boost": 0.10, "contrast": 0.20},
    "Al2O3": {"solar_boost": 0.08, "window_boost": 0.14, "contrast": 0.16},
    "Si3N4": {"solar_boost": 0.09, "window_boost": 0.11, "contrast": 0.18},
}


class MockThinFilmBackend:
    name = "mock"

    def is_available(self) -> bool:
        return True

    def simulate(self, structure: StructureSample, config: DesignSpaceConfig) -> SimulationOutput:
        wavelengths = config.wavelengths_um()
        solar_band = _band_mask(wavelengths, *config.targets.solar_band_um)
        window_band = _band_mask(wavelengths, *config.targets.atmospheric_window_um)

        total_thickness = structure.total_thickness_nm
        normalized_thickness = total_thickness / (
            config.structure.functional_layers * config.structure.thickness_nm.max_nm
        )

        phase = np.zeros_like(wavelengths)
        solar_boost = 0.0
        window_boost = 0.0
        contrast = 0.0

        for index, (material, thickness_nm) in enumerate(
            zip(structure.layer_materials, structure.layer_thicknesses_nm, strict=True)
        ):
            traits = MATERIAL_TRAITS.get(material, {"solar_boost": 0.08, "window_boost": 0.08, "contrast": 0.10})
            scale = (index + 1) / len(structure.layer_materials)
            phase += scale * thickness_nm / (160.0 * wavelengths) * (1.0 + traits["contrast"])
            solar_boost += traits["solar_boost"]
            window_boost += traits["window_boost"]
            contrast += traits["contrast"]

        solar_boost /= len(structure.layer_materials)
        window_boost /= len(structure.layer_materials)
        contrast /= len(structure.layer_materials)

        solar_envelope = np.exp(-0.5 * ((wavelengths - 0.9) / 1.2) ** 2)
        window_envelope = np.exp(-0.5 * ((wavelengths - 10.5) / 2.0) ** 2)
        longwave_envelope = np.clip((wavelengths - 2.5) / 12.0, 0.0, 1.0)

        reflectance = 0.34 + 0.28 * solar_envelope + 0.16 * np.sin(phase) + 0.10 * contrast
        reflectance += 0.12 * solar_boost * solar_envelope
        reflectance -= 0.05 * window_envelope
        reflectance += 0.06 * np.cos(phase * 0.35)
        reflectance -= 0.04 * normalized_thickness
        reflectance = np.clip(reflectance, 0.02, 0.995)

        emissivity = 0.10 + 0.62 * window_envelope + 0.08 * longwave_envelope
        emissivity += 0.08 * window_boost + 0.06 * np.cos(phase * 0.45)
        emissivity -= 0.06 * solar_envelope
        emissivity = np.clip(emissivity, 0.02, 0.995)

        solar_reflectance = float(reflectance[solar_band].mean())
        window_emissivity = float(emissivity[window_band].mean())

        cooling = (
            config.targets.cooling_proxy.window_gain_weight * window_emissivity
            - config.targets.cooling_proxy.solar_penalty_weight * (1.0 - solar_reflectance)
            - config.targets.cooling_proxy.thickness_penalty_weight * total_thickness
        )

        return SimulationOutput(
            reflectance=reflectance.astype(np.float32),
            emissivity=emissivity.astype(np.float32),
            metrics=SimulationMetrics(
                solar_reflectance=solar_reflectance,
                window_emissivity=window_emissivity,
                cooling_power_proxy_w_m2=float(cooling),
                total_thickness_nm=total_thickness,
            ),
        )


def _band_mask(wavelengths: np.ndarray, lower: float, upper: float) -> np.ndarray:
    mask = (wavelengths >= lower) & (wavelengths <= upper)
    if not np.any(mask):
        raise ValueError(f"No wavelength points fall inside band [{lower}, {upper}].")
    return mask