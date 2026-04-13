# How This Paper Plans to Use Each ML Model

> Mapping every model to its specific role, dataset, and use case in the paper
> *"Machine-Learning-Driven Advances in Radiative Cooling Material Design"*

---

## Overview: Three-Tier Framework

The paper organizes ML usage into three tiers:

| Tier | Name | Goal | Key Models |
|---|---|---|---|
| **Tier 1** | Data-Driven Forward Screening | Predict cooling performance from structure parameters | KNN, RF, XGBoost, ANN, CNN |
| **Tier 2** | Forward Optimization | Find the best design parameters within a given space | GA, PSO, BO (often + Tier 1 surrogate) |
| **Tier 3** | Inverse/Generative Design | Generate structures from target performance specs | Tandem NN, GAN, VAE, Diffusion, DRL |

---

## Tier 1: Forward Screening — "Given this structure, how well does it cool?"

### KNN in Radiative Cooling

**What it predicts:** Absorption/emission spectrum of metasurface structures
**Input features:** Geometric parameters of the metasurface unit cell (period, width, height, fill fraction)
**Output:** Spectral absorptivity/emissivity values, optimal structural parameters
**Dataset source:** FDTD or RCWA electromagnetic simulations
**Specific application cited:** Metasurface-based daytime radiative coolers (ref [29-30])

**How it's used in practice:**
1. Simulate ~1,000 metasurface geometries using FDTD
2. Store (geometry → spectrum) pairs
3. When a new candidate geometry is proposed, KNN finds the 5 most similar geometries already simulated
4. Averages their spectra to predict the new geometry's performance
5. Use this for rapid initial screening before running expensive full simulations

**Paper's assessment:** Good for "parametrically clear" structures with few variables. Limited to well-sampled regions of the design space.

---

### Random Forest in Radiative Cooling

**What it predicts:** (a) Absorption/emission of metasurface coolers, (b) Scattering efficiency of particles
**Input features:** Structural parameters (particle size, coating thickness, volume fraction, geometric dimensions)
**Output:** (a) Spectral performance mapping, (b) Scattering efficiency in 0.3–2.5 μm solar band
**Dataset source:** Mie theory calculations, FDTD simulations
**Specific applications cited:**
- Metasurface radiative cooler prediction and design enhancement (ref [29])
- Scattering efficiency prediction for passive daytime radiative cooling particles (ref [31])

**How it's used in practice:**
1. Generate training data via Mie theory (for particles) or FDTD (for metasurfaces)
2. Train RF regressor with structural features as input, performance metrics as output
3. RF identifies which variables most influence performance (feature importance)
4. Use trained RF as a fast filter: quickly evaluate thousands of candidate designs, then run full simulation only on the top 5%

**Paper's assessment:** Better than KNN for complex non-linear relationships. Provides feature importance as a bonus. Recommended for intermediate complexity problems.

---

### XGBoost in Radiative Cooling

**What it predicts:** Thermal properties of radiative cooling aerogels
**Input features:** Aerogel composition, structural parameters, environmental conditions
**Output:** Thermal performance metrics (cooling power, equilibrium temperature drop)
**Dataset source:** Experimental measurements + simulations (31 samples in one cited study)
**Specific application cited:** Radiative cooling aerogel thermal property prediction (ref [32])

**Unique value highlighted by the paper:** XGBoost is used not just for prediction but also for EXPLANATION:
1. Train XGBoost to predict cooling performance
2. Apply SHAP (SHapley Additive exPlanations) to the trained model
3. SHAP reveals which input factors most influence cooling (e.g., "particle size matters 3× more than ambient humidity")
4. This guides experimentalists on what to optimize first

**Paper's assessment:** Best-performing traditional ML model for tabular/structured data. The dual predictor + explainer role makes it uniquely valuable for understanding the physics driving cooling performance.

---

### ANN (Artificial Neural Network) in Radiative Cooling

**What it predicts:** (a) Long-term radiative cooling performance of windows, (b) Electromagnetic response of nanostructures
**Input features:**
- (a) Infrared emissivity settings, city/climate parameters, building features
- (b) Nanoparticle geometric parameters (shell thicknesses, core radius, materials)
**Output:** 
- (a) Long-term cooling energy savings
- (b) Scattering/absorption cross-sections, spectral responses
**Dataset source:**
- (a) Building energy simulation data across multiple tropical cities
- (b) T-matrix electromagnetic simulations
**Specific applications cited:**
- Radiative cooling window emissivity optimization across climates (ref [33])
- Nanophotonic particle simulation and inverse design (Peurifoy et al., ref [19])

**How it's used in practice (as surrogate):**
1. Run ~50,000 electromagnetic simulations with random parameter combinations
2. Train ANN: input = geometric parameters → output = full spectrum (200+ wavelength points)
3. Trained ANN can predict any new design's spectrum in milliseconds (vs. minutes for simulation)
4. Use ANN as the "evaluation engine" inside GA/PSO/BO optimization loops

**Paper's assessment:** The workhorse surrogate model. Most widely applicable. Forms the backbone of the "simulation → surrogate → optimization" pipeline. Ref [19] (Peurifoy et al., Science Advances 2018) is specifically highlighted as the methodological foundation for this approach in radiative cooling.

---

### CNN (Convolutional Neural Network) in Radiative Cooling

**What it predicts:** Complex spectral-to-structural mappings, feature extraction from high-dimensional spectra
**Input features:** Full spectral curves (reflectance/emissivity vs wavelength), material composition descriptors
**Output:** Structural parameters for inverse design, or spectral predictions for forward design
**Dataset source:** Large-scale TMM or FDTD simulation databases
**Specific applications cited:**
- Deep learning-assisted inverse design of nanoparticle-embedded radiative coolers (ref [35])
- Feature extraction from spectral data in radiative cooling material design

**How it's used in practice:**
1. Generate a large dataset of (structure, spectrum) pairs via simulation
2. Feed the spectral curves directly as 1D inputs to a CNN
3. CNN's convolutional filters automatically learn to detect critical spectral features:
   - Solar band behavior (0.3–2.5 μm)
   - Atmospheric window emission (8–13 μm)
   - Transition bands
4. These learned features feed into downstream prediction or inverse design

**Paper's assessment:** Superior to ANN for spectral data because it captures local wavelength correlations. Essential when the spectral shape matters, not just integrated metrics. The bridge between forward prediction and generative inverse design.

---

## Tier 2: Forward Optimization — "What's the best design within these boundaries?"

### GA (Genetic Algorithm) in Radiative Cooling

**Primary application:** Multilayer thin film design
**Design variables optimized:**
- Discrete: Material type per layer (SiO₂, TiO₂, Al₂O₃, HfO₂, Si₃N₄, Ag, etc.)
- Discrete: Number of layers
- Continuous: Thickness of each layer
- Discrete: Layer ordering/arrangement
**Fitness function:** Radiative cooling power density (W/m²), net cooling below ambient, spectral selectivity

**Specific workflows described:**
1. **GA + Transfer Matrix Method (TMM):**
   - GA proposes candidate multilayer designs
   - TMM directly calculates their spectra (fast for <20 layers)
   - GA evolves population toward maximum cooling power
   - Example: You et al. — flexible mixed optimization for multilayer radiative cooling films

2. **GA + Neural Network Surrogate:**
   - Train ANN/CNN on TMM data
   - GA proposes candidates, surrogate evaluates instantly
   - Top candidates verified with real TMM
   - Much faster for large populations or complex stacks

3. **Memetic Algorithm (GA + local search):**
   - GA finds promising regions globally
   - Local optimizer fine-tunes within those regions
   - Example: Mira et al. — selective passive daytime radiative cooler optimization

**Specific 2025+ results highlighted:**
- DMDMD transparent colored radiative cooler: GA optimized materials and thicknesses for simultaneous high visible transmittance + near-IR reflection + atmospheric window emission
- Metasurface + multilayer solar reflector: GA achieved 91.87% solar reflectance and 111.7 W/m² net cooling

**Paper's assessment:** The go-to optimizer for multilayer systems because it naturally handles mixed discrete-continuous variables. Usually the first choice when the design involves material selection.

---

### PSO (Particle Swarm Optimization) in Radiative Cooling

**Primary application:** Microstructure and continuous-parameter optimization
**Design variables optimized:**
- Period/pitch of periodic structures
- Fill fraction / duty cycle
- Height/depth of features
- Particle diameter
- Volume fraction
- Film thickness (continuous)
**Objective function:** Mid-IR emissivity, solar reflectance, net cooling power

**Specific workflows described:**

1. **"FDTD → Neural Network → Adaptive PSO" Three-Stage Pipeline:**
   - Stage 1: FDTD simulations generate training data for truncated pyramid microstructures
   - Stage 2: Neural network surrogate trained (R² = 0.99841 for atmospheric window emissivity)
   - Stage 3: Adaptive PSO searches the surrogate for optimal geometry
   - Result: Near-unity average emissivity in the atmospheric window
   - *This is the most detailed PSO workflow in the paper*

2. **Surrogate-Assisted Multi-Objective PSO:**
   - ~2,000 evaluations sufficient for 30-variable problems
   - Finds Pareto front approximation
   - Applied to multilayer grating radiator (81.8% emission, 118.17 W/m² cooling)

3. **PSO for Nanoparticle Coatings:**
   - Bu & Bao: PSO optimizes particle parameters and coat thickness
   - Target: Efficient radiative cooling with minimum coating thickness
   - Handles statistical scattering behavior of random particle dispersions

**Paper's assessment:** Best for continuous-parameter optimization of microstructures. Faster convergence than GA when all variables are continuous. The "FDTD → NN → PSO" pipeline is positioned as a model workflow.

---

### BO (Bayesian Optimization) in Radiative Cooling

**Primary application:** High-cost-per-evaluation design problems
**Design variables optimized:** Photonic crystal parameters, multilayer thicknesses, metasurface geometries
**Budget constraint:** Typically <100 evaluations total (vs. thousands for GA/PSO)

**Specific applications described:**

1. **Pioneering work (Guo et al., 2020):**
   - Combined RCWA simulation with Bayesian Optimization
   - Found highly selective emitter structure (optimal atmospheric window emission)
   - Used <1% of the candidate design space
   - This is highlighted as the first BO application in radiative cooling

2. **Colored Radiative Cooler (Gunay & Shiomi):**
   - Multi-objective: color fidelity + cooling performance simultaneously
   - BO balanced exploration vs. exploitation across both objectives
   - Small evaluation budget sufficient for identifying high-performing designs

3. **VO₂ Phase-Change Multilayer (BO + FDTD):**
   - Automatically searched for optimal geometry without predefining phase-change thresholds
   - BO's uncertainty quantification was crucial for efficiently exploring the bi-stable design landscape

**Paper's assessment:** The most sample-efficient method. Essential when each evaluation costs hours of simulation time. Limited to ~20 or fewer design variables due to Gaussian Process scaling. The "smart" alternative to brute-force search.

---

## Tier 3: Inverse/Generative Design — "Generate a structure that achieves this target"

### Tandem Neural Network for Inverse Design

**Application:** Colored daytime radiative coolers
**Input (to the inverse net):** Target color coordinates + target cooling power + target solar reflectance
**Output:** Multilayer film structure (materials, thicknesses, layer count)
**How ambiguity is handled:** The forward network (frozen) validates that the generated structure actually produces the desired spectrum, so the inverse network only needs to produce *a* valid solution, not *the* solution.

**Specific cited work:** Keawmuang et al. (ref [37]) — Inverse design of colored daytime radiative coolers using deep neural networks (Solar Energy Materials and Solar Cells, 2024). Also Li et al. (ref [36]) — bidirectional neural networks + GA for colored passive cooling multilayer films.

---

### GAN for Inverse Design

**Proposed application:** Generating entirely new radiative cooling structures that satisfy multi-objective constraints
**How it would work in radiative cooling:**
1. Train Generator on a database of validated structures
2. Condition on target: "solar reflectance > 95%, atmospheric window emissivity > 90%, visible color = blue"
3. Generator outputs candidate structures
4. Discriminator ensures they're physically plausible
5. Physics simulator validates top candidates

**Paper's positioning:** This is the cutting-edge frontier. The paper explicitly lists GAN-based inverse design as one of the most promising directions for radiative cooling material discovery.

---

### VAE for Inverse Design

**Proposed application:** Same as GAN, but with better diversity and uncertainty quantification
**Advantage over GAN:** Can sample from different regions of the latent space to get diverse solutions, rather than a single "best" output.

---

### DRL / DQN for Sequential Design

**Cited work:** Yu et al. — "General deep learning framework for emissivity engineering" used Deep Q-Network for radiative cooling design
**Proposed application:** Sequentially building up a multilayer structure decision by decision (add layer of X material, set thickness to Y, add another layer...)
**Advantage:** Naturally handles the sequential, decision-based nature of multilayer film design

---

## Summary: Model-to-Application Mapping

| Material System | Best Forward Model | Best Optimizer | Inverse Design Approach |
|---|---|---|---|
| **Particle-filled polymers** | RF, ANN | PSO | CNN-based inverse |
| **Multilayer films** | ANN, CNN | GA (discrete + continuous) | Tandem NN, bidirectional NN + GA |
| **Colored/transparent films** | Tandem NN | GA or BO | GAN, VAE, conditional generation |
| **Metasurface/microstructures** | KNN, CNN | PSO, BO | DRL sequential design |
| **Aerogels** | XGBoost | GA | Not yet explored |

---

## Key Insight from the Paper

The paper's main argument is that these methods form a **progressive pipeline** — not isolated tools:

```
Physics simulation data
    → trains surrogate model (Tier 1: KNN/RF/XGBoost/ANN/CNN)
        → enables fast optimization (Tier 2: GA/PSO/BO)
            → provides training data for generative models (Tier 3: GAN/VAE/Diffusion)
                → generates novel designs beyond human intuition
                    → validated by physics simulation (closes the loop)
```

The field is moving from left to right in this pipeline, and the paper argues the frontier is in making Tier 3 reliable and practical.
