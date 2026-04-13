# 数据集、代码仓库与相近研究地图

这份中文版本保留了原文最重要的用途：它不是单纯的文献综述，而是一张“如果你现在就想开始做 radiative cooling + ML，应该从哪里下手”的资源地图。阅读它时，最该关注的是哪些工具能直接拿来用、哪些 paper 是方法论祖先、以及为什么目前几乎每个研究组都还在自己造数据集。

## Part A：开源代码仓库

原文把仓库分成几类：

1. 直接服务于 RC + ML 的仓库。
2. 属于 nanophotonics inverse design 的方法论仓库。
3. 可迁移到 RC 的 simulation 与 optimization 工具。

其中最核心的名字包括：

- WPTherml
- ScatterNet
- ColorRCMC
- Beamz
- DeltaRCWA.jl
- Ceviche
- Meep
- S4

这些项目并不都直接解决同一个问题，但它们共同组成了 RC-ML 工作流的技术底座。

## Part B：光学材料数据库

只做模型而不管 optical constants，在这个领域基本走不通。原文特别强调，refractiveindex.info 是最关键的公共输入来源之一，因为很多常见材料的 n(λ)、k(λ) 都要从这里拿。

此外，Materials Project、AFLOW、NOMAD、HITRAN、MODTRAN 等数据库也分别在材料属性、气体吸收、环境条件建模等方面起到支撑作用。

## Part C：相近研究论文

原文把文献分成三类看：

1. 与 ML + radiative cooling 直接交叉的核心论文。
2. 更广泛的 ML + materials design 方法论论文。
3. 近期虽未被原论文直接引用、但非常相关的新工作。

几篇尤其关键的代表包括：

- Peurifoy et al. (2018)
- Guan et al. (2023)
- Keawmuang et al. (2024)
- Guo et al. (2020)

这些文献的重要性不完全一样。有的定义了方法论祖先，有的展示了 colored / transparent RC 的多目标设计方向，有的则把 Bayesian Optimization 或 Tandem NN 带进了具体的 RC 场景。

## Part D：如何开始构建自己的数据

原文给出的现实建议非常明确：目前几乎没有 Kaggle 或 Zenodo 上现成、可直接拿来训练 inverse-design 模型的 RC 数据集。所以真正可行的开始方式，往往是：

1. 确定 design space。
2. 采样参数组合。
3. 用 WPTherml、TMM、FDTD 或 RCWA 生成 simulation corpus。
4. 再把这批数据交给 ML 模型训练。

这意味着“自己造数据”不是例外，而是当前领域的常态。

## Part E：最值得保留的观察

原文最后有几条非常重要的判断：

- 这个方向的高影响力论文大多集中在 2023–2025。
- colored / transparent radiative cooling 是非常热的分支。
- GitHub 上的可复用实现正在增加，但标准 benchmark 仍然缺位。
- Peurifoy 2018 依然像方法论祖先一样反复出现。
- Kaggle 风格的开放 RC-ML 数据集目前基本不存在。

## 结论

如果你想快速进入这个方向，不要先问“有没有现成大数据集”。更现实的问题是：

1. 我能不能先用 WPTherml 或相近 simulator 生成一套自己可控的数据？
2. 我手上的 design space 是否足够清晰？
3. 我准备把 ML 放在 forward prediction、optimization，还是 inverse design 这一层？

这张资源地图真正提供的，不是一个现成答案，而是一条可执行的起步路径。
