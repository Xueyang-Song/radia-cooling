# 面向辐射制冷的 Generative AI 方案

这份中文版本保留了原文最重要的判断：Generative AI 对辐射制冷最有价值的地方，不是“更炫”，而是它能把问题从“人类提出结构，再去模拟”改写成“先给出目标，再生成结构候选”。真正的难点在于，这条路必须始终接受 physics constraint，而不能只追求表面上的生成能力。

## 核心问题：从正向试错，转向目标驱动生成

传统 workflow 更像：

1. 人提出一个结构。
2. 跑 simulation。
3. 看结果是否满足 cooling target。

Generative AI 试图把这个顺序倒过来：

1. 先设定 target。
2. 再由模型生成一批候选结构。
3. 用 ranking 和 verification 去选出可信解。

这件事之所以困难，是因为 inverse design 天然存在 one-to-many：同一个目标性能，往往对应许多不同结构。

## Tandem Neural Network：当前最稳妥的起点

Tandem NN 的意义在于，它不是把 inverse problem 当成“直接回归一个唯一答案”，而是用一个冻结的 forward network 去验证 inverse network 的输出是否真的达标。这是当前最容易落地、也最容易被研究者接受的一条路径。

## GAN、VAE、Diffusion：为什么它们值得进入辐射制冷

### GAN

GAN 适合表达多模态解，也就是“一组目标可能对应很多不同但都成立的结构”。它的价值在于分布建模，而不是单点预测。

### VAE

VAE 的优势在于可组织的 latent space。它不仅能生成候选，还能在 latent 空间里做平滑插值、局部探索，以及不确定性相关分析。

### Diffusion

Diffusion 是近几年材料生成里非常重要的方向。它训练稳定、样本质量高，适合作为高质量生成器，但也往往伴随着更高的采样成本。

## DRL：把 multilayer 设计看成逐步决策

如果把构造 multilayer 结构看成一连串动作，比如“选下一层材料”“设定厚度”“更新 reward”，那么 DRL 就天然适合这个问题。它与真实制造过程之间也存在更直接的语义对应。

## 关键限制：physics 不能被绕开

Generative AI 在 RC 场景里绝不能只做纯数据驱动生成。无论是 GAN、VAE、Diffusion 还是 DRL，最终都必须满足：

- Maxwell's Equations
- 能量守恒
- fabrication constraints
- 可被 simulator 或实验闭环再次确认

因此，最可信的生成式 workflow 不是“生成完就结束”，而是“生成 → shortlist → verification”。

## 当前仓库已经走到哪里

截至 2026 年 4 月，本仓库已经不是空想状态，而是有一条真实跑通的路线：

1. continuous CVAE 作为 candidate generator。
2. surrogate model 负责 ranking。
3. top-16 shortlist 再交给 WPTherml 做 final verification。
4. 在 sample255 类目标上，total absolute error 已降到约 0.0946。

## 本地天花板与下一步

原文最值得保留的判断是：当前这条模型家族在现有 4096 样本规模下，已经接近本地天花板。继续微调超参数，不太可能带来质变。下一步更值得投入的方向是：

1. 明显扩大模拟数据规模。
2. 引入实验反馈，形成真实 closed-loop。
3. 更换真正不同的算法成分，而不是再做小修补。
4. 扩展 design space，而不是一直停留在 5-layer dielectric stack 上。

Generative AI 的价值，并不是让设计“更自动”，而是让 research loop 变得更像一个真正可迭代、可验证、可扩展的系统。
