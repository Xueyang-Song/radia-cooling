from __future__ import annotations

import json
from pathlib import Path


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_excerpt(path: Path, start_line: int, end_line: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[start_line - 1 : end_line])


def _json_excerpt(path: Path, max_items: int | None = None) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list) and max_items is not None:
        payload = payload[:max_items]
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _metric(label: str, value: str, detail: str, tone: str = "cool") -> dict:
    return {"label": label, "value": value, "detail": detail, "tone": tone}


def _panel(*, panel_id: str, kind: str, title: str, language: str, source_path: str, content: str) -> dict:
    return {
        "id": panel_id,
        "kind": kind,
        "title": title,
        "language": language,
        "sourcePath": source_path,
        "content": content,
    }


def _command(label: str, command: str, note: str, source_paths: list[str]) -> dict:
    return {"label": label, "command": command, "note": note, "sourcePaths": source_paths}


def build_lab_notebook(root: Path) -> dict:
    data_dir = root / "ml_pipeline" / "data" / "train_wptherml_4096"
    artifacts_dir = root / "ml_pipeline" / "artifacts"
    config_path = root / "ml_pipeline" / "configs" / "multilayer_space.yaml"

    generate_dataset_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "generate_dataset.py"
    train_forward_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "train_torch_forward.py"
    train_tandem_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "train_tandem.py"
    train_cvae_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "train_conditional_vae.py"
    train_diffusion_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "train_conditional_diffusion.py"
    rank_candidates_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "rank_candidates.py"
    verify_candidates_path = root / "ml_pipeline" / "src" / "rcml" / "cli" / "verify_candidates.py"

    manifest_path = data_dir / "manifest.json"
    reflectance_metrics_path = artifacts_dir / "train_wptherml_4096_torch_reflectance_tail" / "metrics.json"
    emissivity_metrics_path = artifacts_dir / "train_wptherml_4096_torch_emissivity_tail" / "metrics.json"
    cvae_metrics_path = artifacts_dir / "train_wptherml_4096_cvae_random" / "metrics.json"
    diffusion_metrics_path = artifacts_dir / "train_wptherml_4096_diffusion_random" / "metrics.json"
    categorical_metrics_path = artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "metrics.json"
    verified_sample255_path = artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample255.json"
    verified_sample777_path = artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample777_raw.json"
    audit_report_path = root / "research" / "06_RCML_Final_Audit_Report.md"

    reflectance_metrics = json.loads(reflectance_metrics_path.read_text(encoding="utf-8"))
    emissivity_metrics = json.loads(emissivity_metrics_path.read_text(encoding="utf-8"))
    cvae_metrics = json.loads(cvae_metrics_path.read_text(encoding="utf-8"))
    diffusion_metrics = json.loads(diffusion_metrics_path.read_text(encoding="utf-8"))
    categorical_metrics = json.loads(categorical_metrics_path.read_text(encoding="utf-8"))
    verified_sample255 = json.loads(verified_sample255_path.read_text(encoding="utf-8"))[0]
    verified_sample777 = json.loads(verified_sample777_path.read_text(encoding="utf-8"))[0]

    return {
        "intro": "This notebook view turns the project into a concrete runbook: the actual config, the actual training entrypoints, the actual commands to reproduce the main runs, and the artifact files that decided which model survived.",
        "stages": [
            {
                "id": "design-space",
                "eyebrow": "Stage 1",
                "title": "Lock the multilayer search space",
                "summary": "Before any model training, the project fixed the structure family: 5 dielectric layers, one Ag reflector, 256 wavelength points, and explicit solar and atmospheric-window targets.",
                "meaning": "This step made every later claim reproducible. It defined exactly what a legal design is and exactly what spectra each sample must carry.",
                "metrics": [
                    _metric("Samples", "4096", "Real WPTherml records in the final training bundle."),
                    _metric("Wavelengths", "256", "Each sample stores full reflectance and emissivity spectra."),
                    _metric("Layer stack", "5 on Ag", "Dielectric multilayer above a silver reflector.", "warm"),
                ],
                "commands": [
                    _command(
                        "Rebuild the dataset bundle",
                        "python -m rcml.cli.generate_dataset --config ml_pipeline/configs/multilayer_space.yaml --output-dir ml_pipeline/data/train_wptherml_4096 --num-samples 4096 --backend wptherml --overwrite",
                        "Reproduction command for the current 4096-sample bundle.",
                        [_rel(root, config_path), _rel(root, generate_dataset_path), _rel(root, manifest_path)],
                    )
                ],
                "panels": [
                    _panel(
                        panel_id="design-config",
                        kind="code",
                        title="Design-space YAML",
                        language="yaml",
                        source_path=_rel(root, config_path),
                        content=_read_excerpt(config_path, 1, 40),
                    ),
                    _panel(
                        panel_id="dataset-cli",
                        kind="code",
                        title="Dataset generator CLI",
                        language="python",
                        source_path=_rel(root, generate_dataset_path),
                        content=_read_excerpt(generate_dataset_path, 1, 70),
                    ),
                    _panel(
                        panel_id="dataset-manifest",
                        kind="artifact",
                        title="Generated dataset manifest",
                        language="json",
                        source_path=_rel(root, manifest_path),
                        content=_json_excerpt(manifest_path),
                    ),
                ],
                "takeaways": [
                    "The design problem was bounded before training, so later results are comparable rather than hand-wavy.",
                    "The dataset is simulator-generated, but it is real project data, not a placeholder table.",
                    "Every later page depends on this exact config and dataset bundle.",
                ],
            },
            {
                "id": "forward-models",
                "eyebrow": "Stage 2",
                "title": "Train the fast forward surrogates",
                "summary": "Two differentiable PyTorch models were trained to predict spectra directly from structure: one for reflectance and one for emissivity.",
                "meaning": "These are the speed layer. They let the pipeline score many candidates before paying the cost of a full WPTherml verification run.",
                "metrics": [
                    _metric("Reflectance MAE", f"{reflectance_metrics['metrics']['mae']:.4f}", "Holdout-thickness-tail split."),
                    _metric("Emissivity MAE", f"{emissivity_metrics['metrics']['mae']:.4f}", "Holdout-thickness-tail split."),
                    _metric("Window-band MAE", f"{emissivity_metrics['metrics']['window_band_mae']:.4f}", "Critical 8-13 um band accuracy.", "warm"),
                ],
                "commands": [
                    _command(
                        "Train the reflectance surrogate",
                        "python -m rcml.cli.train_torch_forward --dataset-dir ml_pipeline/data/train_wptherml_4096 --output-dir ml_pipeline/artifacts/train_wptherml_4096_torch_reflectance_tail --spectrum reflectance --split-mode holdout_thickness_tail --epochs 120 --batch-size 128 --device cpu --overwrite",
                        "Current repo reproduction command for the reflectance bundle.",
                        [_rel(root, train_forward_path), _rel(root, reflectance_metrics_path)],
                    ),
                    _command(
                        "Train the emissivity surrogate",
                        "python -m rcml.cli.train_torch_forward --dataset-dir ml_pipeline/data/train_wptherml_4096 --output-dir ml_pipeline/artifacts/train_wptherml_4096_torch_emissivity_tail --spectrum emissivity --split-mode holdout_thickness_tail --epochs 120 --batch-size 128 --device cpu --overwrite",
                        "Current repo reproduction command for the emissivity bundle.",
                        [_rel(root, train_forward_path), _rel(root, emissivity_metrics_path)],
                    ),
                ],
                "panels": [
                    _panel(
                        panel_id="forward-cli",
                        kind="code",
                        title="Forward-surrogate CLI",
                        language="python",
                        source_path=_rel(root, train_forward_path),
                        content=_read_excerpt(train_forward_path, 1, 78),
                    ),
                    _panel(
                        panel_id="reflectance-metrics",
                        kind="artifact",
                        title="Reflectance metrics",
                        language="json",
                        source_path=_rel(root, reflectance_metrics_path),
                        content=_json_excerpt(reflectance_metrics_path),
                    ),
                    _panel(
                        panel_id="emissivity-metrics",
                        kind="artifact",
                        title="Emissivity metrics",
                        language="json",
                        source_path=_rel(root, emissivity_metrics_path),
                        content=_json_excerpt(emissivity_metrics_path),
                    ),
                ],
                "takeaways": [
                    "The forward models are not the final answer. They are the fast evaluators that make large candidate pools affordable.",
                    "The holdout-thickness-tail split matters because it stresses generalization on a harder region of the design space.",
                    "Both spectra matter because daytime radiative cooling needs high solar reflection and strong atmospheric-window emission.",
                ],
            },
            {
                "id": "generators",
                "eyebrow": "Stage 3",
                "title": "Train inverse and generative models",
                "summary": "This is where the project tests different ways to go from a target metric set back to a structure: tandem inverse design, a conditional VAE, and a conditional diffusion model.",
                "meaning": "The models differ in style. Tandem gives one direct answer. The generative models sample many plausible answers and need later ranking plus verification.",
                "metrics": [
                    _metric("CVAE feature RMSE", f"{cvae_metrics['metrics']['feature_rmse']:.2f}", "Scaled 4096-sample continuous-decoder run."),
                    _metric("Diffusion feature RMSE", f"{diffusion_metrics['metrics']['feature_rmse']:.2f}", "Competitive but not the retained winner."),
                    _metric("CVAE material accuracy", f"{cvae_metrics['metrics']['layer_material_accuracy']:.3f}", "Shows why one-shot reconstruction is not the full story.", "warm"),
                ],
                "commands": [
                    _command(
                        "Train the tandem baseline",
                        "python -m rcml.cli.train_tandem --dataset-dir ml_pipeline/data/train_wptherml_4096 --reflectance-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_reflectance_tail/model.pt --emissivity-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_emissivity_tail/model.pt --output-dir ml_pipeline/artifacts/train_wptherml_4096_tandem_tail --split-mode holdout_thickness_tail --epochs 200 --device cpu --overwrite",
                        "Reproduction command for the deterministic tandem baseline.",
                        [_rel(root, train_tandem_path), _rel(root, artifacts_dir / 'train_wptherml_4096_tandem_tail' / 'metrics.json')],
                    ),
                    _command(
                        "Train the continuous CVAE",
                        "python -m rcml.cli.train_conditional_vae --dataset-dir ml_pipeline/data/train_wptherml_4096 --reflectance-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_reflectance_tail/model.pt --emissivity-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_emissivity_tail/model.pt --output-dir ml_pipeline/artifacts/train_wptherml_4096_cvae_random --split-mode random --epochs 240 --batch-size 128 --latent-dim 16 --kl-weight 0.02 --device cpu --overwrite",
                        "Retained generator family after the full audit.",
                        [_rel(root, train_cvae_path), _rel(root, cvae_metrics_path)],
                    ),
                    _command(
                        "Train the diffusion baseline",
                        "python -m rcml.cli.train_conditional_diffusion --dataset-dir ml_pipeline/data/train_wptherml_4096 --reflectance-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_reflectance_tail/model.pt --emissivity-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_emissivity_tail/model.pt --output-dir ml_pipeline/artifacts/train_wptherml_4096_diffusion_random --split-mode random --epochs 160 --batch-size 128 --diffusion-steps 40 --device cpu --overwrite",
                        "Competitive generator that stayed close to raw CVAE sampling but did not beat the shortlist workflow.",
                        [_rel(root, train_diffusion_path), _rel(root, diffusion_metrics_path)],
                    ),
                ],
                "panels": [
                    _panel(
                        panel_id="tandem-cli",
                        kind="code",
                        title="Tandem training entrypoint",
                        language="python",
                        source_path=_rel(root, train_tandem_path),
                        content=_read_excerpt(train_tandem_path, 1, 78),
                    ),
                    _panel(
                        panel_id="cvae-cli",
                        kind="code",
                        title="Conditional VAE entrypoint",
                        language="python",
                        source_path=_rel(root, train_cvae_path),
                        content=_read_excerpt(train_cvae_path, 1, 96),
                    ),
                    _panel(
                        panel_id="diffusion-cli",
                        kind="code",
                        title="Conditional diffusion entrypoint",
                        language="python",
                        source_path=_rel(root, train_diffusion_path),
                        content=_read_excerpt(train_diffusion_path, 1, 94),
                    ),
                    _panel(
                        panel_id="cvae-metrics",
                        kind="artifact",
                        title="Continuous CVAE metrics",
                        language="json",
                        source_path=_rel(root, cvae_metrics_path),
                        content=_json_excerpt(cvae_metrics_path),
                    ),
                ],
                "takeaways": [
                    "The retained CVAE is best judged as a candidate generator, not as a one-shot inverse predictor.",
                    "Diffusion is real in this repo, but the decisive performance jump came later from ranking and verification.",
                    "The notebook keeps the actual training entrypoints visible so the pipeline is inspectable rather than magical.",
                ],
            },
            {
                "id": "shortlist-verify",
                "eyebrow": "Stage 4",
                "title": "Shortlist candidates, then re-run physics",
                "summary": "The generator did not win by itself. The best workflow sampled 256 candidates, ranked them with the forward surrogates, trimmed to the top 16, and then re-simulated those finalists with WPTherml.",
                "meaning": "This is the trust step. It is why the final winner is a verified physics result instead of a model hallucination.",
                "metrics": [
                    _metric("Sample255 winner", f"{verified_sample255['total_absolute_error']:.4f}", "Best shortlisted verified error for target A."),
                    _metric("Sample777 winner", f"{verified_sample777['total_absolute_error']:.4f}", "Best shortlisted verified error for target B."),
                    _metric("Pool trim", "256 -> 16", "Sample broadly, then verify the finalists.", "warm"),
                ],
                "commands": [
                    _command(
                        "Rank a 256-sample candidate pool",
                        "python -m rcml.cli.rank_candidates --model-path ml_pipeline/artifacts/train_wptherml_4096_cvae_random/model.pkl --targets-json '{\"solar_reflectance\":0.9599688671,\"window_emissivity\":0.6209277806,\"cooling_power_proxy_w_m2\":54.0486403880}' --dataset-dir ml_pipeline/data/train_wptherml_4096 --reflectance-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_reflectance_tail/model.pt --emissivity-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_emissivity_tail/model.pt --num-samples 256 --top-k 16 --output-path ml_pipeline/artifacts/train_wptherml_4096_cvae_random/ranked_top16_sample255.json",
                        "This is the shortlist step that changed the leaderboard.",
                        [_rel(root, rank_candidates_path), _rel(root, verified_sample255_path)],
                    ),
                    _command(
                        "Verify the shortlisted finalists with WPTherml",
                        "python -m rcml.cli.verify_candidates --proposals-path ml_pipeline/artifacts/train_wptherml_4096_cvae_random/ranked_top16_sample255.json --config ml_pipeline/configs/multilayer_space.yaml --backend wptherml --output-path ml_pipeline/artifacts/train_wptherml_4096_cvae_random/verified_ranked_top16_sample255.json",
                        "The final truth check: simulator re-run of the shortlisted proposals.",
                        [_rel(root, verify_candidates_path), _rel(root, verified_sample255_path)],
                    ),
                ],
                "panels": [
                    _panel(
                        panel_id="rank-cli",
                        kind="code",
                        title="Candidate ranking CLI",
                        language="python",
                        source_path=_rel(root, rank_candidates_path),
                        content=_read_excerpt(rank_candidates_path, 1, 90),
                    ),
                    _panel(
                        panel_id="verify-cli",
                        kind="code",
                        title="Physics verification CLI",
                        language="python",
                        source_path=_rel(root, verify_candidates_path),
                        content=_read_excerpt(verify_candidates_path, 1, 70),
                    ),
                    _panel(
                        panel_id="verify-sample255",
                        kind="artifact",
                        title="Verified shortlist results for sample255",
                        language="json",
                        source_path=_rel(root, verified_sample255_path),
                        content=_json_excerpt(verified_sample255_path, max_items=2),
                    ),
                ],
                "takeaways": [
                    "The shortlist stage is more important than just choosing CVAE versus diffusion.",
                    "The winning error of about 0.0946 came from the hybrid loop, not from raw best-of-64 generation.",
                    "The final artifact is a ranked JSON file that can be inspected line by line.",
                ],
            },
            {
                "id": "audit",
                "eyebrow": "Stage 5",
                "title": "Audit the main open hypothesis and reject the categorical branch",
                "summary": "The final audit tested a real model-design concern: the old CVAE trained materials softly but decoded them with a hard argmax. A categorical decoder branch was added, retrained, and then forced through the same verification loop.",
                "meaning": "The audit matters because it removed a plausible false lead. The newer categorical decoder did not beat the retained continuous-decoder baseline in final verified error.",
                "metrics": [
                    _metric("Categorical sample255", "0.4879", "Shortlist verified error after the audit retrain.", "warm"),
                    _metric("Categorical sample777", "0.3749", "Still far behind the retained baseline.", "warm"),
                    _metric("CUDA status", "RTX 3080", "The audit also corrected the environment to use CUDA."),
                ],
                "commands": [
                    _command(
                        "Train the categorical audit branch",
                        "python -m rcml.cli.train_conditional_vae --dataset-dir ml_pipeline/data/train_wptherml_4096 --reflectance-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_reflectance_tail/model.pt --emissivity-forward-path ml_pipeline/artifacts/train_wptherml_4096_torch_emissivity_tail/model.pt --output-dir ml_pipeline/artifacts/train_wptherml_4096_cvae_categorical_random --split-mode random --epochs 240 --batch-size 128 --latent-dim 16 --kl-weight 0.02 --decoder-mode categorical --device cuda --overwrite",
                        "The strongest audit hypothesis was tested directly rather than discussed abstractly.",
                        [_rel(root, train_cvae_path), _rel(root, categorical_metrics_path), _rel(root, audit_report_path)],
                    ),
                ],
                "panels": [
                    _panel(
                        panel_id="categorical-metrics",
                        kind="artifact",
                        title="Categorical branch metrics",
                        language="json",
                        source_path=_rel(root, categorical_metrics_path),
                        content=_json_excerpt(categorical_metrics_path),
                    ),
                    _panel(
                        panel_id="audit-report",
                        kind="artifact",
                        title="Final audit report",
                        language="markdown",
                        source_path=_rel(root, audit_report_path),
                        content=_read_excerpt(audit_report_path, 1, 180),
                    ),
                ],
                "takeaways": [
                    "The audit did not rubber-stamp the baseline. It tried to break it.",
                    "The strongest retained workflow is still the continuous-decoder CVAE plus shortlist plus WPTherml verification.",
                    "The next real jump is more data or a more different algorithmic ingredient, not another tiny tweak.",
                ],
            },
        ],
    }
