from __future__ import annotations

import argparse
import json
import pickle
import random
from pathlib import Path

import numpy as np

from rcml.proposals import build_proposal_payloads, decode_candidate_structures, generate_feature_matrix, load_targets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a decoded multilayer candidate from a trained inverse model.")
    parser.add_argument("--model-path", required=True, help="Path to a trained inverse model pickle.")
    parser.add_argument(
        "--targets-json",
        required=True,
        help="JSON string or path to a JSON file containing target metrics keyed by the inverse model target names.",
    )
    parser.add_argument("--output-path", help="Optional JSON file path for the decoded candidate.")
    parser.add_argument("--num-samples", type=int, default=1, help="Number of candidate structures to generate.")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--seed", type=int, help="Optional seed used by stochastic generators.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    model_path = Path(args.model_path)
    with model_path.open("rb") as handle:
        model_bundle = pickle.load(handle)

    targets = load_targets(args.targets_json)
    missing = [name for name in model_bundle.target_names if name not in targets]
    if missing:
        parser.error(f"Missing target values for: {missing}")

    if args.num_samples < 1:
        parser.error("--num-samples must be at least 1")
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    target_vector = np.asarray([[float(targets[name]) for name in model_bundle.target_names]], dtype=np.float64)
    feature_matrix = generate_feature_matrix(
        model_bundle=model_bundle,
        target_vector=target_vector,
        num_samples=args.num_samples,
        device=args.device,
        seed=args.seed,
    )
    structures = decode_candidate_structures(feature_matrix, model_bundle.structure_layout)
    payloads = build_proposal_payloads(structures, model_bundle.target_names, targets)

    payload = payloads[0] if len(payloads) == 1 else payloads

    if args.output_path:
        Path(args.output_path).write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())