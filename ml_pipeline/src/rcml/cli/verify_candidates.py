from __future__ import annotations

import argparse
import json
from pathlib import Path

from rcml.eval.verify import verify_proposals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Re-simulate saved candidate proposals and rank them by target error.")
    parser.add_argument("--proposals-path", required=True, help="Path to a JSON file containing one proposal object or a list of proposals.")
    parser.add_argument("--config", default="ml_pipeline/configs/multilayer_space.yaml", help="Path to the design-space config used for re-simulation.")
    parser.add_argument("--backend", choices=["wptherml", "mock"], default="wptherml")
    parser.add_argument("--output-path", help="Optional output JSON path for the ranked verification results.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    results = verify_proposals(
        proposals_path=args.proposals_path,
        config_path=args.config,
        backend_name=args.backend,
    )
    payload = json.dumps(results, indent=2, ensure_ascii=True)
    if args.output_path:
        Path(args.output_path).write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())