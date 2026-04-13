# RCML Pipeline

Initial Python scaffold for a multilayer radiative-cooling ML workflow.

Current scope:

- Config-driven multilayer design space
- Synthetic dataset bundle writer
- Mock backend for smoke testing the data pipeline
- WPTherml backend hook for later real TMM integration

## Backends

- `mock`: fast synthetic spectra for pipeline validation
- `wptherml`: real multilayer transfer-matrix spectra via `wptherml.TmmDriver`

## Quickstart

Create a virtual environment, install the package, then run a smoke-test dataset build.

```powershell
cd E:\radiative_cooling\ml_pipeline
python -m pip install -e .
python scripts\generate_dataset.py --config configs\multilayer_space.yaml --output-dir data\smoke_mock --num-samples 16 --backend mock --overwrite
```

For the real TMM backend, install the simulator into the same environment and run:

```powershell
python -m pip install wptherml matplotlib
python scripts\generate_dataset.py --config configs\multilayer_space.yaml --output-dir data\smoke_wptherml --num-samples 4 --backend wptherml --overwrite
```

The generated bundle contains:

- `manifest.json`
- `records.jsonl`
- `wavelengths_um.npy`
- `reflectance.npy`
- `emissivity.npy`

You can train the first scalar and spectral baselines with:

```powershell
python scripts\train_baseline.py --dataset-dir data\smoke_mock --output-dir artifacts\rf_scalar --model random_forest --target cooling_power_proxy_w_m2 --overwrite
python scripts\train_spectral_surrogate.py --dataset-dir data\smoke_mock --output-dir artifacts\mlp_reflectance --spectrum reflectance --overwrite
```

For more realistic evaluation, both trainers support held-out split modes:

```powershell
python scripts\train_baseline.py --dataset-dir data\smoke_mock --output-dir artifacts\rf_holdout_combo --model random_forest --target cooling_power_proxy_w_m2 --split-mode holdout_combo --overwrite
python scripts\train_spectral_surrogate.py --dataset-dir data\smoke_mock --output-dir artifacts\mlp_holdout_thickness --spectrum reflectance --split-mode holdout_thickness_tail --overwrite
```

The first inverse-design scaffold is also available:

```powershell
python scripts\train_inverse_design.py --dataset-dir data\smoke_mock --output-dir artifacts\inverse_mlp --split-mode holdout_combo --overwrite
```

This inverse trainer maps target scalar metrics back to multilayer feature vectors, decodes them into candidate stacks, and reports material-match and thickness-reconstruction quality on the held-out split.

To propose a candidate from a trained inverse model:

```powershell
python -m rcml.cli.propose_inverse_design --model-path artifacts\inverse_mlp\model.pkl --targets-json "{\"solar_reflectance\": 0.9, \"window_emissivity\": 0.9, \"cooling_power_proxy_w_m2\": 70.0}"
```

The next-stage differentiable forward surrogate can be trained with:

```powershell
python -m rcml.cli.train_torch_forward --dataset-dir data\train_wptherml_256 --output-dir artifacts\torch_forward_emissivity --spectrum emissivity --split-mode holdout_thickness_tail --epochs 200 --device cpu --overwrite
```

This produces a PyTorch model bundle that uses the same dataset and split surfaces as the sklearn spectral surrogate, but is suitable for later tandem training.

The tandem inverse model can then be trained against frozen reflectance and emissivity forward bundles:

```powershell
python -m rcml.cli.train_torch_forward --dataset-dir data\train_wptherml_256 --output-dir artifacts\torch_forward_reflectance --spectrum reflectance --split-mode holdout_thickness_tail --epochs 120 --device cpu --overwrite
python -m rcml.cli.train_tandem --dataset-dir data\train_wptherml_256 --reflectance-forward-path artifacts\torch_forward_reflectance\model.pt --emissivity-forward-path artifacts\torch_forward_emissivity\model.pt --output-dir artifacts\tandem --split-mode random --epochs 150 --device cpu --overwrite
```

The first true generative model is a conditional VAE that samples multiple candidate structures for the same target request:

```powershell
python -m rcml.cli.train_conditional_vae --dataset-dir data\train_wptherml_256 --reflectance-forward-path artifacts\torch_forward_reflectance\model.pt --emissivity-forward-path artifacts\torch_forward_emissivity\model.pt --output-dir artifacts\cvae --split-mode random --epochs 200 --device cpu --overwrite
python -m rcml.cli.propose_inverse_design --model-path artifacts\cvae\model.pkl --targets-json '{"solar_reflectance":0.92,"window_emissivity":0.88,"cooling_power_proxy_w_m2":110.0}' --num-samples 32 --output-path artifacts\cvae_proposals.json
```

There is now also a conditional diffusion baseline that uses the same proposal interface:

```powershell
python -m rcml.cli.train_conditional_diffusion --dataset-dir data\train_wptherml_4096 --reflectance-forward-path artifacts\train_wptherml_4096_torch_reflectance_tail\model.pt --emissivity-forward-path artifacts\train_wptherml_4096_torch_emissivity_tail\model.pt --output-dir artifacts\train_wptherml_4096_diffusion_random --split-mode random --epochs 160 --batch-size 128 --diffusion-steps 40 --device cpu --overwrite
python -m rcml.cli.propose_inverse_design --model-path artifacts\train_wptherml_4096_diffusion_random\model.pkl --targets-json '{"solar_reflectance":0.9599688671198857,"window_emissivity":0.6209277806338159,"cooling_power_proxy_w_m2":54.04864038804648}' --num-samples 64 --seed 123 --output-path artifacts\train_wptherml_4096_diffusion_random\proposals_sample255.json
```

To avoid sending every sampled candidate to full physics, there is also a surrogate shortlist step that ranks decoded candidates with the frozen forward surrogates before WPTherml verification:

```powershell
python -m rcml.cli.rank_candidates --model-path artifacts\train_wptherml_4096_cvae_random\model.pkl --targets-json '{"solar_reflectance":0.9599688671198857,"window_emissivity":0.6209277806338159,"cooling_power_proxy_w_m2":54.04864038804648}' --dataset-dir data\train_wptherml_4096 --reflectance-forward-path artifacts\train_wptherml_4096_torch_reflectance_tail\model.pt --emissivity-forward-path artifacts\train_wptherml_4096_torch_emissivity_tail\model.pt --num-samples 256 --top-k 16 --seed 123 --output-path artifacts\train_wptherml_4096_cvae_random\ranked_top16_sample255.json
python -m rcml.cli.verify_candidates --proposals-path artifacts\train_wptherml_4096_cvae_random\ranked_top16_sample255.json --config configs\multilayer_space.yaml --output-path artifacts\train_wptherml_4096_cvae_random\verified_ranked_top16_sample255.json
```

Any saved proposals can be re-simulated and ranked with:

```powershell
python -m rcml.cli.verify_candidates --proposals-path artifacts\some_proposals.json --config ml_pipeline\configs\multilayer_space.yaml --output-path artifacts\verified_proposals.json
```

For a larger real-data run, the current reproducible scaling recipe is:

```powershell
python -m rcml.cli.generate_dataset --config configs\multilayer_space.yaml --output-dir data\train_wptherml_4096 --num-samples 4096 --backend wptherml --overwrite
python -m rcml.cli.train_torch_forward --dataset-dir data\train_wptherml_4096 --output-dir artifacts\train_wptherml_4096_torch_reflectance_tail --spectrum reflectance --split-mode holdout_thickness_tail --epochs 120 --batch-size 128 --device cpu --overwrite
python -m rcml.cli.train_torch_forward --dataset-dir data\train_wptherml_4096 --output-dir artifacts\train_wptherml_4096_torch_emissivity_tail --spectrum emissivity --split-mode holdout_thickness_tail --epochs 120 --batch-size 128 --device cpu --overwrite
python -m rcml.cli.train_tandem --dataset-dir data\train_wptherml_4096 --reflectance-forward-path artifacts\train_wptherml_4096_torch_reflectance_tail\model.pt --emissivity-forward-path artifacts\train_wptherml_4096_torch_emissivity_tail\model.pt --output-dir artifacts\train_wptherml_4096_tandem_tail --split-mode holdout_thickness_tail --epochs 200 --batch-size 128 --device cpu --overwrite
python -m rcml.cli.train_conditional_vae --dataset-dir data\train_wptherml_4096 --reflectance-forward-path artifacts\train_wptherml_4096_torch_reflectance_tail\model.pt --emissivity-forward-path artifacts\train_wptherml_4096_torch_emissivity_tail\model.pt --output-dir artifacts\train_wptherml_4096_cvae_random --split-mode random --epochs 240 --batch-size 128 --device cpu --overwrite
```

On GPU-equipped machines, switch `--device` from `cpu` to `cuda`. The final audit reruns used a CUDA-enabled PyTorch build (`2.11.0+cu128`) on an RTX 3080. The CVAE trainer also now supports `--decoder-mode categorical` for the audited categorical-material branch, but that mode is experimental rather than the retained default.

On that 4096-sample corpus, the forward surrogates improved sharply versus the 256-sample run. The emissivity holdout-thickness-tail MAE dropped from about `0.0623` to about `0.0236`, and the tandem cooling-proxy MAE dropped from about `2.91 W/m²` to about `1.30 W/m²`. The conditional VAE still benefits from best-of-N proposal sampling plus full WPTherml reranking; its strongest behavior is in candidate generation, not single-sample reconstruction.

The first conditional diffusion baseline is competitive with that scaled CVAE result. On the same `4096`-sample training corpus and the same reference target used for proposal validation, best-of-64 diffusion sampling reached a fully verified total target error of about `0.1909`, versus about `0.1902` for the best-of-64 CVAE run. At this stage diffusion is a valid generator in the stack, but not yet a decisive improvement over the CVAE.

The strongest current workflow is now a hybrid one: broad CVAE sampling, surrogate shortlist ranking, then full WPTherml reranking. On the reference target above, `256` CVAE samples trimmed to the surrogate top `16` produced a verified best candidate with total target error of about `0.0946`, which is substantially better than the earlier best-of-64 full-verification result (`~0.1902`) while still avoiding verification of all `256` samples. The same shortlist trick did not improve the diffusion model as much, so shortlist quality is generator-dependent.

After additional real-data ablations, this should be treated as the current local ceiling for the `4096`-sample stack and present model family. The most stable retained workflow is:

```text
baseline CVAE (kl=0.02, latent_dim=16)
	-> sample 256 candidates
	-> surrogate shortlist top 16
	-> full WPTherml verification
```

Verified reference points with that retained workflow:

- sample255-like target: total target error `~0.0946`
- sample777-like target: total target error `~0.0712`

Branches that were tested and did not beat this retained baseline in a robust way:

- diversity-aware shortlist filtering: no material gain
- larger candidate pools (`512` or `1024`) at fixed top-16 budget: worse than `256`
- single-target empirical rank calibration: overfit and failed out-of-sample
- tuned CVAE (`kl=0.15`, `latent_dim=32`): improved one target but collapsed on another
- mixed baseline-CVAE plus diffusion proposal pools under the current ranker: substantially worse

The April 2026 audit also tested an explicit categorical-material CVAE decoder after identifying the soft-train / hard-decode mismatch as a plausible defect. That branch was retrained on the same `4096`-sample corpus after fixing the project environment to use CUDA on the RTX 3080. It trained cleanly but did not improve verification quality: the best fully verified errors were about `0.4446` from raw best-of-64 sampling and `0.4879` from the `256 -> top 16` shortlist on the sample255-like target, and about `0.6499` raw versus `0.3749` shortlist on the sample777-like target. Those results are far worse than the retained `~0.0946` / `~0.0712` baseline, so the categorical decoder is preserved as an explicit experiment mode, while the default and recommended path remains the original continuous-relaxation CVAE plus shortlist.

Within the current dataset and architecture family, further local tuning is not well supported by the evidence. The next justified jump is a structural one: materially more data, experimental feedback, or a new algorithmic ingredient rather than another small search over shortlist or CVAE hyperparameters.

## Notes

- The `mock` backend exists to validate pipeline mechanics quickly.
- The `wptherml` backend assumes an Air / multilayer / Ag reflector / Air stack and currently computes scalar cooling targets from the same proxy metric used by the mock backend.