from __future__ import annotations

import numpy as np

from rcml.data.schema import DesignSpaceConfig, StructureSample


class MultilayerSampler:
    def __init__(self, config: DesignSpaceConfig, seed: int | None = None) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed if seed is None else seed)

    def sample_many(self, num_samples: int) -> list[StructureSample]:
        if num_samples <= 0:
            raise ValueError("num_samples must be greater than zero.")
        return [self.sample_one(index) for index in range(num_samples)]

    def sample_one(self, index: int) -> StructureSample:
        structure = self.config.structure
        materials: list[str] = []
        previous: str | None = None
        for _ in range(structure.functional_layers):
            material = self._sample_material(previous=previous)
            materials.append(material)
            previous = material
        thicknesses = self.rng.uniform(
            structure.thickness_nm.min_nm,
            structure.thickness_nm.max_nm,
            size=structure.functional_layers,
        )
        rounded = np.round(thicknesses, 3).tolist()
        return StructureSample(
            sample_id=f"sample_{index:06d}",
            layer_materials=materials,
            layer_thicknesses_nm=rounded,
            reflector_material=structure.reflector_material,
            reflector_thickness_nm=structure.reflector_thickness_nm,
        )

    def _sample_material(self, previous: str | None) -> str:
        materials = self.config.structure.dielectric_materials
        choice = str(self.rng.choice(materials))
        if self.config.structure.allow_adjacent_duplicates or previous is None:
            return choice
        while choice == previous:
            choice = str(self.rng.choice(materials))
        return choice