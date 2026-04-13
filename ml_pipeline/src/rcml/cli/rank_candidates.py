from __future__ import annotations

import argparse
import json
from pathlib import Path

from rcml.eval.rank import rank_generated_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sample and surrogate-rank inverse-design candidates before physics verification.")
    parser.add_argument("--model-path", required=True, help="Path to a trained inverse, CVAE, or diffusion model pickle.")
    parser.add_argument(
        "--targets-json",
        required=True,
        help="JSON string or path to a JSON file containing target metrics keyed by the model target names.",
    )
    parser.add_argument("--dataset-dir", required=True, help="Dataset bundle used to recover target definitions and band masks.")
    parser.add_argument("--reflectance-forward-path", required=True, help="Path to a trained reflectance forward bundle.")
    parser.add_argument("--emissivity-forward-path", required=True, help="Path to a trained emissivity forward bundle.")
    parser.add_argument("--num-samples", type=int, default=128, help="Number of candidates to sample from the generator.")
    parser.add_argument("--top-k", type=int, default=8, help="Number of top-ranked candidates to keep.")
    parser.add_argument(
        "--diversity-pool-size",
        type=int,
        help="Optional surrogate-ranked pool size to diversity-filter before keeping the final top-k.",
    )
    parser.add_argument(
        "--diversity-min-distance",
        type=float,
        help="Optional minimum cosine distance between shortlisted candidates in normalized feature space.",
    )
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    parser.add_argument("--seed", type=int, help="Optional seed used by stochastic generators.")
    parser.add_argument("--calibrator-path", help="Optional trained rank calibrator used to replace raw surrogate ranking scores.")
    parser.add_argument("--output-path", help="Optional JSON output path for the ranked candidate list.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    ranked_payloads = rank_generated_candidates(
        model_path=args.model_path,
        targets_json=args.targets_json,
        dataset_dir=args.dataset_dir,
        reflectance_forward_path=args.reflectance_forward_path,
        emissivity_forward_path=args.emissivity_forward_path,
        num_samples=args.num_samples,
        top_k=args.top_k,
        device=args.device,
        seed=args.seed,
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