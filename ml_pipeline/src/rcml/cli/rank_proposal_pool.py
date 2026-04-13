from __future__ import annotations

import argparse
import json
from pathlib import Path

from rcml.eval.rank import rank_existing_candidate_pool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Surrogate-rank an existing mixed proposal pool before physics verification.")
    parser.add_argument("--proposals-paths", nargs="+", required=True, help="One or more proposal JSON files to combine and rank.")
    parser.add_argument("--dataset-dir", required=True, help="Dataset bundle used to recover target definitions and band masks.")
    parser.add_argument("--reflectance-forward-path", required=True, help="Path to a trained reflectance forward bundle.")
    parser.add_argument("--emissivity-forward-path", required=True, help="Path to a trained emissivity forward bundle.")
    parser.add_argument("--top-k", type=int, default=16, help="Number of top-ranked proposals to keep.")
    parser.add_argument("--diversity-pool-size", type=int, help="Optional surrogate-ranked pool size to diversity-filter before keeping top-k.")
    parser.add_argument("--diversity-min-distance", type=float, help="Optional minimum cosine distance between shortlisted proposals.")
    parser.add_argument("--calibrator-path", help="Optional trained rank calibrator used to replace raw surrogate ranking scores.")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    parser.add_argument("--output-path", help="Optional JSON output path for the ranked candidate list.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    ranked_payloads = rank_existing_candidate_pool(
        proposals_paths=list(args.proposals_paths),
        dataset_dir=args.dataset_dir,
        reflectance_forward_path=args.reflectance_forward_path,
        emissivity_forward_path=args.emissivity_forward_path,
        top_k=args.top_k,
        device=args.device,
        diversity_pool_size=args.diversity_pool_size,
        diversity_min_distance=args.diversity_min_distance,
        calibrator_path=args.calibrator_path,
    )

    payload: dict[str, object] | list[dict[str, object]]
    payload = ranked_payloads[0] if len(ranked_payloads) == 1 else ranked_payloads
    serialized = json.dumps(payload, indent=2, ensure_ascii=True)
    if args.output_path:
        Path(args.output_path).write_text(serialized, encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())