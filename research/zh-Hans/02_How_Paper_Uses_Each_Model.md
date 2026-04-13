# 论文中每类模型是怎么被用起来的

这份中文整理把原文的核心结构保留下来：不是单纯介绍“有哪些模型”，而是说明这些模型在辐射制冷研究里分别被放在什么位置、解决什么问题，以及为什么它们往往会出现在一个分层 workflow 中。

## 三层框架先行

阅读相关论文时，最容易混淆的问题是：大家都说自己在做 ML for radiative cooling，但实际做的可能完全不是一类任务。更清楚的划分方式，是把它们分成三个 tier：

1. Tier 1：Forward Screening
2. Tier 2：Forward Optimization
3. Tier 3：Inverse / Generative Design

## Tier 1：Forward Screening

这一层的目标是“给结构，快速估计性能”。典型例子包括：

- 用 KNN 快速近邻筛查 metasurface 或粒子结构。
- 用 Random Forest 预测表现，并用 feature importance 看出哪些参数更关键。
- 用 XGBoost + SHAP 做“既预测又解释”的分析。
- 用 ANN 取代大量 electromagnetic simulation，快速输出 spectrum。
- 用 CNN 直接学习 1D spectral sequence，自动提取关键波段特征。

这层的意义在于速度。它不直接给出最终设计，但能把原本昂贵的模拟问题变成可大规模筛查的问题。

## Tier 2：Forward Optimization

这一层不是直接从目标反推结构，而是在给定 design space 内做更聪明的搜索。

### GA

GA 特别适合 multilayer film，因为材料是离散变量、厚度是连续变量，两者混合在一起时，GA 往往比单纯梯度法更自然。

### PSO

PSO 更适合那些主要由连续几何参数定义的问题，比如微结构周期、粒径、填充率等。它常被放在 surrogate model 后面，用来快速逼近最优解。

### BO

BO 的代表性价值在于：当单次评估特别贵时，依然能用很少的实验或仿真次数逼近优秀设计。Guo et al. (2020) 在 RC 里展示了这条路径的可行性。

## Tier 3：Inverse / Generative Design

这一层才是真正回答“我想要这样的 cooling target，应该设计出什么结构”的地方。

### Tandem NN

Tandem NN 是目前最清楚、最容易落地的一种方案。它用 forward net 去约束 inverse net，因此不会把问题粗暴地当成一一映射。

### GAN / VAE / Diffusion

这些 generative model 的共同点，是都接受“一个目标可能有很多解”这件事。差异在于：

- GAN 更强调样本分布与质量。
- VAE 更强调 latent space 的连续性和可探索性。
- Diffusion 更强调稳定训练与高质量生成。

### DRL / DQN

如果把结构设计过程理解为一连串动作，DRL 就能自然进入这个框架。例如逐层添加材料、设定厚度、更新 reward，再继续下一步。

## 结论：论文里的模型不是孤立出现的

真正重要的不是“某篇论文用了哪个模型”，而是它把模型放在了哪一层：

1. 是在做快速预测？
2. 是在做 constrained optimization？
3. 还是在做真正的 inverse / generative design？

把文献按 tier 来看，很多看似零散的工作就会变得非常清楚。也正因为如此，当前仓库采用的 retained workflow 并不是“训练一个模型就结束”，而是 generator、surrogate ranking 和 final verification 的组合。
