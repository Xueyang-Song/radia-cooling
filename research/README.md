# Radiative Cooling + Machine Learning — Research Compendium

> A comprehensive study companion for the paper:
> **机器学习驱动的辐射制冷材料设计进展**
> *(Progress in Machine-Learning-Driven Radiative Cooling Material Design)*

---

## 📂 Document Index

| # | Document | What It Covers |
|---|---|---|
| 01 | [ML Models Explained](01_ML_Models_Explained.md) | Beginner-friendly guide to every ML model and algorithm in the paper. Analogies, strengths/weaknesses, visual explanations. |
| 02 | [How the Paper Uses Each Model](02_How_Paper_Uses_Each_Model.md) | Specific mapping of each model to its role, inputs, outputs, and cited examples in the paper. |
| 03 | [Generative AI Proposals](03_Generative_AI_Proposals.md) | Deep dive into the paper's vision for generative AI (GAN, VAE, Diffusion, DRL) in inverse design. |
| 04 | [Future Needs vs Existing Advances](04_Future_Needs_vs_Existing_Advances.md) | Gap analysis: what the paper says the field needs vs. what already exists today. |
| 05 | [Datasets & Similar Research](05_Datasets_and_Similar_Research.md) | Open datasets, code repos, databases, and Google Scholar results for related papers. |
| 06 | [RCML Final Audit Report](06_RCML_Final_Audit_Report.md) | Final repo audit: data cleanliness, free-data rationale, model comparison, CUDA environment fix, and the retained best workflow. |

---

## Quick Paper Summary (English)

This is a **Chinese-language review paper** surveying how machine learning is being used to design radiative cooling (RC) materials — materials that can cool objects below ambient temperature without any energy input by emitting thermal radiation through the atmosphere's 8-13 μm transparency window.

### The Three-Tier ML Framework

```
Tier 1: FORWARD SCREENING          Tier 2: FORWARD OPTIMIZATION       Tier 3: INVERSE / GENERATIVE
─────────────────────────           ───────────────────────────         ──────────────────────────────
"Which existing designs             "What's the BEST design in         "Given a target spectrum,
are promising?"                      this parameter space?"             generate a structure."

Models: KNN, RF, XGBoost            Models: ANN, CNN + GA/PSO/BO       Models: DNN/Tandem, GAN, VAE,
                                                                         Diffusion, DRL

Dataset: 100s of samples            Dataset: 1,000s-10,000s            Dataset: 10,000s-100,000s
Speed: Minutes                       Speed: Hours                       Speed: Seconds per design
```

### Material Systems Covered

1. **Particle-filled polymer composites** — TiO₂, SiO₂, BaSO₄ particles in PDMS/PMMA/PE matrices
2. **Multilayer thin films** — Alternating dielectric/metal stacks (SiO₂/TiO₂/Ag/Al...)
3. **Colored & transparent RC films** — Multi-objective: cooling + aesthetics + visibility
4. **Metasurfaces & micro/nanostructures** — Photonic crystals, gratings, biomimetic moth-eye

### Key Physics

- **Goal**: Maximize solar reflectance (0.3-2.5 μm) + maximize thermal emissivity (8-13 μm)
- **Simulation tools**: Transfer Matrix Method (TMM), FDTD, RCWA, Mie scattering, Monte Carlo
- **The ML promise**: Replace expensive physics simulations with fast surrogate models, then use those surrogates for optimization and inverse design

---

## How to Navigate This Research

**If you're completely new to ML:**
→ Start with [01_ML_Models_Explained.md](01_ML_Models_Explained.md)

**If you understand ML and want to know how the paper applies it:**
→ Read [02_How_Paper_Uses_Each_Model.md](02_How_Paper_Uses_Each_Model.md)

**If you're interested in the cutting-edge generative AI proposals:**
→ Read [03_Generative_AI_Proposals.md](03_Generative_AI_Proposals.md)

**If you want to know what's achievable now vs. what's aspirational:**
→ Read [04_Future_Needs_vs_Existing_Advances.md](04_Future_Needs_vs_Existing_Advances.md)

**If you want to download code and start experimenting:**
→ Read [05_Datasets_and_Similar_Research.md](05_Datasets_and_Similar_Research.md)

**If you want the final repo-level conclusion and retained best pipeline:**
→ Read [06_RCML_Final_Audit_Report.md](06_RCML_Final_Audit_Report.md)

---

## Glossary of Key Terms

| Term | Meaning |
|---|---|
| **Radiative Cooling (RC)** | Passive cooling via thermal radiation emission through the atmospheric transparency window |
| **Atmospheric Window** | 8-13 μm wavelength range where Earth's atmosphere is mostly transparent to IR radiation |
| **Emissivity (ε)** | How efficiently a surface emits thermal radiation (0 = perfect mirror, 1 = perfect emitter) |
| **Solar Reflectance (ρ_solar)** | Fraction of sunlight reflected (higher = less solar heating) |
| **Forward Model** | Structure → Spectrum (given a design, predict its optical properties) |
| **Inverse Model** | Spectrum → Structure (given desired properties, generate a design) |
| **Surrogate Model** | A fast ML approximation of an expensive physics simulation |
| **Transfer Matrix Method (TMM)** | Analytical method to calculate optical properties of multilayer thin films |
| **FDTD** | Finite-Difference Time-Domain — numerical EM simulation for complex geometries |
| **RCWA** | Rigorous Coupled-Wave Analysis — simulation for periodic structures (gratings, metasurfaces) |
| **Mie Theory** | Analytical solution for light scattering by spherical particles |
| **Tandem Network** | Forward NN + Inverse NN trained together; forward network regularizes the inverse |
| **One-to-many problem** | Multiple different structures can produce similar spectra — the core challenge of inverse design |
