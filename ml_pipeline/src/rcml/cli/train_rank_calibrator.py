from __future__ import annotations

import argparse
import json
import pickle
import shutil
from pathlib import Path

from rcml.models.rank_calibration import train_rank_calibrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a shortlist rank calibrator from ranked and verified proposal files.")
    parser.add_argument("--ranked-paths", nargs="+", required=True, help="One or more ranked shortlist JSON files.")
    parser.add_argument("--verified-paths", nargs="+", required=True, help="One or more verified shortlist JSON files aligned with the ranked files.")
    parser.add_argument("--output-dir", required=True, help="Directory where the calibrator and metrics will be stored.")
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

    result = train_rank_calibrator(
        ranked_paths=list(args.ranked_paths),
        verified_paths=list(args.verified_paths),
    )

    model_path = output_dir / "model.pkl"
    with model_path.open("wb") as handle:
        pickle.dump(result.model, handle)

    payload = {
        "ranked_paths": list(args.ranked_paths),
        "verified_paths": list(args.verified_paths),
        "sample_count": result.sample_count,
        "metrics": result.metrics,
    }
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    print("Trained rank calibrator")
    print(f"sample_count: {result.sample_count}")
    for key, value in result.metrics.items():
        print(f"{key}: {value:.6f}")
    print(f"Model: {model_path}")
    print(f"Metrics: {metrics_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())