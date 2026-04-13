from __future__ import annotations

import argparse
import json
import pickle
import shutil
from pathlib import Path

from rcml.data.dataset import load_dataset_bundle
from rcml.data.splits import available_split_modes
from rcml.models.conditional_diffusion import (
    available_diffusion_targets,
    default_diffusion_targets,
    train_conditional_diffusion,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a conditional diffusion model for inverse design candidate generation.")
    parser.add_argument("--dataset-dir", required=True, help="Path to a dataset bundle directory.")
    parser.add_argument("--reflectance-forward-path", required=True, help="Path to a trained torch forward reflectance bundle.")
    parser.add_argument("--emissivity-forward-path", required=True, help="Path to a trained torch forward emissivity bundle.")
    parser.add_argument("--output-dir", required=True, help="Directory where the diffusion model and metrics will be stored.")
    parser.add_argument("--target-features", nargs="+", choices=available_diffusion_targets(), default=default_diffusion_targets())
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--split-mode", choices=available_split_modes(), default="random")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--epochs", type=int, default=160)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--reconstruction-loss-weight", type=float, default=1.0)
    parser.add_argument("--target-loss-weight", type=float, default=1.0)
    parser.add_argument("--diffusion-steps", type=int, default=40)
    parser.add_argument("--beta-start", type=float, default=1e-4)
    parser.add_argument("--beta-end", type=float, default=0.02)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
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
    result = train_conditional_diffusion(
        dataset=dataset,
        target_names=list(args.target_features),
        reflectance_forward_path=args.reflectance_forward_path,
        emissivity_forward_path=args.emissivity_forward_path,
        test_size=args.test_size,
        random_seed=args.seed,
        split_mode=args.split_mode,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        reconstruction_loss_weight=args.reconstruction_loss_weight,
        target_loss_weight=args.target_loss_weight,
        diffusion_steps=args.diffusion_steps,
        beta_start=args.beta_start,
        beta_end=args.beta_end,
        device=args.device,
    )

    model_path = output_dir / "model.pkl"
    with model_path.open("wb") as handle:
        pickle.dump(result.model, handle)

    payload = {
        "target_features": list(args.target_features),
        "test_size": args.test_size,
        "split_mode": args.split_mode,
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "reconstruction_loss_weight": args.reconstruction_loss_weight,
        "target_loss_weight": args.target_loss_weight,
        "diffusion_steps": args.diffusion_steps,
        "beta_start": args.beta_start,
        "beta_end": args.beta_end,
        "device": args.device,
        "split_summary": result.split_summary,
        "metrics": result.metrics,
    }
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    print("Trained conditional diffusion model")
    for key, value in result.metrics.items():
        print(f"{key}: {value:.6f}")
    print(f"Model: {model_path}")
    print(f"Metrics: {metrics_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())