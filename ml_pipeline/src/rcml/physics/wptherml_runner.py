from __future__ import annotations

from importlib.util import find_spec

import numpy as np

from rcml.data.schema import DesignSpaceConfig, SimulationMetrics, SimulationOutput, StructureSample


class WPThermlBackend:
    name = "wptherml"

    def is_available(self) -> bool:
        return find_spec("wptherml") is not None

    def simulate(self, structure: StructureSample, config: DesignSpaceConfig):
        if not self.is_available():
            raise RuntimeError("WPTherml is not installed in the current environment.")
        from wptherml import TmmDriver

        wavelengths_um = config.wavelengths_um()
        wavelength_args = [float(wavelengths_um[0] * 1e-6), float(wavelengths_um[-1] * 1e-6), len(wavelengths_um)]

        material_list = ["Air", *structure.layer_materials, structure.reflector_material, "Air"]
        thickness_list_m = [
            0.0,
            *[float(value) * 1e-9 for value in structure.layer_thicknesses_nm],
            float(structure.reflector_thickness_nm) * 1e-9,
            0.0,
        ]
        args = {
            "material_list": material_list,
            "thickness_list": thickness_list_m,
            "wavelength_list": wavelength_args,
            "incident_angle": 0.0,
            "polarization": "p",
        }

        driver = TmmDriver(args)
        reflectance = np.asarray(driver.reflectivity_array, dtype=np.float64)
        emissivity = np.asarray(driver.emissivity_array, dtype=np.float64)

        solar_mask = _band_mask(wavelengths_um, *config.targets.solar_band_um)
        window_mask = _band_mask(wavelengths_um, *config.targets.atmospheric_window_um)
        solar_reflectance = float(reflectance[solar_mask].mean())
        window_emissivity = float(emissivity[window_mask].mean())
        cooling = (
            config.targets.cooling_proxy.window_gain_weight * window_emissivity
            - config.targets.cooling_proxy.solar_penalty_weight * (1.0 - solar_reflectance)
            - config.targets.cooling_proxy.thickness_penalty_weight * structure.total_thickness_nm
        )

        return SimulationOutput(
            reflectance=reflectance.astype(np.float32),
            emissivity=emissivity.astype(np.float32),
            metrics=SimulationMetrics(
                solar_reflectance=solar_reflectance,
                window_emissivity=window_emissivity,
                cooling_power_proxy_w_m2=float(cooling),
                total_thickness_nm=structure.total_thickness_nm,
            ),
        )


def _band_mask(wavelengths: np.ndarray, lower: float, upper: float) -> np.ndarray:
    mask = (wavelengths >= lower) & (wavelengths <= upper)
    if not np.any(mask):
        raise ValueError(f"No wavelength points fall inside band [{lower}, {upper}].")
    return mask