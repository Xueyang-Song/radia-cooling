from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn

from rcml.data.codec import StructureFeatureLayout, layout_from_dataset
from rcml.data.dataset import LoadedDataset


@dataclass(frozen=True)
class ConditioningSpec:
    target_names: list[str]
    solar_mask: np.ndarray
    window_mask: np.ndarray
    solar_penalty_weight: float
    window_gain_weight: float
    thickness_penalty_weight: float
    structure_layout: StructureFeatureLayout


def conditioning_spec_from_dataset(dataset: LoadedDataset, target_names: list[str]) -> ConditioningSpec:
    targets = dataset.manifest["config"]["targets"]
    cooling = targets["cooling_proxy"]
    return ConditioningSpec(
        target_names=list(target_names),
        solar_mask=dataset.band_mask("solar"),
        window_mask=dataset.band_mask("window"),
        solar_penalty_weight=float(cooling["solar_penalty_weight"]),
        window_gain_weight=float(cooling["window_gain_weight"]),
        thickness_penalty_weight=float(cooling["thickness_penalty_weight"]),
        structure_layout=layout_from_dataset(dataset),
    )


class StructuredFeatureDecoder(nn.Module):
    def __init__(self, input_dim: int, layout: StructureFeatureLayout) -> None:
        super().__init__()
        self.layout = layout
        self.material_head = nn.Linear(input_dim, layout.functional_layers * len(layout.dielectric_materials))
        self.thickness_head = nn.Linear(input_dim, layout.functional_layers)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        batch_size = hidden.shape[0]
        material_logits = self.material_head(hidden).view(
            batch_size,
            self.layout.functional_layers,
            len(self.layout.dielectric_materials),
        )
        material_probs = torch.softmax(material_logits, dim=-1)
        thickness_raw = self.thickness_head(hidden)
        thickness_range = self.layout.max_thickness_nm - self.layout.min_thickness_nm
        thickness_values = self.layout.min_thickness_nm + torch.sigmoid(thickness_raw) * thickness_range

        parts: list[torch.Tensor] = []
        for layer_index in range(self.layout.functional_layers):
            parts.append(material_probs[:, layer_index, :])
            parts.append(thickness_values[:, layer_index : layer_index + 1])

        total_thickness = thickness_values.sum(dim=1, keepdim=True) + self.layout.reflector_thickness_nm
        parts.append(total_thickness)
        return torch.cat(parts, dim=1)


def feature_tensor_to_target_matrix(
    feature_tensor: torch.Tensor,
    reflectance_bundle,
    emissivity_bundle,
    spec: ConditioningSpec,
) -> torch.Tensor:
    reflectance = reflectance_bundle.predict_tensor(feature_tensor)
    emissivity = emissivity_bundle.predict_tensor(feature_tensor)

    solar_mask = torch.as_tensor(spec.solar_mask, dtype=torch.bool, device=feature_tensor.device)
    window_mask = torch.as_tensor(spec.window_mask, dtype=torch.bool, device=feature_tensor.device)
    solar_reflectance = reflectance[:, solar_mask].mean(dim=1)
    window_emissivity = emissivity[:, window_mask].mean(dim=1)
    total_thickness = feature_tensor[:, -1]
    cooling_proxy = (
        spec.window_gain_weight * window_emissivity
        - spec.solar_penalty_weight * (1.0 - solar_reflectance)
        - spec.thickness_penalty_weight * total_thickness
    )

    available = {
        "solar_reflectance": solar_reflectance,
        "window_emissivity": window_emissivity,
        "cooling_power_proxy_w_m2": cooling_proxy,
        "total_thickness_nm": total_thickness,
    }
    return torch.stack([available[name] for name in spec.target_names], dim=1)