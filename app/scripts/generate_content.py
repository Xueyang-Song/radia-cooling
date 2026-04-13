from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import numpy as np
from localization import SUPPORTED_LOCALES, localize_research_payload, localize_site_data
from notebook_library import build_lab_notebook
from paper_library import build_paper_library


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"
OUTPUT_DIR = APP_DIR / "public" / "content"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def public_path(path: Path) -> str:
    return "/" + path.relative_to(APP_DIR / "public").as_posix()


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def round_map(data: dict[str, float], digits: int = 6) -> dict[str, float]:
    return {key: round(float(value), digits) for key, value in data.items()}


def title_from_markdown(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def summary_from_markdown(body: str) -> str:
    paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n", body) if segment.strip()]
    for paragraph in paragraphs:
        cleaned = " ".join(paragraph.split())
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if (
            paragraph.startswith("#")
            or paragraph.startswith(">")
            or paragraph.startswith("|")
            or paragraph.startswith("```")
            or re.fullmatch(r"-+", cleaned)
            or "```" in paragraph
            or cleaned.lower().startswith("table of contents")
            or cleaned.count("](#") >= 2
            or (lines and all(re.match(r"(?:\d+\.|[-*])\s+", line) for line in lines))
        ):
            continue
        if len(cleaned) > 220:
            return f"{cleaned[:217]}..."
        return cleaned
    return ""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "document"


def _language_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".md":
        return "markdown"
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "json"
    if suffix == ".toml":
        return "toml"
    return "plaintext"


def _truncate_text(content: str, *, max_lines: int = 180) -> str:
    lines = content.splitlines()
    if len(lines) <= max_lines:
        return content
    return "\n".join(lines[:max_lines] + ["", f"... truncated after {max_lines} lines from {len(lines)} total lines ..."])


def _preview_json(path: Path) -> str:
    payload = read_json(path)
    if isinstance(payload, list) and len(payload) > 8:
        payload = {
            "previewItems": payload[:8],
            "shownItems": 8,
            "totalItems": len(payload),
            "note": f"Showing the first 8 items from {path.name}.",
        }
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _preview_jsonl(path: Path) -> str:
    rows = read_jsonl(path)
    preview_rows = rows[:4]
    payload = {
        "previewRows": preview_rows,
        "shownRows": len(preview_rows),
        "totalRows": len(rows),
        "note": f"Showing the first {len(preview_rows)} parsed rows from {path.name}.",
    }
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _preview_numpy(path: Path) -> str:
    array = np.load(path, mmap_mode="r")
    flat_preview = np.asarray(array).reshape(-1)[:12]
    payload = {
        "file": path.name,
        "dtype": str(array.dtype),
        "shape": list(array.shape),
        "min": round(float(np.min(array)), 6),
        "max": round(float(np.max(array)), 6),
        "mean": round(float(np.mean(array)), 6),
        "preview": [round(float(value), 6) for value in flat_preview.tolist()],
        "note": "Binary NumPy arrays are summarized here instead of dumped raw.",
    }
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _read_evidence_content(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _preview_json(path)
    if suffix == ".jsonl":
        return _preview_jsonl(path)
    if suffix == ".npy":
        return _preview_numpy(path)
    return _truncate_text(path.read_text(encoding="utf-8"))


def _build_evidence_file(path: Path, *, title: str | None = None) -> dict:
    return {
        "id": slugify(f"{title or path.name}-{rel(path)}"),
        "title": title or path.name,
        "language": _language_for_path(path),
        "sourcePath": rel(path),
        "content": _read_evidence_content(path),
    }


def normalize_candidate(record: dict, *, label: str, family: str, route: str, note: str, source_path: Path) -> dict:
    return {
        "id": f"{family}:{label.lower().replace(' ', '-')}",
        "label": label,
        "family": family,
        "route": route,
        "note": note,
        "sourcePath": rel(source_path),
        "sampleId": record["sample_id"],
        "targets": round_map(record["targets"]),
        "simulated": round_map(record["simulated"]),
        "absoluteError": round_map(record["absolute_error"]),
        "totalAbsoluteError": round(float(record["total_absolute_error"]), 6),
        "layerMaterials": list(record["layer_materials"]),
        "layerThicknessesNm": [round(float(value), 3) for value in record["layer_thicknesses_nm"]],
        "reflectorMaterial": record["reflector_material"],
        "reflectorThicknessNm": round(float(record["reflector_thickness_nm"]), 3),
    }


def best_record(path: Path):
    payload = read_json(path)
    if isinstance(payload, list):
        return payload[0]
    return payload


def build_research_payload() -> dict:
    research_dir = ROOT / "research"
    doc_paths = [
        research_dir / "01_ML_Models_Explained.md",
        research_dir / "02_How_Paper_Uses_Each_Model.md",
        research_dir / "03_Generative_AI_Proposals.md",
        research_dir / "04_Future_Needs_vs_Existing_Advances.md",
        research_dir / "05_Datasets_and_Similar_Research.md",
        research_dir / "06_RCML_Final_Audit_Report.md",
    ]

    documents = []
    for index, path in enumerate(doc_paths, start=1):
        body = read_markdown(path)
        fallback_title = path.stem.replace("_", " ")
        title = title_from_markdown(body, fallback_title)
        summary = summary_from_markdown(body)
        documents.append(
            {
                "id": f"doc-{index:02d}",
                "title": title,
                "summary": summary,
                "body": body,
                "type": "markdown",
                "sourcePath": rel(path),
            }
        )

    papers = build_paper_library(ROOT, OUTPUT_DIR, APP_DIR / "public")

    return {
        "documents": documents,
        "papers": papers,
    }


def build_site_data(research_payload: dict) -> dict:
    data_dir = ROOT / "ml_pipeline" / "data" / "train_wptherml_4096"
    artifacts_dir = ROOT / "ml_pipeline" / "artifacts"
    lab_notebook = build_lab_notebook(ROOT)

    manifest = read_json(data_dir / "manifest.json")
    records = read_jsonl(data_dir / "records.jsonl")
    reflectance = np.load(data_dir / "reflectance.npy")
    emissivity = np.load(data_dir / "emissivity.npy")
    wavelengths = np.load(data_dir / "wavelengths_um.npy")

    cooling_values = np.array([float(record["cooling_power_proxy_w_m2"]) for record in records])
    solar_values = np.array([float(record["solar_reflectance"]) for record in records])
    window_values = np.array([float(record["window_emissivity"]) for record in records])
    thickness_values = np.array([float(record["total_thickness_nm"]) for record in records])

    cooling_sorted = np.argsort(cooling_values)
    candidate_indices = [
        ("cooling-floor", int(cooling_sorted[0]), "Cooling floor", "A real sample near the bottom of the cooling range."),
        ("median-cooling", int(cooling_sorted[len(cooling_sorted) // 2]), "Middle of the pack", "A real sample near the center of the training distribution."),
        ("cooling-peak", int(cooling_sorted[-1]), "Cooling peak", "A real sample near the best cooling proxy in the dataset."),
        ("thin-stack", int(np.argmin(thickness_values)), "Thin stack", "A real sample with unusually low total thickness."),
        ("window-peak", int(np.argmax(window_values)), "Window emitter", "A real sample with very strong 8-13 um emissivity."),
    ]

    selected_samples = []
    seen_indices: set[int] = set()
    for sample_id, index, label, note in candidate_indices:
        if index in seen_indices:
            continue
        seen_indices.add(index)
        record = records[index]
        selected_samples.append(
            {
                "id": sample_id,
                "label": label,
                "note": note,
                "sampleId": record["sample_id"],
                "targets": {
                    "solar_reflectance": round(float(record["solar_reflectance"]), 6),
                    "window_emissivity": round(float(record["window_emissivity"]), 6),
                    "cooling_power_proxy_w_m2": round(float(record["cooling_power_proxy_w_m2"]), 6),
                },
                "layerMaterials": list(record["layer_materials"]),
                "layerThicknessesNm": [round(float(value), 3) for value in record["layer_thicknesses_nm"]],
                "totalThicknessNm": round(float(record["total_thickness_nm"]), 3),
                "reflectance": [round(float(value), 6) for value in reflectance[index].tolist()],
                "emissivity": [round(float(value), 6) for value in emissivity[index].tolist()],
            }
        )

    tandem_metrics_path = artifacts_dir / "train_wptherml_4096_tandem_tail" / "metrics.json"
    cvae_metrics_path = artifacts_dir / "train_wptherml_4096_cvae_random" / "metrics.json"
    diffusion_metrics_path = artifacts_dir / "train_wptherml_4096_diffusion_random" / "metrics.json"
    categorical_metrics_path = artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "metrics.json"

    tandem_metrics = read_json(tandem_metrics_path)
    cvae_metrics = read_json(cvae_metrics_path)
    diffusion_metrics = read_json(diffusion_metrics_path)
    categorical_metrics = read_json(categorical_metrics_path)

    continuous_255_short = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample255.json"),
        label="Continuous winner / sample255",
        family="continuous-cvae",
        route="shortlist",
        note="This retained winner came from the 256-candidate shortlist loop.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample255.json",
    )
    continuous_255_raw = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_proposals_sample255.json"),
        label="Continuous raw / sample255",
        family="continuous-cvae",
        route="raw-best-of-64",
        note="Useful candidate generator, but not the final winner once shortlist verification was added.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_proposals_sample255.json",
    )
    continuous_777_short = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample777_raw.json"),
        label="Continuous winner / sample777",
        family="continuous-cvae",
        route="shortlist",
        note="Second reference target that confirmed the retained workflow was not a one-off.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample777_raw.json",
    )
    diffusion_255_raw = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_diffusion_random" / "verified_proposals_sample255.json"),
        label="Diffusion raw / sample255",
        family="diffusion",
        route="raw-best-of-64",
        note="Competitive generator, but it did not beat the retained continuous-CVAE shortlist workflow.",
        source_path=artifacts_dir / "train_wptherml_4096_diffusion_random" / "verified_proposals_sample255.json",
    )
    tandem_255 = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_tandem_tail" / "verified_proposal_sample255.json"),
        label="Tandem proposal / sample255",
        family="tandem",
        route="single-proposal",
        note="Deterministic baseline that produces one structure instead of a sampled pool.",
        source_path=artifacts_dir / "train_wptherml_4096_tandem_tail" / "verified_proposal_sample255.json",
    )
    categorical_255_raw = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_proposals_sample255.json"),
        label="Categorical raw / sample255",
        family="categorical-cvae",
        route="raw-best-of-64",
        note="Audit branch tested after the soft-to-hard material mismatch was identified.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_proposals_sample255.json",
    )
    categorical_255_short = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_ranked_top16_sample255.json"),
        label="Categorical shortlist / sample255",
        family="categorical-cvae",
        route="shortlist",
        note="The shortlist did not rescue this branch on the sample255 target.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_ranked_top16_sample255.json",
    )
    categorical_777_raw = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_proposals_sample777.json"),
        label="Categorical raw / sample777",
        family="categorical-cvae",
        route="raw-best-of-64",
        note="Raw best-of-64 sample on the second reference target.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_proposals_sample777.json",
    )
    categorical_777_short = normalize_candidate(
        best_record(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_ranked_top16_sample777.json"),
        label="Categorical shortlist / sample777",
        family="categorical-cvae",
        route="shortlist",
        note="The better of the two categorical results for the sample777 target, but still far behind the retained baseline.",
        source_path=artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_ranked_top16_sample777.json",
    )

    project = {
        "title": "Radiative Cooling, explained",
        "subtitle": "A guided web story for a real ML design project",
        "summary": "This app turns a dense radiative-cooling ML workflow into a guided walkthrough. It uses the real local research notes, real dataset outputs, and real model-verification artifacts from the project so you can see what was tried, what the data looked like, and why one workflow was retained over the others.",
        "finalVerdict": "The retained best workflow is a continuous-decoder CVAE trained on 4096 real WPTherml samples, followed by 256 candidate samples, a surrogate top-16 shortlist, and final WPTherml verification.",
        "heroStats": [
            {"label": "Real samples", "value": str(manifest["num_samples"]), "detail": "Generated from the open WPTherml thin-film simulator."},
            {"label": "Wavelength points", "value": str(manifest["wavelength_points"]), "detail": "Every real spectrum spans 0.3 to 25.0 um."},
            {"label": "Papers reviewed", "value": str(len(research_payload["papers"])), "detail": "External papers studied while building the project story and audit."},
            {"label": "Best verified error", "value": f"{continuous_777_short['totalAbsoluteError']:.4f}", "detail": "Smallest curated target error among the retained reference runs."},
        ],
        "cards": [
            {
                "id": "why",
                "title": "Why the project exists",
                "summary": "Radiative cooling research is powerful but hard to read if you are not already fluent in optics, ML, and materials science.",
                "detail": "The app is designed to unpack the whole workflow in plain language while still staying anchored to the real artifacts.",
            },
            {
                "id": "data",
                "title": "What the data really is",
                "summary": "The main dataset is not a toy spreadsheet. It is a real, reproducible WPTherml simulation corpus for 5-layer dielectric stacks over silver.",
                "detail": "Each sample includes structure details and two full spectra with 256 wavelength points.",
            },
            {
                "id": "loop",
                "title": "What the trained loop means",
                "summary": "The project did not stop at training a model. It used a multi-step loop: generate candidates, rank them, then check them again with the physics simulator.",
                "detail": "That final verification step is why the retained result is trustworthy.",
            },
            {
                "id": "result",
                "title": "How the final answer was reached",
                "summary": "Several branches were tested and compared, including diffusion, tandem, and an audited categorical CVAE branch.",
                "detail": "The continuous-CVAE shortlist workflow stayed on top after the final audit.",
            },
        ],
    }

    design_space = {
        "functionalLayers": int(manifest["config"]["structure"]["functional_layers"]),
        "materials": list(manifest["config"]["structure"]["dielectric_materials"]),
        "reflectorMaterial": manifest["config"]["structure"]["reflector_material"],
        "reflectorThicknessNm": float(manifest["config"]["structure"]["reflector_thickness_nm"]),
        "thicknessMinNm": float(manifest["config"]["structure"]["thickness_nm"]["min_nm"]),
        "thicknessMaxNm": float(manifest["config"]["structure"]["thickness_nm"]["max_nm"]),
        "wavelengthStartUm": float(manifest["config"]["spectrum"]["wavelength_um"]["start_um"]),
        "wavelengthStopUm": float(manifest["config"]["spectrum"]["wavelength_um"]["stop_um"]),
        "wavelengthPoints": int(manifest["config"]["spectrum"]["wavelength_um"]["points"]),
        "solarBand": [float(value) for value in manifest["config"]["targets"]["solar_band_um"]],
        "windowBand": [float(value) for value in manifest["config"]["targets"]["atmospheric_window_um"]],
    }

    pipeline = {
        "steps": [
            {
                "id": "design-space",
                "title": "Lock the design space",
                "why": "The project needed a clear, reproducible structure family before any model could be trained.",
                "inputs": ["5 dielectric layers", "Material pool: SiO2, TiO2, HfO2, Al2O3, Si3N4", "Thickness bounds: 40-500 nm"],
                "outputs": ["A fixed multilayer thin-film search space", "Consistent wavelength bands and target metrics"],
                "sourcePaths": [rel(ROOT / "ml_pipeline" / "configs" / "multilayer_space.yaml"), rel(data_dir / "manifest.json")],
                "evidenceFiles": [
                    _build_evidence_file(ROOT / "ml_pipeline" / "configs" / "multilayer_space.yaml", title="Design-space YAML"),
                    _build_evidence_file(data_dir / "manifest.json", title="Generated manifest"),
                ],
            },
            {
                "id": "dataset",
                "title": "Generate the real dataset",
                "why": "There is no standard public benchmark for this exact inverse-design problem, so the project had to generate a reproducible local corpus.",
                "inputs": ["Open WPTherml backend", "Randomized legal structures", "256 wavelength points per spectrum"],
                "outputs": ["4096 real records", "Reflectance spectra", "Emissivity spectra"],
                "sourcePaths": [rel(data_dir / "records.jsonl"), rel(data_dir / "reflectance.npy"), rel(data_dir / "emissivity.npy")],
                "evidenceFiles": [
                    _build_evidence_file(data_dir / "records.jsonl", title="Dataset records preview"),
                    _build_evidence_file(data_dir / "reflectance.npy", title="Reflectance array summary"),
                    _build_evidence_file(data_dir / "emissivity.npy", title="Emissivity array summary"),
                ],
            },
            {
                "id": "forward-models",
                "title": "Train forward surrogates",
                "why": "Fast forward models make it possible to score many candidate structures without calling the full simulator every time.",
                "inputs": ["Real training corpus", "Holdout thickness-tail split", "Two spectral tasks: reflectance and emissivity"],
                "outputs": ["Torch reflectance surrogate", "Torch emissivity surrogate"],
                "sourcePaths": [rel(artifacts_dir / "train_wptherml_4096_torch_reflectance_tail" / "metrics.json"), rel(artifacts_dir / "train_wptherml_4096_torch_emissivity_tail" / "metrics.json")],
                "evidenceFiles": [
                    _build_evidence_file(artifacts_dir / "train_wptherml_4096_torch_reflectance_tail" / "metrics.json", title="Reflectance surrogate metrics"),
                    _build_evidence_file(artifacts_dir / "train_wptherml_4096_torch_emissivity_tail" / "metrics.json", title="Emissivity surrogate metrics"),
                ],
            },
            {
                "id": "generators",
                "title": "Train inverse and generative models",
                "why": "Different model families answer different questions: deterministic inverse, candidate generation, or stochastic search over many valid designs.",
                "inputs": ["Tandem inverse model", "Continuous CVAE", "Conditional diffusion", "Categorical audit branch"],
                "outputs": ["Single proposals", "Candidate pools", "Metrics for apples-to-apples comparison"],
                "sourcePaths": [rel(tandem_metrics_path), rel(cvae_metrics_path), rel(diffusion_metrics_path), rel(categorical_metrics_path)],
                "evidenceFiles": [
                    _build_evidence_file(tandem_metrics_path, title="Tandem metrics"),
                    _build_evidence_file(cvae_metrics_path, title="Continuous CVAE metrics"),
                    _build_evidence_file(diffusion_metrics_path, title="Diffusion metrics"),
                    _build_evidence_file(categorical_metrics_path, title="Categorical audit metrics"),
                ],
            },
            {
                "id": "ranking",
                "title": "Rank and shortlist candidates",
                "why": "The best workflow did not trust a raw generator blindly. It scored a large pool, trimmed it, and only then spent physics budget on verification.",
                "inputs": ["256 generated candidates", "Surrogate ranking", "Top-16 shortlist"],
                "outputs": ["Compact high-value candidate set", "Much lower verification cost"],
                "sourcePaths": [rel(artifacts_dir / "train_wptherml_4096_cvae_random" / "ranked_top16_sample255.json"), rel(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "ranked_top16_sample255.json")],
                "evidenceFiles": [
                    _build_evidence_file(artifacts_dir / "train_wptherml_4096_cvae_random" / "ranked_top16_sample255.json", title="Continuous shortlist"),
                    _build_evidence_file(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "ranked_top16_sample255.json", title="Categorical shortlist"),
                ],
            },
            {
                "id": "verify",
                "title": "Re-check with WPTherml",
                "why": "This is the truth step. It is what turns an ML guess into an evidence-backed result.",
                "inputs": ["Top shortlist candidates", "Original physics simulator", "Target metrics"],
                "outputs": ["Verified absolute errors", "Final retained winner and rejected branches"],
                "sourcePaths": [rel(artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample255.json"), rel(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_ranked_top16_sample777.json")],
                "evidenceFiles": [
                    _build_evidence_file(artifacts_dir / "train_wptherml_4096_cvae_random" / "verified_ranked_top16_sample255.json", title="Continuous verified finalists"),
                    _build_evidence_file(artifacts_dir / "train_wptherml_4096_cvae_categorical_random" / "verified_ranked_top16_sample777.json", title="Categorical verified finalists"),
                ],
            },
        ]
    }

    comparison = {
        "retainedWorkflow": {
            "title": "Continuous CVAE shortlist loop",
            "summary": "Train on the 4096-sample real corpus, sample 256 candidates, shortlist the best 16 with the surrogates, then re-check those finalists with WPTherml.",
            "steps": [
                "Train on 4096 real WPTherml samples",
                "Sample 256 candidate stacks for each target",
                "Score them with the forward surrogates",
                "Re-run the top 16 through WPTherml",
            ],
        },
        "models": [
            {
                "id": "tandem",
                "name": "Tandem inverse model",
                "family": "Deterministic inverse",
                "status": "baseline",
                "summary": "Useful as a direct structure-from-target baseline. It predicts one structure per target instead of a diverse pool.",
                "splitMode": tandem_metrics["split_mode"],
                "device": tandem_metrics["device"],
                "metrics": {
                    "cooling_power_proxy_w_m2_mae": round(float(tandem_metrics["metrics"]["cooling_power_proxy_w_m2_mae"]), 6),
                    "layer_material_accuracy": round(float(tandem_metrics["metrics"]["layer_material_accuracy"]), 6),
                    "total_thickness_mae_nm": round(float(tandem_metrics["metrics"]["total_thickness_mae_nm"]), 6),
                },
                "verifiedHighlights": {"sample255": tandem_255["totalAbsoluteError"]},
            },
            {
                "id": "continuous-cvae",
                "name": "Continuous CVAE",
                "family": "Generative shortlist winner",
                "status": "retained",
                "summary": "The best generator after full verification. Its real strength comes from sampling many candidates and then letting the shortlist plus physics loop sort them.",
                "splitMode": cvae_metrics["split_mode"],
                "device": cvae_metrics["device"],
                "metrics": {
                    "cooling_power_proxy_w_m2_mae": round(float(cvae_metrics["metrics"]["cooling_power_proxy_w_m2_mae"]), 6),
                    "layer_material_accuracy": round(float(cvae_metrics["metrics"]["layer_material_accuracy"]), 6),
                    "feature_rmse": round(float(cvae_metrics["metrics"]["feature_rmse"]), 6),
                },
                "verifiedHighlights": {"sample255": continuous_255_short["totalAbsoluteError"], "sample777": continuous_777_short["totalAbsoluteError"]},
            },
            {
                "id": "diffusion",
                "name": "Conditional diffusion",
                "family": "Generative competitor",
                "status": "competitive",
                "summary": "A serious alternative generator that stayed in the same performance neighborhood as raw CVAE sampling, but never passed the retained shortlist workflow.",
                "splitMode": diffusion_metrics["split_mode"],
                "device": diffusion_metrics["device"],
                "metrics": {
                    "cooling_power_proxy_w_m2_mae": round(float(diffusion_metrics["metrics"]["cooling_power_proxy_w_m2_mae"]), 6),
                    "layer_material_accuracy": round(float(diffusion_metrics["metrics"]["layer_material_accuracy"]), 6),
                    "feature_rmse": round(float(diffusion_metrics["metrics"]["feature_rmse"]), 6),
                },
                "verifiedHighlights": {"sample255": diffusion_255_raw["totalAbsoluteError"]},
            },
            {
                "id": "categorical-cvae",
                "name": "Categorical CVAE audit branch",
                "family": "Rejected audit experiment",
                "status": "rejected",
                "summary": "Added after the audit spotted a soft-to-hard material mismatch. The branch trained cleanly but failed under final physics verification.",
                "splitMode": categorical_metrics["split_mode"],
                "device": categorical_metrics["device"],
                "metrics": {
                    "cooling_power_proxy_w_m2_mae": round(float(categorical_metrics["metrics"]["cooling_power_proxy_w_m2_mae"]), 6),
                    "layer_material_accuracy": round(float(categorical_metrics["metrics"]["layer_material_accuracy"]), 6),
                    "feature_rmse": round(float(categorical_metrics["metrics"]["feature_rmse"]), 6),
                },
                "verifiedHighlights": {"sample255": categorical_255_raw["totalAbsoluteError"], "sample777": categorical_777_short["totalAbsoluteError"]},
            },
        ],
        "targetResults": [
            {
                "id": "sample255",
                "label": "Reference target A",
                "summary": "The high-cooling sample255-like target used throughout the shortlist experiments.",
                "targetMetrics": continuous_255_short["targets"],
                "contenders": [
                    {"label": "Continuous CVAE shortlist", "value": continuous_255_short["totalAbsoluteError"], "status": "retained", "sourcePath": continuous_255_short["sourcePath"]},
                    {"label": "Continuous CVAE raw best-of-64", "value": continuous_255_raw["totalAbsoluteError"], "status": "competitive", "sourcePath": continuous_255_raw["sourcePath"]},
                    {"label": "Diffusion raw best-of-64", "value": diffusion_255_raw["totalAbsoluteError"], "status": "competitive", "sourcePath": diffusion_255_raw["sourcePath"]},
                    {"label": "Tandem single proposal", "value": tandem_255["totalAbsoluteError"], "status": "baseline", "sourcePath": tandem_255["sourcePath"]},
                    {"label": "Categorical CVAE raw best-of-64", "value": categorical_255_raw["totalAbsoluteError"], "status": "rejected", "sourcePath": categorical_255_raw["sourcePath"]},
                    {"label": "Categorical CVAE shortlist", "value": categorical_255_short["totalAbsoluteError"], "status": "rejected", "sourcePath": categorical_255_short["sourcePath"]},
                ],
            },
            {
                "id": "sample777",
                "label": "Reference target B",
                "summary": "The second curated target used to check whether the best workflow generalized beyond a single story point.",
                "targetMetrics": continuous_777_short["targets"],
                "contenders": [
                    {"label": "Continuous CVAE shortlist", "value": continuous_777_short["totalAbsoluteError"], "status": "retained", "sourcePath": continuous_777_short["sourcePath"]},
                    {"label": "Categorical CVAE shortlist", "value": categorical_777_short["totalAbsoluteError"], "status": "rejected", "sourcePath": categorical_777_short["sourcePath"]},
                    {"label": "Categorical CVAE raw best-of-64", "value": categorical_777_raw["totalAbsoluteError"], "status": "rejected", "sourcePath": categorical_777_raw["sourcePath"]},
                ],
            },
        ],
        "candidateShowcase": [continuous_255_short, continuous_777_short, categorical_255_raw, categorical_777_short],
    }

    timeline = [
        {
            "id": "dataset-built",
            "title": "A reproducible real dataset replaced hand-wavy examples",
            "summary": "The project settled on a 4096-sample WPTherml corpus so every later claim could point back to concrete structures and spectra.",
            "evidence": [rel(data_dir / "manifest.json"), rel(data_dir / "records.jsonl")],
            "evidenceFiles": [
                _build_evidence_file(data_dir / "manifest.json", title="Dataset manifest"),
                _build_evidence_file(data_dir / "records.jsonl", title="Dataset records preview"),
            ],
        },
        {
            "id": "forward-models",
            "title": "Forward surrogates made ranking practical",
            "summary": "Separate reflectance and emissivity surrogates were trained to score many candidate stacks quickly before spending full physics budget.",
            "evidence": [rel(artifacts_dir / "train_wptherml_4096_torch_reflectance_tail" / "metrics.json"), rel(artifacts_dir / "train_wptherml_4096_torch_emissivity_tail" / "metrics.json")],
            "evidenceFiles": [
                _build_evidence_file(artifacts_dir / "train_wptherml_4096_torch_reflectance_tail" / "metrics.json", title="Reflectance surrogate metrics"),
                _build_evidence_file(artifacts_dir / "train_wptherml_4096_torch_emissivity_tail" / "metrics.json", title="Emissivity surrogate metrics"),
            ],
        },
        {
            "id": "generative-branching",
            "title": "The workflow expanded from single predictions to candidate pools",
            "summary": "Tandem, continuous CVAE, and diffusion all entered the stack, but the best results came from a generator plus shortlist plus verification loop.",
            "evidence": [rel(cvae_metrics_path), rel(diffusion_metrics_path), rel(tandem_metrics_path)],
            "evidenceFiles": [
                _build_evidence_file(cvae_metrics_path, title="Continuous CVAE metrics"),
                _build_evidence_file(diffusion_metrics_path, title="Diffusion metrics"),
                _build_evidence_file(tandem_metrics_path, title="Tandem metrics"),
            ],
        },
        {
            "id": "shortlist-breakthrough",
            "title": "Shortlisting changed the leaderboard",
            "summary": "The turning point was not just a better generator. It was the 256-candidate pool plus top-16 verification strategy that cut the sample255 error to about 0.0946.",
            "evidence": [continuous_255_short["sourcePath"]],
            "evidenceFiles": [
                _build_evidence_file(ROOT / continuous_255_short["sourcePath"], title="Retained sample255 verification"),
            ],
        },
        {
            "id": "audit-and-gpu",
            "title": "The final audit checked the data, the environment, and the main open modeling concern",
            "summary": "The audit confirmed the dataset was clean, fixed the Python environment to use the RTX 3080, and tested an explicit categorical-material decoder branch.",
            "evidence": [rel(ROOT / "research" / "06_RCML_Final_Audit_Report.md"), rel(categorical_metrics_path)],
            "evidenceFiles": [
                _build_evidence_file(ROOT / "research" / "06_RCML_Final_Audit_Report.md", title="Final audit report"),
                _build_evidence_file(categorical_metrics_path, title="Categorical branch metrics"),
            ],
        },
        {
            "id": "categorical-rejected",
            "title": "The categorical decoder stayed rejected",
            "summary": "Even after retraining on CUDA, the categorical branch stayed far behind the retained continuous-CVAE shortlist workflow on both reference targets.",
            "evidence": [categorical_255_raw["sourcePath"], categorical_777_short["sourcePath"]],
            "evidenceFiles": [
                _build_evidence_file(ROOT / categorical_255_raw["sourcePath"], title="Categorical sample255 verification"),
                _build_evidence_file(ROOT / categorical_777_short["sourcePath"], title="Categorical sample777 verification"),
            ],
        },
    ]

    glossary = [
        {"term": "Radiative cooling", "explanation": "Passive cooling by reflecting sunlight and sending heat out through the atmosphere's transparent infrared window."},
        {"term": "WPTherml", "explanation": "The open thin-film simulator used to generate the real dataset and to verify the final candidates."},
        {"term": "Forward surrogate", "explanation": "A fast ML model that estimates what a structure will do without rerunning the full simulator."},
        {"term": "CVAE", "explanation": "A conditional variational autoencoder. Here it acts as a candidate generator that can sample many possible structures for one target."},
        {"term": "Shortlist", "explanation": "A ranked subset of generated candidates that gets sent to the full simulator for the final truth check."},
        {"term": "Verified error", "explanation": "The total difference between the target metrics and the simulator-confirmed metrics for a proposed structure."},
    ]

    files_of_record = [
        {"label": "Retained sample255 winner", "path": continuous_255_short["sourcePath"], "viewer": _build_evidence_file(ROOT / continuous_255_short["sourcePath"], title="Retained sample255 winner")},
        {"label": "Retained sample777 winner", "path": continuous_777_short["sourcePath"], "viewer": _build_evidence_file(ROOT / continuous_777_short["sourcePath"], title="Retained sample777 winner")},
        {"label": "Categorical sample255 raw branch", "path": categorical_255_raw["sourcePath"], "viewer": _build_evidence_file(ROOT / categorical_255_raw["sourcePath"], title="Categorical sample255 raw branch")},
        {"label": "Categorical sample777 shortlist branch", "path": categorical_777_short["sourcePath"], "viewer": _build_evidence_file(ROOT / categorical_777_short["sourcePath"], title="Categorical sample777 shortlist branch")},
        {"label": "Final audit report", "path": rel(ROOT / "research" / "06_RCML_Final_Audit_Report.md"), "viewer": _build_evidence_file(ROOT / "research" / "06_RCML_Final_Audit_Report.md", title="Final audit report")},
    ]

    return {
        "generatedAt": "2026-04-12",
        "project": project,
        "designSpace": design_space,
        "dataset": {
            "backend": manifest["backend"],
            "numSamples": int(manifest["num_samples"]),
            "seed": int(manifest["seed"]),
            "stats": {
                "solarReflectance": {"min": round(float(solar_values.min()), 6), "max": round(float(solar_values.max()), 6)},
                "windowEmissivity": {"min": round(float(window_values.min()), 6), "max": round(float(window_values.max()), 6)},
                "coolingPowerProxy": {"min": round(float(cooling_values.min()), 6), "max": round(float(cooling_values.max()), 6)},
                "totalThicknessNm": {"min": round(float(thickness_values.min()), 3), "max": round(float(thickness_values.max()), 3)},
            },
            "wavelengths": [round(float(value), 4) for value in wavelengths.tolist()],
            "selectedSamples": selected_samples,
        },
        "pipeline": pipeline,
        "comparison": comparison,
        "labNotebook": lab_notebook,
        "timeline": timeline,
        "glossary": glossary,
        "researchLibrary": {
            "docCount": len(research_payload["documents"]),
            "paperCount": len(research_payload["papers"]),
            "pdfCount": sum(1 for paper in research_payload["papers"] if paper.get("downloadedPdfPath")),
            "openAccessCount": sum(1 for paper in research_payload["papers"] if paper.get("openAccessPdfUrl")),
            "note": "Internal guides stay as local markdown. External papers are resolved from the citations we used, and only official open-access PDFs are downloaded into the app automatically.",
        },
        "filesOfRecord": files_of_record,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    research_payload = build_research_payload()
    site_data = build_site_data(research_payload)

    (OUTPUT_DIR / "research-docs.json").write_text(json.dumps(research_payload, indent=2, ensure_ascii=True), encoding="utf-8")
    (OUTPUT_DIR / "site-data.json").write_text(json.dumps(site_data, indent=2, ensure_ascii=True), encoding="utf-8")
    (OUTPUT_DIR / "research-docs.en.json").write_text(json.dumps(research_payload, indent=2, ensure_ascii=True), encoding="utf-8")
    (OUTPUT_DIR / "site-data.en.json").write_text(json.dumps(site_data, indent=2, ensure_ascii=True), encoding="utf-8")

    print(f"Wrote {OUTPUT_DIR / 'site-data.json'}")
    print(f"Wrote {OUTPUT_DIR / 'research-docs.json'}")

    for locale in SUPPORTED_LOCALES:
        if locale == "en":
            continue

        localized_research_payload = localize_research_payload(research_payload, locale, ROOT)
        localized_site_data = localize_site_data(site_data, locale)

        localized_research_path = OUTPUT_DIR / f"research-docs.{locale}.json"
        localized_site_path = OUTPUT_DIR / f"site-data.{locale}.json"

        localized_research_path.write_text(
            json.dumps(localized_research_payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        localized_site_path.write_text(
            json.dumps(localized_site_data, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

        print(f"Wrote {localized_site_path}")
        print(f"Wrote {localized_research_path}")


if __name__ == "__main__":
    main()