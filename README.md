# radia-cooling

> A practical, evidence-driven workspace for **machine-learning-assisted radiative cooling design**.
>  
> This repo links data generation, model training, candidate proposal, physics re-verification, and research references in one reproducible workflow.

![Focus](https://img.shields.io/badge/Focus-Radiative%20Cooling-4f46e5)
![Stack](https://img.shields.io/badge/Stack-React%20%2B%20TypeScript%20%2B%20Python-0ea5e9)
![Workflow](https://img.shields.io/badge/Workflow-Forward%20%2B%20Inverse%20%2B%20Verification-16a34a)

## What this project does

The goal is to make multilayer radiative-cooling design faster and more trustworthy:

- use ML surrogates to explore a large design space efficiently
- generate inverse-design candidates toward target metrics
- verify shortlisted candidates again with physics simulation before drawing conclusions

## Repository structure

- `ml_pipeline/`: dataset generation, forward surrogates, inverse models, ranking, and verification
- `app/`: interactive interface (Story / Pipeline / Compare / Explore / Notebook / Research / Audit)
- `research/`: technical notes, model explainers, audit reports, and literature references

## Highlights

- **Evidence-first interface**: views are wired to real local artifacts, commands, and outputs.
- **Closed-loop evaluation**: generated designs are rechecked with simulation, not accepted on surrogate confidence alone.
- **Model-family comparison**: RF, XGBoost, MLP, Tandem, CVAE, and Diffusion can be evaluated within one framework.
- **Traceable research workflow**: from code and metrics to supporting papers and audit notes.

## Examples

| Home / Story | Pipeline |
|---|---|
| ![Story view](assets/readme/example-1.png) | ![Pipeline view](assets/readme/example-2.png) |

| Explorer | Research / Audit |
|---|---|
| ![Explorer view](assets/readme/example-3.png) | ![Research view](assets/readme/example-4.png) |

## Quickstart

### 1) Set up the Python pipeline

```bash
cd ml_pipeline
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[train]"
```

### 2) Install the frontend app

```bash
cd app
npm install
```

### 3) Generate content and run the app

```bash
cd ..
python app/scripts/generate_content.py
cd app && npm run dev
```

## Suggested reading path

1. Start with **Story / Pipeline** for the end-to-end logic.
2. Move to **Compare / Explore** for model behavior and candidate inspection.
3. Use **Notebook / Research / Audit** for commands, evidence files, and references.
