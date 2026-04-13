# 辐射制冷研究中常见的 ML 模型解释

这份中文版本保留了原文的技术骨架，但把说明改写成更适合快速阅读的形式。目标不是把所有术语翻成中文，而是帮助你在读到 KNN、Random Forest、XGBoost、ANN、CNN、GA、PSO、BO、VAE、GAN、Diffusion 和 DRL/DQN 时，立刻知道它们在辐射制冷里各自承担什么角色。

## 什么是 Machine Learning

在辐射制冷问题里，Machine Learning 通常承担三类任务：

1. 从结构预测性能，也就是前向预测。
2. 在给定约束下搜索更优结构，也就是优化。
3. 从目标性能反向生成结构，也就是 inverse design 或 generative design。

这三类任务看起来都叫“用 ML 做设计”，但它们的难点并不相同。前向预测更像 surrogate modeling，优化更像 intelligent search，而 inverse design 则要面对“一组目标可能对应很多结构”的 one-to-many 问题。

## 传统 ML：KNN、Random Forest、XGBoost

### KNN

KNN 的思想最直白：如果一个新结构和训练集里某些结构很像，那它们的光谱或冷却表现通常也会接近。它适合做快速近邻筛查，尤其是在结构表示已经比较稳定的时候。

### Random Forest

Random Forest 把很多 decision tree 的判断结果组合起来，因此对非线性关系更稳健。在辐射制冷语境里，它不仅能做预测，还能帮助研究者知道“哪个结构参数更重要”。

### XGBoost

XGBoost 擅长逐步纠错，常见优势是预测性能强、训练稳定、解释工具成熟。在相关文献里，它的价值不只是给出结果，还能配合 SHAP 说明为什么某些粒径、厚度或环境参数对 cooling response 更敏感。

## 神经网络：ANN、CNN、Tandem NN

### ANN / MLP

ANN 是最常见的前向 surrogate。它们把昂贵的电磁仿真替换成毫秒级近似器，因此非常适合在大规模搜索前做筛查。

### CNN

如果输入或输出具有一维序列结构，比如 reflectance / emissivity 光谱，CNN 就能直接学习局部波段模式，尤其适合抓住 solar band 和 atmospheric window 的局部特征。

### Tandem NN

Tandem NN 是 inverse design 里很重要的一类结构。它会把一个已训练好的 forward network 冻结下来，再用它去约束 inverse network 的输出。这样做的意义是：即便存在很多不同结构都能实现同一个目标，模型也不会只被表面重建误差牵着走。

## 优化算法：GA、PSO、BO

### GA

GA 很适合 mixed discrete + continuous 的问题。辐射制冷 multilayer 设计里，“材料选什么”通常是离散变量，“厚度多少”通常是连续变量，因此 GA 很自然。

### PSO

PSO 更偏向连续变量优化。当问题主要是几何尺寸、周期或填充率时，它往往收敛得更快。

### BO

BO 的优势是 sample efficiency。每次仿真都很贵时，BO 可以用很少的评估次数逼近好解。它不一定适合超高维问题，但对于 expensive evaluation 场景非常有价值。

## 生成式模型：VAE、GAN、Diffusion、DRL

### VAE

VAE 的重点是学习一个平滑、可插值的 latent space。对 inverse design 来说，这意味着你不仅能生成一个答案，还能系统地探索附近可能同样有效的结构。

### GAN

GAN 擅长逼近高质量样本分布。对于“很多结构都可能实现相近目标”的辐射制冷问题，它理论上很适合表达多模态解。

### Diffusion

Diffusion 的优点是训练更稳定、样本质量高，近几年在材料设计领域越来越常见。它的代价通常是采样链更长，但在高质量生成方面很有吸引力。

### DRL / DQN

如果把 multilayer 设计看成“逐层决策”的过程，DRL 就很自然：选择下一层材料、设定厚度、继续迭代，直到形成完整结构。这和真实沉积流程在逻辑上也更接近。

## 在辐射制冷项目里的三层结构

最实用的理解方式，是把这些模型放进一个三层 pipeline：

1. Tier 1：forward prediction，用 surrogate 快速估计结构表现。
2. Tier 2：optimization search，在约束条件下找更优候选。
3. Tier 3：inverse or generative design，从目标反推结构并生成候选池。

真正可落地的系统，通常不会只押注某一个模型，而是把这三层组合起来。当前仓库里的 continuous CVAE + surrogate shortlist + WPTherml verification，本质上就是这样一种组合式工作流。
