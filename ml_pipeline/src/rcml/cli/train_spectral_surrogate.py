from __future__ import annotations

import argparse
import json
import pickle
import shutil
from pathlib import Path

from rcml.data.dataset import load_dataset_bundle
from rcml.data.splits import available_split_modes
from rcml.models.surrogate import train_spectral_surrogate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a first spectral surrogate on a generated dataset bundle.")
    parser.add_argument("--dataset-dir", required=True, help="Path to a dataset bundle directory.")
    parser.add_argument("--output-dir", required=True, help="Directory where the model and metrics will be stored.")
    parser.add_argument("--spectrum", choices=["reflectance", "emissivity"], default="reflectance")
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--split-mode", choices=available_split_modes(), default="random")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            parser.error(f"Output directory already exists: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset_bundle(args.dataset_dir)
    result = train_spectral_surrogate(
        dataset=dataset,
        spectrum_kind=args.spectrum,
        test_size=args.test_size,
        random_seed=args.seed,
        split_mode=args.split_mode,
    )

    model_path = output_dir / "model.pkl"
    with model_path.open("wb") as handle:
        pickle.dump(result.model, handle)

    payload = {
        "spectrum": args.spectrum,
        "test_size": args.test_size,
        "split_mode": args.split_mode,
        "seed": args.seed,
        "feature_names": dataset.feature_names,
        "split_summary": result.split_summary,
        "metrics": result.metrics,
    }
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    print(f"Trained spectral surrogate for {args.spectrum}")
    for key, value in result.metrics.items():
        print(f"{key}: {value:.6f}")
    print(f"Model: {model_path}")
    print(f"Metrics: {metrics_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())