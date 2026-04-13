# Machine Learning Models Explained (For Beginners)

> A plain-English guide to every ML model and optimization algorithm mentioned in the paper
> *"Machine-Learning-Driven Advances in Radiative Cooling Material Design"*

---

## Table of Contents

1. [What Is Machine Learning?](#1-what-is-machine-learning)
2. [Traditional ML Models (Forward Prediction)](#2-traditional-ml-models)
   - KNN
   - Random Forest
   - XGBoost
3. [Neural Network Models (Deep Learning)](#3-neural-network-models)
   - ANN (Artificial Neural Network)
   - CNN (Convolutional Neural Network)
   - DNN / Tandem Neural Network
   - GNN (Graph Neural Network) — mentioned as future
4. [Optimization Algorithms](#4-optimization-algorithms)
   - GA (Genetic Algorithm)
   - PSO (Particle Swarm Optimization)
   - BO (Bayesian Optimization)
5. [Generative Models (Inverse Design)](#5-generative-models)
   - VAE (Variational Autoencoder)
   - GAN (Generative Adversarial Network)
   - Diffusion Models
   - Deep Reinforcement Learning (DRL / DQN)

---

## 1. What Is Machine Learning?

Machine learning is a way to teach a computer to recognize patterns in data, so it can make predictions or decisions without being explicitly programmed for every case.

**Analogy:** Imagine you tasted 1,000 different coffees and wrote down the beans, roast time, water temperature, and grind size for each one, along with a score for how good it was. After enough data, you'd start to *feel* which combinations make great coffee — even for recipes you've never tried. Machine learning does the same thing, but with math instead of taste buds.

In technical terms:
- **Input** = features you feed to the model (e.g., particle size, layer thickness)
- **Output** = prediction the model gives back (e.g., solar reflectance, cooling power)
- **Training** = the process of showing the model thousands of examples so it learns the pattern
- **Inference** = using the trained model to predict the output for a *new* input it hasn't seen before

### Supervised vs. Unsupervised vs. Generative

| Paradigm | What it does | Used in this paper for |
|---|---|---|
| **Supervised learning** | Learns from labeled examples (input → known output) | Predicting cooling performance from structure parameters |
| **Unsupervised learning** | Finds hidden patterns in data without labels | Not a main focus of this paper |
| **Generative models** | Creates new data samples that look like the training data | Inverse design — generating new material structures from target performance |

---

## 2. Traditional ML Models (Forward Prediction)

These are the "classic" machine learning algorithms. They work well with small-to-medium datasets where the input features are clearly defined numbers (like particle size = 200 nm, layer thickness = 0.5 μm).

### 2.1 K-Nearest Neighbors (KNN)

**What it is in plain English:**
KNN is the simplest ML algorithm. When you give it a new data point, it looks at the K most similar examples it already knows about and averages their answers.

**How it works:**
1. You have a dataset of structures and their known cooling performance.
2. A new structure comes in that you want to predict.
3. KNN measures the "distance" between the new structure's parameters and every known example.
4. It picks the K closest ones (e.g., K=5 means the five most similar).
5. It averages their cooling performance to make its prediction.

**Analogy:** You move to a new neighborhood and want to guess the price of your house. You look at the 5 most similar houses nearby (same size, same age, same number of bedrooms) and average their prices. That's KNN.

**Strengths:**
- Extremely simple to understand and implement
- No training phase needed — it just memorizes the data
- Works well when the relationship between inputs and outputs is smooth

**Weaknesses:**
- Slow with large datasets (has to compare against *every* data point)
- Performs poorly in high-dimensional spaces (many input variables)
- Doesn't learn abstract patterns — just memorizes

**In this paper:** Used to predict optimal structure parameters and absorption/emission performance of metasurface daytime radiative coolers. Works best when design variables are few and well-defined.

---

### 2.2 Random Forest (RF)

**What it is in plain English:**
A Random Forest is a committee of many "decision trees" that each vote on the answer. Each tree is trained on a slightly different random subset of the data, and the final prediction is the average of all trees' votes.

**What is a Decision Tree?**
A decision tree is like a flowchart of yes/no questions:
- "Is the particle size > 500 nm?" → Yes → "Is the volume fraction > 10%?" → Yes → Predict high reflectance
- Each branch splits the data based on whichever feature most reduces prediction error.

**How Random Forest improves on a single tree:**
- A single tree tends to "overfit" — it memorizes quirks in the data.
- By building hundreds of trees on random subsets, the Random Forest smooths out those quirks.
- The final answer is the average across all trees, which is more reliable.

**Analogy:** You ask 100 friends to each guess the temperature tomorrow, but each friend only looks at a random 70% of the weather data. Their average guess is usually better than any single person's.

**Strengths:**
- Handles non-linear relationships well
- Provides feature importance (tells you which variables matter most)
- Resistant to overfitting
- Works with both continuous and categorical inputs

**Weaknesses:**
- Can be slow with extremely large datasets
- Less effective at capturing very complex, interleaved patterns compared to deep learning
- Not great at extrapolation (predicting outside the range of training data)

**In this paper:** Used for predicting absorption/emission performance of metasurface radiative coolers, and outperformed some other traditional models. Also used for scattering efficiency prediction of particles in passive radiative cooling.

---

### 2.3 XGBoost (eXtreme Gradient Boosting)

**What it is in plain English:**
XGBoost is a more sophisticated version of the decision tree idea, but instead of building trees independently (like Random Forest), it builds them *sequentially*. Each new tree focuses specifically on correcting the mistakes of all previous trees combined.

**How it works step by step:**
1. Build the first tree and make predictions.
2. Measure the errors (where predictions were wrong).
3. Build a second tree that specifically targets those errors.
4. Add the second tree's corrections to the first tree's predictions.
5. Repeat for hundreds of trees.
6. The final prediction is the sum of all trees' contributions.

**Analogy:** Imagine taking an exam, then reviewing only the questions you got wrong, studying just those topics, and retaking the exam. XGBoost does this hundreds of times.

**Strengths:**
- Often the best-performing traditional ML algorithm on structured/tabular data
- Very fast (optimized with parallelization)
- Built-in regularization to prevent overfitting
- Can handle missing values
- Provides feature importance scores (helps identify which material properties matter most)

**Weaknesses:**
- More hyperparameters to tune than simpler models
- Can overfit if the dataset is very small
- Like all tree-based methods, not ideal for learning from raw spectral curves

**In this paper:** Used for predicting thermal properties of radiative cooling aerogels, achieving higher accuracy than other models. Also used with model explanation tools (like SHAP) to identify which input factors most influence cooling performance — this dual use as both predictor and explainer is specifically highlighted.

---

## 3. Neural Network Models (Deep Learning)

Neural networks are inspired by how the brain works. They consist of layers of artificial "neurons" that transform input data through learned mathematical operations. The key advantage over traditional ML: they can automatically discover complex, non-obvious patterns — no need to manually select features.

### 3.1 Artificial Neural Network (ANN) — also called "Fully Connected Network" or "Multilayer Perceptron"

**What it is in plain English:**
An ANN is the most basic form of neural network. It's a stack of layers where every neuron in one layer is connected to every neuron in the next layer. Data flows from input to output, being transformed at each layer.

**Architecture:**
```
INPUT LAYER          HIDDEN LAYERS          OUTPUT LAYER
[particle size]  →  [neuron] [neuron]  →   [solar reflectance]
[layer thickness]→  [neuron] [neuron]  →   [IR emissivity]
[volume fraction]→  [neuron] [neuron]  →   [cooling power]
```

**How it works:**
1. Input features (e.g., particle size, thickness) enter the input layer.
2. Each neuron multiplies inputs by learned "weights," adds them up, and applies a non-linear function (like a dimmer switch that can amplify or diminish signals).
3. These transformed values pass to the next layer.
4. After several layers of transformation, the output layer produces predictions.
5. During training, the network compares its prediction to the true answer and adjusts all weights to reduce error (this is called "backpropagation").

**Analogy:** Like an assembly line where each worker takes the previous worker's product, modifies it slightly, and passes it forward. After thousands of practice runs, the assembly line learns to produce exactly what's needed.

**Strengths:**
- Can learn complex non-linear relationships
- Works well as a "surrogate model" — a fast approximation of expensive physics simulations
- Flexible: can handle multiple inputs and outputs simultaneously

**Weaknesses:**
- Needs more data than traditional ML to train well
- "Black box" — hard to understand *why* it made a specific prediction
- Requires careful tuning of architecture (how many layers, how many neurons)

**In this paper:** Used to predict long-term radiative cooling performance of windows under different climate conditions. Also used as a fundamental building block for surrogate models that replace expensive electromagnetic simulations (like FDTD or transfer matrix calculations).

---

### 3.2 Convolutional Neural Network (CNN)

**What it is in plain English:**
A CNN is a specialized neural network designed to detect local patterns in sequential or spatial data. Instead of connecting every neuron to every other neuron, it slides a small "window" (called a filter or kernel) across the data to detect features.

**Why it matters for spectral data:**
A reflectance/emissivity spectrum is fundamentally a 1D sequence: values at wavelength 0.3 μm, 0.4 μm, 0.5 μm, ..., 25 μm. Local features (like a sharp dip at 10 μm or a plateau from 8–13 μm) are critically important. CNN automatically learns to detect these local spectral patterns.

**How it works:**
```
INPUT SPECTRUM: [R(λ₁), R(λ₂), R(λ₃), ..., R(λₙ)]
                     ↓
CONV LAYER 1:  Slide small filters across spectrum → detect basic features
                (e.g., peaks, dips, slopes)
                     ↓
CONV LAYER 2:  Combine basic features → detect complex patterns
                (e.g., "high solar reflectance + atmospheric window emission")
                     ↓
FULLY CONNECTED: Map detected patterns → cooling performance predictions
```

**Analogy:** When you read text, your eyes don't process each letter independently — they slide across groups of letters to recognize words. CNN works the same way but with spectral data, recognizing "spectral words" (characteristic patterns).

**Strengths:**
- Excellent at detecting local patterns in sequential data (spectra)
- Parameter-efficient (filters are shared across the whole input)
- Can handle very high-dimensional spectral data
- Automatically learns which spectral features matter

**Weaknesses:**
- Needs more training data than traditional ML
- Less interpretable than simpler models
- Architecture design requires expertise

**In this paper:** Used for learning the mapping between complex spectral requirements and structural parameters in radiative cooling material design, particularly for inverse design tasks. CNNs extract meaningful features from high-dimensional spectral curves automatically.

---

### 3.3 DNN / Tandem Neural Network

**What it is in plain English:**
A tandem neural network is a special architecture designed specifically for inverse design problems. It chains together two networks: a forward one and an inverse one.

**The one-to-many problem:**
In forward design: one structure → one spectrum (unique answer). ✓
In inverse design: one target spectrum → MANY possible structures (ambiguous). ✗

This ambiguity makes training an inverse network directly very difficult — the network gets confused by contradictory training examples.

**How the tandem architecture solves this:**
```
TARGET SPECTRUM → [Inverse Network] → predicted structure → [Forward Network] → predicted spectrum
                                                                    ↓
                              Loss = difference between target spectrum and predicted spectrum
```

1. First, train a forward network (structure → spectrum) using simulation data.
2. Freeze the forward network's weights.
3. Chain an inverse network before it: target spectrum → structure → (frozen forward) → predicted spectrum.
4. Train only the inverse network, but measure error at the *spectral* output.
5. This way, the inverse network doesn't need to find THE "correct" structure — it just needs to find ANY structure that produces the target spectrum.

**Analogy:** Instead of asking "what recipe makes this exact cake?" (hard, many possible recipes), you ask "find me a recipe, and I'll test if the cake tastes right" (easier, just optimize taste).

**In this paper:** Used for colored daytime radiative coolers where both color fidelity and cooling performance must be satisfied simultaneously. The tandem architecture handles the inherent ambiguity of mapping from target properties to structural parameters.

---

### 3.4 Graph Neural Network (GNN) — Mentioned as Future Potential

**What it is in plain English:**
GNNs are neural networks that operate on data structured as graphs — networks of nodes and edges. They can represent complex, irregular structures like molecular bonds, atomic arrangements, or topology of nanoscale patterns.

**Why it's mentioned but not yet used:**
Most current radiative cooling structures can be described by a simple list of parameters (thickness, particle size, etc.). But future structures may have complex, irregular geometries (random porous networks, biomimetic patterns) that are best described as graphs rather than simple parameter lists. GNNs could handle these.

**In this paper:** Mentioned as a promising future direction for predicting properties of complex micro/nano radiative cooling structures with irregular topologies. Not yet applied in this field.

---

## 4. Optimization Algorithms

These aren't "learning" algorithms per se — they're *search* algorithms that find the best set of parameters within a given design space. The paper combines them with ML surrogate models: the ML model predicts performance quickly, and the optimizer uses those predictions to search for the best design.

### 4.1 Genetic Algorithm (GA)

**What it is in plain English:**
A Genetic Algorithm mimics biological evolution. It maintains a "population" of candidate solutions and evolves them over generations using selection, crossover, and mutation — survival of the fittest, but for engineering designs.

**How it works step by step:**
```
GENERATION 0: Random population of 100 candidate designs
              [Design A] [Design B] [Design C] ... [Design Z]
                  ↓
EVALUATE:     Calculate cooling performance of each design
                  ↓  
SELECT:       Pick the best performers as "parents"
                  ↓
CROSSOVER:    Combine features of two parents to create "offspring"
              Parent 1: [Material A, 50nm, 3 layers]
              Parent 2: [Material B, 80nm, 5 layers]
              Child:    [Material A, 80nm, 5 layers]  ← mix of both
                  ↓
MUTATE:       Randomly tweak some offspring (to explore new terrain)
              [Material A, 80nm, 5 layers] → [Material A, 85nm, 5 layers]
                  ↓
REPEAT for 100+ generations until convergence
```

**Key strength for this paper:** GA naturally handles DISCRETE variables. In multilayer film design, you need to choose from a fixed set of materials (SiO₂, TiO₂, Al₂O₃, etc.) AND optimize continuous variables (thickness). GA's binary/integer encoding handles both seamlessly.

**Variant mentioned: NSGA-II** — a multi-objective version of GA that finds a set of Pareto-optimal solutions (trade-off curve) rather than a single best answer. Useful when you need to balance solar reflectance vs. infrared emission vs. aesthetics simultaneously.

**Analogy:** Breeding dogs — you pick the fastest dogs and breed them together, occasionally getting random mutations that might make them even faster, until after many generations you have championship greyhounds.

**Strengths:**
- Handles mixed discrete + continuous variables naturally
- No gradient needed (works with black-box functions)
- Can find multiple good solutions (Pareto front)
- Robust against local optima traps

**Weaknesses:**
- Slow convergence with large populations
- Each generation requires evaluating many candidates (expensive if simulation is slow)
- Doesn't guarantee finding the global optimum

**In this paper:** The most commonly used optimizer for multilayer film design. Used to simultaneously optimize material type, layer count, layer thickness, and ordering. Often paired with transfer matrix method or a neural network surrogate model to evaluate candidates quickly.

---

### 4.2 Particle Swarm Optimization (PSO)

**What it is in plain English:**
PSO simulates a flock of birds searching for food. Each "particle" represents a candidate design, and particles communicate with each other about where good solutions are. They balance between exploring new areas and converging toward known good spots.

**How it works:**
```
INITIALIZE: Scatter 50 particles randomly in the design space
            Each particle has a position (design parameters) and velocity

FOR each iteration:
  Each particle knows:
    - Its own best position ever found (personal best)
    - The best position any particle has found (global best)
  
  Update velocity = inertia × current velocity
                  + attraction toward personal best
                  + attraction toward global best
  
  Move particle to new position
  Evaluate fitness at new position
  Update personal/global bests
```

**Analogy:** A flock of birds looking for a lake. Each bird remembers the wettest area it personally found AND knows the wettest area any bird found. They drift toward these good areas while still spreading out to explore.

**Key difference from GA:** PSO is naturally suited for CONTINUOUS variables (particle size, film thickness, period, fill fraction, etc.) because particles move through continuous space. It's less natural for discrete choices like "which material."

**Strengths:**
- Fast convergence for continuous parameter spaces
- Simple to implement (fewer parameters than GA)
- Works well when combined with neural network surrogate models
- Naturally parallelizable

**Weaknesses:**
- Poor at discrete variable optimization (material selection)
- Can get stuck in local optima in complex landscapes
- Performance drops in very high-dimensional spaces

**In this paper:** Used primarily for optimizing microstructure geometry (period, height, fill fraction) and particle-based systems (particle size, volume fraction, coating thickness). A specific highlighted workflow: FDTD simulation → Neural network surrogate → Adaptive PSO optimization, achieving R² = 0.99841 for atmospheric window emissivity prediction.

---

### 4.3 Bayesian Optimization (BO)

**What it is in plain English:**
Bayesian Optimization is the most sample-efficient optimizer — it's designed for situations where each evaluation is VERY expensive (e.g., a single FDTD simulation takes hours). Instead of testing thousands of candidates, it intelligently picks the *single next best candidate to test* based on what it's learned so far.

**How it works:**
```
STEP 1: Evaluate a few random designs (5-10)
STEP 2: Build a probabilistic surrogate model (usually Gaussian Process)
        that predicts BOTH the expected performance AND the uncertainty
STEP 3: Use an "acquisition function" to decide where to sample next:
        - Explore? (high uncertainty areas)
        - Exploit? (areas predicted to be good)
        Balance between both.
STEP 4: Evaluate the chosen design
STEP 5: Update the surrogate model
STEP 6: Repeat until budget is exhausted
```

**The key insight:** BO doesn't just predict "what's the best design" — it tracks its own *uncertainty*. If it's very uncertain about a region, that region might contain something great, so it's worth exploring. If it's confident a region is good, it exploits that knowledge.

**Analogy:** You're looking for the best restaurant in a city. Strategy 1 (GA/PSO): Try 500 random restaurants. Strategy 2 (BO): Try 5 random ones, then each time ask "given what I know, which restaurant would teach me the most or is most likely to be amazing?" — you find the best restaurant in maybe 20 tries.

**Strengths:**
- Extreme sample efficiency (finds good solutions with very few evaluations)
- Built-in uncertainty quantification
- Natural support for noisy evaluations (real experiments)
- Well-suited for expensive black-box optimization

**Weaknesses:**
- Struggles in very high-dimensional spaces (>20 variables)
- Sequential by nature — hard to parallelize
- Gaussian Process fitting itself becomes expensive with many observations

**In this paper:** The pioneering BO work in radiative cooling was by Guo et al. (2020), who combined RCWA simulation with BO and found optimal selective-emission structures using less than 1% of the candidate space. BO is specifically highlighted for colored radiative coolers where the "color + cooling" trade-off makes each candidate evaluation expensive and multi-objective.

---

## 5. Generative Models (Inverse Design)

These are the cutting-edge models that the paper identifies as the frontier. Instead of predicting performance from a design (forward) or searching through a design space (optimization), generative models directly CREATE new designs from target performance specifications.

### 5.1 Variational Autoencoder (VAE)

**What it is in plain English:**
A VAE learns to compress data into a compact "code" and then reconstruct it. Once trained, you can manipulate the code to generate new, never-before-seen designs that are physically plausible.

**How it works:**
```
ENCODING (learning to compress):
Design → [Encoder Network] → Compact latent code (e.g., 10 numbers)

DECODING (learning to reconstruct):
Compact latent code → [Decoder Network] → Reconstructed design

GENERATION (creating new designs):
Sample random point in latent space → [Decoder] → Brand new design!
```

**The magic:** The latent space is *organized* — nearby points produce similar designs. You can smoothly interpolate between two known good designs to find new intermediate designs. You can also sample in regions corresponding to high cooling performance.

**Analogy:** A VAE is like a fashion designer who studies thousands of dresses, learns the essence of what makes a dress (the latent code), and can then sketch new dresses by tweaking that essence — "more formal," "more red," "cooler fabric."

**Strengths:**
- Generates diverse new designs, not just the "single best"
- Smooth, organized latent space allows interpolation
- Can be conditioned on target properties (conditional VAE)
- Provides uncertainty through the probabilistic formulation

**Weaknesses:**
- Generated designs can be "blurry" (tend toward average)
- Quality usually lower than GANs
- Training can be tricky (balancing reconstruction vs. regularization)

**In this paper:** Mentioned as one of the key generative model approaches for radiative cooling inverse design, alongside GANs.

---

### 5.2 Generative Adversarial Network (GAN)

**What it is in plain English:**
A GAN consists of two neural networks that compete against each other: a Generator that creates fake designs, and a Discriminator that tries to tell fakes from real designs. Through this competition, the Generator gets better and better at producing realistic designs.

**How it works:**
```
TRAINING:
Random noise → [Generator] → Fake design
                                    ↓
Real training designs ─────→ [Discriminator] → "Real" or "Fake"?
                                    ↓
If Discriminator wins: Generator adjusts to make more convincing fakes
If Generator wins: Discriminator adjusts to better detect fakes

After thousands of rounds, the Generator produces designs 
indistinguishable from real (simulation-generated) data.
```

**Analogy:** A GAN is like an art forger (Generator) vs. an art detective (Discriminator). The forger keeps improving until even experts can't tell the forgeries from genuine paintings.

**For radiative cooling:** A conditional GAN (cGAN) can generate material structures conditioned on target spectral properties. You specify "I want 95% solar reflectance, 90% emissivity in 8-13 μm, and it should look blue" and the GAN generates structures that meet those targets.

**Strengths:**
- Generates very high-quality, realistic designs
- Can handle complex, multi-modal distributions
- Produces sharper outputs than VAEs
- Can incorporate physics constraints into the discriminator

**Weaknesses:**
- Training is notoriously unstable (mode collapse, oscillation)
- No guarantee of diversity in outputs
- Harder to evaluate quality systematically
- Doesn't provide uncertainty estimates

**In this paper:** Highlighted as a key frontier method for inverse design. Specifically relevant for colored/transparent radiative cooling films where the design space is highly multi-modal (many different structures can achieve similar performance).

---

### 5.3 Diffusion Models

**What it is in plain English:**
Diffusion models work by learning to reverse a destruction process. First, you gradually add noise to real data until it becomes pure static. Then you train a neural network to reverse this process — starting from pure noise and gradually denoising it into a valid design.

**How it works:**
```
FORWARD PROCESS (destruction):
Real design → add noise → add more noise → ... → pure random noise

REVERSE PROCESS (generation):
Pure random noise → [Learned denoiser] → slightly less noisy → ... → clean design
```

**Why they're exciting for materials design:**
- They produce extremely high-quality samples
- They're more stable to train than GANs
- They can be conditioned on target properties
- They naturally handle the diversity of possible solutions

**In this paper:** Mentioned as an emerging frontier alongside GANs and VAEs. Not yet widely applied in radiative cooling specifically, but already showing promise in nanophotonics and materials science more broadly.

---

### 5.4 Deep Reinforcement Learning (DRL / DQN)

**What it is in plain English:**
DRL treats the design process as a game. An "agent" takes sequential design actions (add this layer, change this thickness, pick this material) and receives rewards based on how close the resulting design is to the target performance. Through trial and error over thousands of "games," the agent learns an optimal design strategy.

**How it works:**
```
STATE: Current partial design (e.g., 3 layers placed so far)
ACTION: Add a layer of SiO₂ with thickness 150 nm
NEW STATE: Design with 4 layers
REWARD: Improvement in cooling performance

Agent learns: "In this situation, adding SiO₂ at ~150 nm usually leads to good outcomes"
```

**Analogy:** Like training a dog with treats. The agent (dog) takes actions (tricks), gets rewards (treats) for good performance, and gradually learns the best strategy.

**In this paper:** Referenced through Yu et al.'s "General deep learning framework for emissivity engineering" which used Deep Q-Network (DQN) for radiative cooling design. Also referenced through reinforcement learning-based inverse design of composite films for spacecraft thermal control. Positioned as a promising future direction that can handle sequential design decisions naturally.

---

## Quick Comparison Table

| Model | Type | Best For | Data Needed | Handles Spectra? | Can Do Inverse Design? |
|---|---|---|---|---|---|
| **KNN** | Traditional ML | Small datasets, simple screening | Small | Poor | No |
| **Random Forest** | Traditional ML | Medium complexity, feature importance | Small-Medium | Moderate | No |
| **XGBoost** | Traditional ML | Best tabular predictor, explainability | Medium | Moderate | No |
| **ANN** | Neural Network | General surrogate modeling | Medium-Large | Good | With tandem architecture |
| **CNN** | Neural Network | Spectral data, local patterns | Large | Excellent | As part of larger pipeline |
| **Tandem NN** | Neural Network | Inverse design with ambiguity | Large | Excellent | Yes — primary purpose |
| **GA** | Optimizer | Discrete + continuous mixed variables | N/A (uses evaluator) | N/A | Searches, not generates |
| **PSO** | Optimizer | Continuous parameter tuning | N/A (uses evaluator) | N/A | Searches, not generates |
| **BO** | Optimizer | Expensive evaluations, <20 variables | N/A (uses evaluator) | N/A | Searches, not generates |
| **VAE** | Generative | Diverse design generation | Large | Good | Yes |
| **GAN** | Generative | High-quality design generation | Large | Good | Yes |
| **Diffusion** | Generative | State-of-the-art generation quality | Very Large | Excellent | Yes |
| **DRL** | Generative/Optimizer | Sequential design decisions | Very Large | Via environment | Yes |

---

## How These Models Relate to Each Other in Practice

The paper's key insight is that these models aren't used in isolation — they form a **pipeline**:

```
STAGE 1: FORWARD PREDICTION (surrogate modeling)
         KNN / RF / XGBoost / ANN / CNN
         "Given this structure, what's its performance?"
              ↓
STAGE 2: OPTIMIZATION (finding the best within known space)
         GA / PSO / BO + Stage 1 surrogate
         "Within these bounds, what's optimally structured?"
              ↓
STAGE 3: INVERSE/GENERATIVE DESIGN (creating new designs from targets)
         Tandem NN / VAE / GAN / Diffusion / DRL
         "Given this target performance, generate structures that achieve it"
```

Each stage builds on the previous one, and the paper argues the field is progressively moving from Stage 1 → Stage 2 → Stage 3.
