# Final Audit Report: Radiative Cooling ML / GenAI Pipeline

## Scope

This report answers the final review request for the local radiative-cooling ML project:

- confirm that the best free/publicly reproducible data path is being used
- confirm that the current dataset is clean enough for model comparison
- review whether the best freely available research directions were implemented locally
- identify and test any still-actionable mistakes
- retrain if a concrete improvement path exists
- state the final recommended workflow

All conclusions below are based on the code and artifacts in `e:\radiative_cooling\ml_pipeline` and the research notes under `e:\radiative_cooling\research`.

## Executive Verdict

The project is now in a good audited state.

1. The best free-data route available in this niche is still the one used here: an open WPTherml multilayer thin-film generator backed by public optical-constant data. There is no better standardized open benchmark dataset for radiative-cooling inverse design that would clearly supersede it.
2. The main training corpus, `data/train_wptherml_4096`, is clean by the checks run in this audit: `4096` records, `0` duplicate structures, physically valid scalar ranges, and broad target coverage.
3. The strongest implemented model workflow remains the original continuous-relaxation conditional VAE plus surrogate shortlist ranking plus final WPTherml verification.
4. One real model-design flaw was identified and tested directly: the CVAE had a soft continuous material reconstruction path but a hard `argmax` decode path. That categorical-material hypothesis was implemented, retrained, and fully verified. It did **not** beat the retained baseline.
5. The environment was also corrected during the audit: the local venv had CPU-only PyTorch even though the machine has an RTX 3080. PyTorch was upgraded to a CUDA-enabled build and CUDA training was verified.

The final recommendation is therefore conservative and evidence-based: keep the original CVAE shortlist workflow as the default, keep the categorical decoder only as an explicit experiment mode, and do not claim another performance improvement without either materially more data or a new algorithmic ingredient.

## Free Data and Literature Decision

### Why WPTherml remains the right data source

The literature and repository scan support the same conclusion reached earlier in the project:

- radiative-cooling ML papers usually train on self-generated simulation corpora rather than a common public benchmark
- Kaggle and Zenodo do not provide a mature direct benchmark for this specific inverse-design task
- open thin-film solvers such as WPTherml are widely used and are sufficiently reproducible for a benchmark-style local pipeline
- public optical constants and atmospheric references are available, so this route does not depend on closed data

This means the current dataset strategy is not a compromise caused by lack of effort. It is the strongest freely reproducible path that currently exists for this exact problem class.

### Freely available research directions reflected locally

The implemented stack already covers the main freely accessible model families that are justified at the current problem scale:

- forward surrogates for spectral prediction
- tandem inverse design
- conditional VAE generation
- conditional diffusion generation
- shortlist ranking and full-physics reranking

This aligns with the current radiative-cooling and nanophotonics inverse-design literature. GANs and RL remain interesting, but with the present dataset size they are not the first missing ingredient. The evidence in this repo says the current bottleneck is verification quality and data scale, not the absence of yet another generative family.

## Dataset Cleanliness Audit

The `data/train_wptherml_4096` bundle was re-audited directly.

Measured summary:

- number of records: `4096`
- duplicate structures: `0`
- solar reflectance range: `0.9347289583` to `0.9752305299`
- window emissivity range: `0.0025934942` to `0.7734905399`
- cooling-power-proxy range: `-28.4044635189` to `65.9214341044 W/m²`
- total thickness range: `533.12` to `2358.228 nm`

Interpretation:

- the corpus is not degenerate
- the scalar targets span both low- and high-performance regions
- there was no duplicate-structure contamination in the generated bundle
- nothing in the audit suggested broken physics outputs or invalid ranges for the core targets

This does not make the dataset perfect. It is still a simulated corpus with the limits of the chosen design space. But it is clean enough for fair local model comparison.

## Environment Audit and Fix

Before the final retraining pass, the local machine had a mismatch between hardware and environment:

- GPU present: `NVIDIA GeForce RTX 3080`
- driver version: `595.97`
- project PyTorch before fix: CPU-only build

The environment was corrected to:

- `torch 2.11.0+cu128`
- `torch.cuda.is_available() == True`
- CUDA runtime reported by PyTorch: `12.8`

This matters because any conclusion about model quality is weak if a large retraining branch is left on CPU unnecessarily. The final categorical-CVAE retrain was therefore run on CUDA rather than on the earlier CPU-only setup.

## Model Status After Audit

### Forward surrogates

These remain strong enough to justify shortlist ranking.

- reflectance forward model, holdout-thickness-tail split:
  - MAE `0.02272`
  - RMSE `0.03951`
  - solar-band MAE `0.01201`
  - window-band MAE `0.04381`
- emissivity forward model, holdout-thickness-tail split:
  - MAE `0.02359`
  - RMSE `0.03950`
  - solar-band MAE `0.01199`
  - window-band MAE `0.04307`

### Tandem inverse model

The tandem branch is a credible inverse baseline but not the top verified generator.

- solar reflectance MAE `0.00074`
- window emissivity MAE `0.01225`
- cooling-power-proxy MAE `1.29836 W/m²`
- layer thickness MAE `102.16 nm`
- total thickness MAE `134.85 nm`

### Retained baseline generator: continuous CVAE

The best generator workflow is still the original CVAE branch represented by `artifacts/train_wptherml_4096_cvae_random`.

Core training metrics:

- solar reflectance MAE `0.00239`
- window emissivity MAE `0.05109`
- cooling-power-proxy MAE `5.96858 W/m²`
- layer material accuracy `0.25215`
- layer thickness MAE `115.25 nm`

Those reconstruction metrics are not the main reason it is retained. It is retained because proposal generation plus reranking works.

Verified winners of the retained workflow:

- sample255-like target, shortlist path: `0.0946387895` total absolute error
- sample777-like target, shortlist path: `0.0711892080` total absolute error

This is the current best verified outcome in the repo.

### Diffusion baseline

The diffusion branch is real and competitive, but not the winner.

Core training metrics:

- solar reflectance MAE `0.00224`
- window emissivity MAE `0.04009`
- cooling-power-proxy MAE `5.57252 W/m²`
- layer material accuracy `0.26758`
- layer thickness MAE `126.17 nm`

Its earlier verified best-of-64 result on the reference target was about `0.1909`, essentially tied with the non-shortlisted CVAE regime and clearly behind the retained shortlist winner.

## Actionable Mistake Found and Tested

### Hypothesis

The most plausible remaining modeling issue was the CVAE material-decoder mismatch:

- training encouraged soft continuous reconstruction of material slots
- decoding converted those soft slots into hard material choices with `argmax`

This was a real technical concern, not cosmetic tuning. If correct, it could have improved structural validity and made the forward-surrogate shortlist more trustworthy.

### Intervention

The CVAE implementation was extended to support a categorical-material decoder mode with:

- per-layer material logits
- cross-entropy material loss
- normalized thickness regression
- the same target-conditioning and KL regularization path

The code now supports this as an explicit training option instead of making it the default.

### Retraining result

Artifact: `artifacts/train_wptherml_4096_cvae_categorical_random`

Training metrics from the corrected categorical branch:

- solar reflectance MAE `0.0018004808`
- window emissivity MAE `0.0686300918`
- cooling-power-proxy MAE `8.1340789795 W/m²`
- layer material accuracy `0.2621093750`
- exact combo accuracy `0.0009765625`
- layer thickness MAE `120.1592400391 nm`
- total thickness MAE `221.8058837891 nm`

The branch trained stably after fixing the thickness-loss scale. But the only metric that matters for promotion is final WPTherml verification.

## Final Verification Comparison

### Retained continuous CVAE shortlist baseline

- sample255-like target: `0.0946387895`
- sample777-like target: `0.0711892080`

### Categorical-material CVAE branch

- sample255-like target:
  - raw best-of-64: `0.4446270074`
  - shortlist `256 -> top 16`: `0.4878946035`
- sample777-like target:
  - raw best-of-64: `0.6498900493`
  - shortlist `256 -> top 16`: `0.3749434163`

### Interpretation

The categorical-material branch is decisively worse.

- on sample255 shortlist verification it is about `5.2x` worse than the retained baseline
- on sample777 shortlist verification it is about `5.3x` worse than the retained baseline
- even its best raw candidates do not recover the baseline

This means the audit did not discover a hidden easy win. It discovered a plausible modeling defect, tested it properly, and showed that fixing it in the obvious way does not beat the existing retained workflow.

That is still a useful result because it removes a false lead.

## Final Recommendation

Use the following as the project default and reported best method:

```text
continuous-decoder CVAE (kl=0.02, latent_dim=16)
        -> sample 256 candidates
        -> surrogate shortlist top 16
        -> full WPTherml verification
```

Keep these supporting decisions:

- keep CUDA enabled for all future training runs on this machine
- keep the categorical decoder only as an explicit experiment mode
- keep WPTherml verification as the final authority for generator comparison

Do not spend more time on small local tweaks to the current CVAE / shortlist family unless one of the following changes first:

1. The dataset is expanded materially beyond the current `4096`-sample regime.
2. The design space is expanded beyond the current 5-layer dielectric stack family.
3. A new algorithmic ingredient is introduced that changes the ranking or generation geometry, not just its hyperparameters.
4. Experimental feedback is added so the pipeline can optimize against fabrication reality rather than only simulated proxy objectives.

## Files of Record

Recommended result artifacts:

- retained baseline winner for sample255-like target:
  - `artifacts/train_wptherml_4096_cvae_random/verified_ranked_top16_sample255.json`
- retained baseline winner for sample777-like target:
  - `artifacts/train_wptherml_4096_cvae_random/verified_ranked_top16_sample777_raw.json`
- rejected categorical branch:
  - `artifacts/train_wptherml_4096_cvae_categorical_random/verified_proposals_sample255.json`
  - `artifacts/train_wptherml_4096_cvae_categorical_random/verified_ranked_top16_sample255.json`
  - `artifacts/train_wptherml_4096_cvae_categorical_random/verified_proposals_sample777.json`
  - `artifacts/train_wptherml_4096_cvae_categorical_random/verified_ranked_top16_sample777.json`

These files are sufficient to reproduce the final comparison stated in this report.