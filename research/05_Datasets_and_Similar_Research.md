# Open Datasets, Code Repositories & Similar Research

> Resources identified for studying radiative cooling + machine learning
> Compiled from Google Scholar, GitHub, Zenodo, and Kaggle searches

---

## Part A: Open-Source Code Repositories (Downloadable)

### Directly Related to Radiative Cooling + ML

| Repository | Description | Language | Stars | URL |
|---|---|---|---|---|
| **iguanaus/ScatterNet** | Nanophotonic particle simulation & inverse design via ANN (Peurifoy et al., Science Advances 2018). Includes training data and pre-trained models. **The foundational codebase for ANN-based spectral prediction in this field.** | MATLAB + Python | 85 | https://github.com/iguanaus/ScatterNet |
| **sanmoyo/radiative_cooling_ML_dissertation** | GA optimization of multilayer photonic radiator design using WPTherml (transfer matrix) + DEAP (genetic algorithm). University of Southampton dissertation. | Jupyter Notebook | 3 | https://github.com/sanmoyo/radiative_cooling_ML_dissertation |
| **refetaliyalcin/ColorRCMC** | Mie theory + Monte Carlo radiative transfer for colored radiative cooling coatings with nanoparticles (Yalçın et al., ACS Photonics). Generates spectra for core-shell and plain nanoparticle mixtures. GPU-accelerated MATLAB. | MATLAB | 11 | https://github.com/refetaliyalcin/ColorRCMC |
| **cuity1/Radiation-cooling-and-heating-calculation** | Radiative cooling and heating power calculations in Python. | Python | 12 | https://github.com/cuity1/Radiation-cooling-and-heating-calculation |
| **yuruiquLab/Radiative-cooling** | Simulations of random SiO₂ and Al₂O₃ sphere distributions for radiative cooling. | Jupyter Notebook | 4 | https://github.com/yuruiquLab/Radiative-cooling |
| **JingWei-William/radiative-cooling-solar-heating-power** | Radiative cooling and solar heating power calculations. Published: doi.org/10.1016/j.csite.2024.105232 | MATLAB | 5 | https://github.com/JingWei-William/radiative-cooling-solar-heating-power |
| **GiuseppeELio/FRESCO-Board** | Arduino/ESP8266 measurement station for passive radiative cooling experiments — hardware + software. | Jupyter + Arduino | 7 | https://github.com/GiuseppeELio/FRESCO-Board |
| **FoleyLab/wptherml** | Transfer Matrix Method library for multilayer thin films — widely used to generate training data for ML models. Referenced in multiple RC-ML papers. | Python | — | https://github.com/FoleyLab/wptherml |
| **Dasol-Lee-Yonsei-BME/ViBA-Rad** | Visualization and basic analysis tools for radiative cooling | Tcl | 5 | https://github.com/Dasol-Lee-Yonsei-BME/ViBA-Rad |
| **Collins-kariuk/Physics-Thesis-PDRCs** | Passive Daytime Radiative Cooling with COMSOL Multiphysics | TeX | 3 | https://github.com/Collins-kariuk/Physics-Thesis-PDRCs |

### Nanophotonics Inverse Design (Directly Applicable Methods)

| Repository | Description | Language | Stars | URL |
|---|---|---|---|---|
| **FiodarM/InvDesignNet** | Training neural networks for inverse design of nanophotonic gratings. **Includes ~1GB pre-generated dataset (Google Drive link in README).** Forward + inverse model Jupyter notebooks. | Jupyter + Python | 21 | https://github.com/FiodarM/InvDesignNet |
| **ZooBeasts/cWGAN-GP_Inverse_Design** | Conditional Wasserstein GAN for inverse design of disordered waveguide nanophotonics. Directly demonstrates GAN-based generative inverse design. | Python + PyTorch | 13 | https://github.com/ZooBeasts/cWGAN-GP_Inverse_Design_Disordered_Waveguide_Nanophotonics |
| **wonderit/maxwellfdfd-controlgan** | GAN-based inverse design of nanophotonic devices | Jupyter Notebook | 12 | https://github.com/wonderit/maxwellfdfd-controlgan |
| **jLabKAIST/Physics-Informed-RL** | Physics-informed reinforcement learning for freeform nanophotonic inverse design | Python | 14 | https://github.com/jLabKAIST/Physics-Informed-Reinforcement-Learning |
| **QuentinWach/beamz** | GPU-accelerated FDTD simulations for inverse design / gradient-based optimization of nanophotonic devices | Python | 32 | https://github.com/QuentinWach/beamz |
| **lxvm/DeltaRCWA.jl** | Nanophotonics RCWA solver for inverse design of metamaterials | Julia | 14 | https://github.com/lxvm/DeltaRCWA.jl |
| **fancompute/ceviche** | Differentiable FDTD/FDFD solver in Python — enables gradient-based electromagnetic optimization | Python | — | https://github.com/fancompute/ceviche |
| **NanoComp/meep** | MIT Electromagnetic Equation Propagation — open-source FDTD with adjoint optimization | C++ + Python | — | https://github.com/NanoComp/meep |

---

## Part B: Optical Materials Databases

| Database | Content | URL | Relevance |
|---|---|---|---|
| **refractiveindex.info** | Comprehensive refractive index (n, k) data for thousands of materials across UV-Vis-IR wavelengths. Essential input for ANY radiative cooling simulation. | https://refractiveindex.info | **Critical** — primary source of optical constants |
| **Materials Project** | Computed properties of 150,000+ inorganic materials, some with dielectric/optical data | https://materialsproject.org | Useful for identifying candidate materials |
| **AFLOW** | >3.5M material entries with computed properties | https://aflowlib.org | Large-scale materials screening |
| **NOMAD** | Open archive of materials science computational data | https://nomad-lab.eu | Growing optical data |
| **HITRAN** | High-resolution molecular absorption database — atmospheric transmission spectra | https://hitran.org | **Critical** — needed to model atmospheric window |
| **MODTRAN** | Atmospheric transmittance/radiance model | Restricted but widely available | For accurate atmospheric window modeling |

---

## Part C: Similar Research Papers (From Google Scholar Search)

### Core Papers Directly at the Intersection of ML + Radiative Cooling

| Paper | Year | Key Contribution | Citations |
|---|---|---|---|
| **Peurifoy et al.** "Nanophotonic particle simulation and inverse design using ANN" *Science Advances* | 2018 | **Foundational work.** Proved ANNs can predict electromagnetic spectra and perform inverse design. Referenced as [19] in the paper. | 1,300+ |
| **Guan et al.** "ML-Enabled Inverse Design of Radiative Cooling Film with On-Demand Transmissive Color" *ACS Photonics* | 2023 | Conditional deep learning for colored transmissive RC films. Multi-objective: color + cooling + transparency. Referenced as [24]. | 68 |
| **Keawmuang et al.** "Inverse design of colored daytime radiative coolers using deep neural networks" *Solar Energy Mater. & Solar Cells* | 2024 | Tandem neural network for colored RC. Demonstrates the forward-inverse architecture. Referenced as [37]. | 26 |
| **Kim et al.** "Deep learning-assisted inverse design of nanoparticle-embedded radiative coolers" *Optics Express* | 2024 | CNN-based inverse design specifically for particle-embedded RC systems. Referenced as [35]. | 15 |
| **Le et al.** "AI-enabled design of extraordinary daytime radiative cooling materials" *Solar Energy Mater. & Solar Cells* | 2024 | Generative ML model for high-performance daytime RC. Referenced as [25]. | 3 |
| **Ding et al.** "ML-assisted design of a robust biomimetic radiative cooling metamaterial" *ACS Materials Letters* | 2024 | KNN-based design of biomimetic RC metamaterial. Referenced as [30]. | 48 |
| **Su et al.** "ML-enabled design of metasurface based near-perfect daytime radiative cooler" *Solar Energy Mater. & Solar Cells* | 2023 | ML framework for metasurface RC emitter design. Referenced as [29]. | — |
| **Guo et al.** "Design of highly selective radiative cooling structure accelerated by materials informatics" *Optics Letters* | 2020 | **First Bayesian optimization work in RC.** Used <1% of design space. Referenced as [22]. | — |
| **Yu et al.** "General deep learning framework for emissivity engineering" *Light: Science & Applications* | 2023 | Deep Q-Network (DRL) for emissivity design including radiative cooling. | 74 |
| **Sullivan & Lee** "Deep learning-based inverse design of microstructured materials for thermal radiation control" *Scientific Reports* | 2022/2023 | Deep learning for microstructured thermal radiation control. Open-source based approach. | 24/16 |

### Broader ML + Materials Design (Methodological Foundation)

| Paper | Year | Key Contribution | Citations |
|---|---|---|---|
| **Cheng et al.** "AI-driven approaches for materials design and discovery" *Nature Materials* | 2025 | Comprehensive review of AI in materials science. Referenced as [17]. | — |
| **Shahriari et al.** "Taking the human out of the loop: A review of Bayesian optimization" *Proc. IEEE* | 2016 | Definitive BO tutorial. Referenced as [20]. | 12,000+ |
| **Lee et al.** "ML-based inverse design methods considering data characteristics and design space size" *Materials Horizons* | 2023 | Review of inverse design approaches in materials science. | 120 |
| **Wang et al.** "Inverse design of materials by machine learning" *Materials* | 2022 | Overview of ML for materials inverse design. | 131 |
| **Malkiel et al.** "Plasmonic nanostructure design and characterization via deep learning" *Light: Sci. & App.* | 2018 | Deep learning for plasmonic structure design. Referenced as [34]. | — |

### Recent Papers Not Cited But Highly Relevant

| Paper | Year | Key Contribution | Citations |
|---|---|---|---|
| **Zhou et al.** "Deep-learning-based multilayer nano-film structure reverse design for efficient passive radiative cooling" *Chinese Optics Letters* | 2026 | Very recent DNN-based reverse design of multilayer films for RC. | 3 |
| **Chen et al.** "Reinforcement learning-based inverse design of composite films for spacecraft smart thermal control" *Physical Chemistry Chemical Physics* | 2025 | RL for thermal control film design — directly applicable to RC. | 4 |
| **Gan et al.** "Predicting surface temperature of radiative cooling coatings with time-series forecasting" *Renewable Energy* | 2025 | ML for RC surface temperature prediction using small-batch datasets. | 3 |
| **Wang et al.** "ML assisted energy performance analysis of semi-transparent PV glazing with radiative cooling film" *Energy and Buildings* | 2025 | ML for building-integrated RC film performance analysis. | 6 |
| **Kim et al.** "High-performance transparent radiative cooler designed by quantum computing" *ACS Energy Letters* | 2022 | Quantum annealing + active ML for transparent RC design. Novel optimization approach. | 116 |
| **Fan & Li** "Emissivity prediction of multilayer film radiators by ML using an ultrasmall dataset" *ES Energy and Environment* | 2022 | ML for emissivity prediction with very small datasets — addresses the data scarcity challenge directly. | 7 |
| **Carne** "Machine Learning and Optimization Towards Improved Radiative Cooling Paints" *Purdue thesis* | 2025 | Open-source FOS tool: Mie + Monte Carlo + ML for nanoparticle RC paint design. | — |

---

## Part D: How to Get Started with These Resources

### Recommended Download Priority

**For learning ML + inverse design fundamentals:**
1. `iguanaus/ScatterNet` — Clone it, run the demo, see how ANN predicts spectra and performs inverse design
2. `FiodarM/InvDesignNet` — Download the ~1GB dataset, explore the forward/inverse model notebooks

**For radiative cooling simulation specifically:**
3. `FoleyLab/wptherml` — Install it, run transfer matrix calculations, generate your own RC training data
4. `refetaliyalcin/ColorRCMC` — If you have MATLAB, see how Mie theory + Monte Carlo produces RC spectra

**For advanced generative / inverse design:**
5. `ZooBeasts/cWGAN-GP_Inverse_Design` — See how a conditional GAN actually works for inverse design
6. `jLabKAIST/Physics-Informed-RL` — Explore how reinforcement learning designs photonic structures

**For optical properties data:**
7. Visit `refractiveindex.info` and download n(λ), k(λ) data for common RC materials:
   - SiO₂, TiO₂, Al₂O₃, Si₃N₄, HfO₂ (dielectric layers)
   - Ag, Al (metal reflectors)
   - PDMS, PMMA, PE (polymer matrices)
   - BaSO₄, CaCO₃ (particle fillers)

### Generating Your Own Training Data

The paper repeatedly notes that most ML models in RC are trained on simulated data. Here's how to create your own:

```
Step 1: Choose a structure type
        → Multilayer film? Use WPTherml (Python TMM)
        → Nanoparticle composite? Use ColorRCMC (MATLAB Mie+MC)
        → Metasurface? Use Meep (FDTD) or S4 (RCWA)

Step 2: Define parameter ranges
        → e.g., layer thickness 10-500 nm, materials from {SiO2, TiO2, Al2O3}

Step 3: Sample parameter space
        → Latin Hypercube Sampling or random sampling
        → Generate 5,000-50,000 parameter combinations

Step 4: Run simulations
        → Calculate full UV-Vis-MIR spectrum (0.3-25 μm) for each combination
        → Store as (parameters, spectrum, integrated metrics) tuples

Step 5: Train ML models
        → Use the dataset for any of the ML approaches described in the paper
```

---

## Part E: Key Observations from the Literature Search

1. **The field is growing rapidly** — most high-impact papers are from 2023-2025, with 2026 papers already appearing.

2. **No standardized benchmark exists** — every research group generates their own simulation data. This is the #1 bottleneck for reproducibility and comparison.

3. **GitHub adoption is increasing** — more papers now share code, but datasets are still rarely shared openly (they're expensive to generate and considered competitive advantages).

4. **The Peurifoy et al. (2018) ScatterNet paper** is the methodological ancestor of essentially all ANN-based work in this space — if you understand that paper, you understand the foundation.

5. **Colored/transparent RC films** is the hottest sub-topic, because it's where multi-objective optimization and inverse design are most needed and most impactful.

6. **Kaggle has zero directly relevant datasets** for radiative cooling ML. Zenodo also has none. This is a clear gap.
