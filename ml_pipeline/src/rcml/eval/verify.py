from __future__ import annotations

import json
from pathlib import Path

from rcml.config import load_design_space
from rcml.data.schema import StructureSample
from rcml.physics import build_backend


def load_proposals(path: str | Path) -> list[dict[str, object]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    return [payload]


def structure_from_payload(payload: dict[str, object]) -> StructureSample:
    return StructureSample(
        sample_id=str(payload["sample_id"]),
        layer_materials=[str(item) for item in payload["layer_materials"]],
        layer_thicknesses_nm=[float(item) for item in payload["layer_thicknesses_nm"]],
        reflector_material=str(payload["reflector_material"]),
        reflector_thickness_nm=float(payload["reflector_thickness_nm"]),
    )


def verify_proposals(
    proposals_path: str | Path,
    config_path: str | Path,
    backend_name: str = "wptherml",
) -> list[dict[str, object]]:
    config = load_design_space(config_path)
    backend = build_backend(backend_name)
    results: list[dict[str, object]] = []
    for payload in load_proposals(proposals_path):
        structure = structure_from_payload(payload)
        simulation = backend.simulate(structure=structure, config=config)
        item = {
            "sample_id": structure.sample_id,
            "targets": payload.get("targets"),
            "simulated": {
                "solar_reflectance": simulation.metrics.solar_reflectance,
                "window_emissivity": simulation.metrics.window_emissivity,
                "cooling_power_proxy_w_m2": simulation.metrics.cooling_power_proxy_w_m2,
                "total_thickness_nm": simulation.metrics.total_thickness_nm,
            },
            "layer_materials": structure.layer_materials,
            "layer_thicknesses_nm": structure.layer_thicknesses_nm,
            "reflector_material": structure.reflector_material,
            "reflector_thickness_nm": structure.reflector_thickness_nm,
        }
        if isinstance(payload.get("targets"), dict):
            targets = payload["targets"]
            absolute_error = {
                "solar_reflectance": abs(float(targets["solar_reflectance"]) - simulation.metrics.solar_reflectance),
                "window_emissivity": abs(float(targets["window_emissivity"]) - simulation.metrics.window_emissivity),
                "cooling_power_proxy_w_m2": abs(
                    float(targets["cooling_power_proxy_w_m2"]) - simulation.metrics.cooling_power_proxy_w_m2
                ),
            }
            item["absolute_error"] = absolute_error
            item["total_absolute_error"] = float(sum(absolute_error.values()))
        results.append(item)

    results.sort(key=lambda item: float(item.get("total_absolute_error", 0.0)))
    return results