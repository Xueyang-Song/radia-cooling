from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from time import perf_counter

from rcml.config import load_design_space
from rcml.data.schema import write_dataset_bundle
from rcml.physics import build_backend
from rcml.sampling.design_space import MultilayerSampler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a multilayer radiative-cooling dataset bundle.")
    parser.add_argument("--config", required=True, help="Path to the design-space YAML file.")
    parser.add_argument("--output-dir", required=True, help="Directory where the dataset bundle will be written.")
    parser.add_argument("--num-samples", type=int, default=128, help="Number of structures to generate.")
    parser.add_argument("--backend", choices=["mock", "wptherml"], help="Simulation backend override.")
    parser.add_argument("--seed", type=int, help="Random seed override.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the output directory if it exists.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_design_space(args.config)
    backend_name = args.backend or config.backend.default
    backend = build_backend(backend_name)

    output_dir = Path(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            parser.error(f"Output directory already exists: {output_dir}")
        shutil.rmtree(output_dir)

    if backend_name == "wptherml" and not backend.is_available():
        parser.error("The WPTherml backend was requested, but the package is not installed in this environment.")

    seed = args.seed if args.seed is not None else config.seed
    sampler = MultilayerSampler(config=config, seed=seed)

    start = perf_counter()
    structures = sampler.sample_many(args.num_samples)
    simulations = []
    progress_interval = max(1, args.num_samples // 10)

    for index, structure in enumerate(structures, start=1):
        simulations.append(backend.simulate(structure=structure, config=config))
        if index % progress_interval == 0 or index == args.num_samples:
            print(f"[{index:>5}/{args.num_samples}] simulated via {backend.name}")

    manifest_path = write_dataset_bundle(
        output_dir=output_dir,
        config=config,
        structures=structures,
        simulations=simulations,
        backend_name=backend.name,
        seed=seed,
    )
    elapsed = perf_counter() - start

    print(f"Wrote dataset bundle to {output_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"Elapsed: {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())