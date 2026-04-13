机器学习驱动的辐射制冷材料设计进展
全文主线是：
引言：辐射制冷基础→机器学习引入动因→按方法分类综述→典型材料案例→核心挑战与未来展望
0.引言：辐射制冷基础与技术背景
随着全球能源消耗持续增长和“双碳”目标不断推进的情况下，建筑环境调控[1-3]、电子器件散热[4-6]以及户外热管理[7-9]等领域对低能耗、可持续热管理技术的需求日益迫切。传统制冷方式大多依赖机械压缩循环，不仅运行能耗较高，而且伴随着制冷剂使用和碳排放增加等一系列环境问题。因此，开发能够充分利用自然冷源、减少主动供冷依赖的新型被动式供冷技术，已成为能源、材料与热科学交叉领域的重要研究方向。辐射制冷正是在这一背景下受到广泛关注的一类绿色降温技术，它通过物体与天空之间的辐射能量交换实现散热，具有无需持续外部供能、环境友好和理论上可长期运行等特点，因此被认为是被动式供冷领域中最具潜力的技术路线之一。
辐射制冷的物理基础在于地球大气对不同波长热辐射具有不同的吸收与透过特性。对于接近环境温度的物体而言，其主要热辐射集中于中红外波段，而大气在约8–13μm范围内存在相对较高透过率的“窗口”区域，使得该波段内的热辐射能够更有效地穿过大气并传递至冷外层空间，从而形成净散热通道。这一大气窗口的存在，为辐射制冷提供了明确的物理依据，也决定了辐射制冷材料设计必须围绕特定波段的光谱调控展开。然而，仅依赖大气窗口高发射并不足以保证白天条件下的冷却效果，因为太阳辐射主要集中于0.3–2.5μm波段，若材料在该波段吸收过强，则其获得的太阳热输入会抵消甚至超过红外辐射散热带来的冷却收益。因此，真正高性能的日间辐射制冷材料通常需要同时满足“太阳波段高反射、红外窗口高发射”的协同光谱选择性，而这种双重要求也使辐射制冷材料设计成为一个典型的多目标耦合问题[10]。
随着纳米光子学、微纳结构调控、聚合物复合材料和多层薄膜设计的发展，辐射制冷逐渐从夜间应用走向白天应用，从单纯机理研究拓展到高性能材料开发与多场景适配[11]。尤其是被动式日间辐射制冷的发展，使该领域不再局限于概念性降温，而是进一步走向建筑表面热管理、器件散热、柔性薄膜和功能化表面等更接近实际应用的方向[12]。与此同时，近年来的综述研究表明，辐射制冷已经从以材料和机理为中心的研究阶段，逐步转向更加重视性能测试、场景适用性与工程化应用的综合发展阶段[13-14]。
尽管如此，辐射制冷材料设计仍面临若干关键挑战。一方面，不同结构体系往往涉及折射率、粒径、体积分数、膜厚、层数、几何周期和拓扑形貌等大量设计变量，参数空间庞大且变量间耦合显著[15]；另一方面，辐射制冷性能不仅取决于单一光谱指标，而是与太阳反射率、中红外发射率、环境条件、热平衡过程及实际应用约束共同相关，这使得传统依赖经验试错、参数扫描和高成本数值仿真的设计方式逐渐显现出效率不足的问题。特别是在多目标协同优化、复杂结构设计以及功能集成型材料开发不断推进的背景下，如何更高效地建立“材料/结构—光谱—性能”之间的关系，并在高维设计空间中快速筛选和优化候选方案，已成为辐射制冷研究进一步发展的关键问题[16]。
基于上述背景，机器学习开始被越来越多地引入辐射制冷材料设计之中，并逐渐展现出在性能预测、参数优化和逆向设计等方面的独特优。围绕这一趋势，本文将系统综述机器学习在辐射制冷材料设计中的研究进展。具体而言，本文首先介绍机器学习引入辐射制冷设计的主要动因；在此基础上，由图1可知从材料性能预测方法、正演优化方法和逆向生成方法三个方面总结机器学习在辐射制冷中的主要应用；接着结合颗粒填充型聚合物、多层/叠层薄膜、彩色/透明辐射制冷薄膜以及微纳结构与超表面等典型体系，讨论机器学习驱动辐射制冷材料设计的代表性案例；最后，针对当前该领域在数据质量、模型泛化、物理约束融合及工程应用方面存在的问题，进一步总结其核心挑战并展望未来发展方向。
 
图1  机器学习辅助辐射制冷领域应用
Fig.1  Machine learning-assisted applications in the field of radiative cooling
（先写辐射制冷的研究背景与应用价值，介绍一下能源消耗、建筑降温、电子热管理、户外热舒适、可持续制冷等背景；然后在介绍一下大气窗口与辐射制冷的基本机理以及辐射制冷性能评价指标；然后可以简单一句话带过一下辐射制冷材料与典型结构概述，先给出后文会用到的结构分类如颗粒填充型聚合物、多层/叠层薄膜、彩色/透明辐射制冷膜与微纳结构与超表面这些）
相关文献插入：
1.Pisello A L. Implementation of passive radiative cooling technology in buildings: A review[J]. Buildings, 2020, 10(12): 215.
2.Li Y, Shi X, et al. Advances in radiative cooling materials for building energy efficiency[J]. Journal of Materials Chemistry A, 2024.
3.Wang Y, Liang Z, Shi S, Tang G, Peng Y. Radiative thermal management material for net-zero buildings[J]. Cell Reports Physical Science, 2025.
4.Liu H, Yang C, Wang R. Passive thermal management of electronic devices[J]. Device, 2024, 2: 100684.
5.Radiative cooling drives the integration and application of thermal management in flexible electronic devices[J]. npj Flexible Electronics, 2025.
6.Li L, Zhang Q, Liu G, et al. Advanced passive daytime radiative cooling: From material selection and structural design to application towards multifunctional integration[J]. Advanced Composites and Hybrid Materials, 2025.
7.Xue S, Huang G, Chen Q, Wang X, Fan J, Shou D. Personal thermal management by radiative cooling and heating[J]. Nano-Micro Letters, 2024, 16: 153.
8.Recent advancements in radiative cooling textiles for personal thermal management[J]. Journal of Materials Chemistry A, 2024.
9.Radiative cooling cellulose-based fabric with hierarchical structure for outdoor personal thermal management[J]. Chemical Engineering Journal, 2024.
10.Chen M, Pang D, Chen X, Yan H, Yang Y. Passive daytime radiative cooling: Fundamentals, material designs, and applications[J]. EcoMat, 2022, 4(1): e12153.
11.Zhai Y, Ma Y, David S N, Zhao D, Lou R, Tan G, Yang R, Yin X. Scalable-manufactured randomized glass-polymer hybrid metamaterial for daytime radiative cooling[J]. Science, 2017, 355(6329): 1062-1066.
12.Aili A, Jiang T, Chen J, Wen Y, Yang R, Yin X, Tan G. Passive daytime radiative cooling: Moving beyond materials towards real-world applications[J]. Next Energy, 2024, 3: 100121.
13.Feng K, Wu Y, Pei X, Zhou F. Passive daytime radiative cooling: From mechanism to materials and applications[J]. Materials Today Energy, 2024, 39: 101575.
14.Lee M, Kim G, Jung Y, et al. Photonic structures in radiative cooling[J]. Light: Science & Applications, 2023, 12: 134.
15.Yu X, Chan J W Y, Chen C. Review of radiative cooling materials: Performance evaluation and design approaches[J]. Nano Energy, 2021, 88: 106259.
16.Jung Y, Ko S H. Radiative cooling technology with artificial intelligence[J]. iScience, 2024, 27(12): 111325.
 
1.机器学习引入辐射制冷设计的动因
随着辐射制冷研究不断从基础机理验证走向高性能材料开发与真实场景应用，其设计问题也变得越来越复杂。当前辐射制冷体系已不再局限于简单均匀辐射表面，而是扩展到颗粒填充复合材料、多层/叠层薄膜、微纳周期结构、超表面以及兼具颜色或透明性的多功能结构等多种类型。与此相对应，设计变量也从早期相对单一的材料光学常数，扩展到粒径、体积分数、膜厚、层数、周期参数、单元形貌及拓扑构型等多个维度，使辐射制冷材料设计逐渐演变为典型的高维、多参数、强耦合问题。相关中文综述已经指出，机器学习辅助辐射特性调控的研究目前主要围绕“前向响应预测”和“逆向结构设计”两条主线展开，这实际上也说明，传统依赖有限经验和局部试错的设计路径已经越来越难以满足复杂辐射结构优化的需求。
从更一般的材料设计视角来看，当候选空间持续扩大时，传统高通量正向筛选方法虽然仍然有效，但其计算成本和搜索效率会迅速成为瓶颈。人工智能驱动材料设计相关综述指出，近年来材料设计范式正由单纯依靠经验与正向筛选，逐步转向面向目标性能的智能优化与逆向生成，其中深度学习、强化学习和生成模型正在推动材料设计流程发生结构性变化[17]。这种判断对于辐射制冷领域同样适用，因为辐射制冷设计不仅要面对庞大的结构空间，还必须处理太阳反射、中红外发射以及功能约束之间的复杂平衡关系。
对于辐射制冷而言，这种复杂性主要体现在三个方面。首先，辐射制冷性能不是由单一物理量决定，而是由太阳波段反射率、中红外发射率、大气窗口匹配程度、环境热交换条件以及应用场景约束共同决定，因此天然具有多目标优化特征。其次，许多辐射制冷结构还需要兼顾透明性、颜色、美观性、柔性或可制造性等附加要求，使设计任务进一步从“追求最高冷却性能”演化为“性能与功能协同优化”的综合问题。再次，辐射制冷性能评估通常依赖传输矩阵法、Mie 散射理论、严格耦合波分析、有限差分时域法等数值计算方法，这些方法虽然物理准确性较高，但在高维结构空间和大规模候选样本条件下往往计算成本昂贵。正因如此，越来越多研究开始将人工智能和机器学习方法引入辐射制冷设计，以提升结构搜索与性能优化效率[18]。
机器学习之所以能够被引入辐射制冷研究，首先是因为它具有显著的性能预测能力。在已有仿真或实验数据基础上，机器学习模型能够学习材料/结构参数与光谱响应、热学性能之间的映射关系，从而以代理模型替代大量重复的高成本数值仿真。这种“用数据驱动模型逼近高保真求解器”的思路，能够显著提高候选结构的评估效率。纳米光子学领域的经典研究已经证明，人工神经网络不仅可以实现对复杂粒子体系电磁响应的快速预测，还可以进一步用于逆向设计，这为辐射制冷中的结构性能预测提供了直接的方法学参照[19]。
除性能预测外，机器学习的第二个重要价值在于加速高维参数优化。传统设计流程中，即便已经能够计算某一候选结构的性能，如何在庞大参数空间中高效找到更优解仍然是一个困难问题。而当机器学习模型与贝叶斯优化、材料信息学优化或粒子群优化等智能搜索策略结合后，就可以构建“高保真仿真—代理模型—全局优化”的工作流，从而在减少评价次数的同时提高搜索效率。已有研究表明，贝叶斯优化特别适合求解评价代价高、无显式梯度且试验次数受限的黑箱优化问题；针对光学器件的多目标多保真优化研究进一步说明，数据驱动优化可以更有效地在多个性能指标之间取得平衡；而在辐射冷却结构设计中，材料信息学加速设计和粒子群优化方法也已开始显示出良好的适用性[20-23]。
更进一步地，机器学习的引入推动了辐射制冷设计从“正向筛选”向“逆向生成”转变。传统正向设计通常从结构参数出发，再逐步计算和筛选其性能，而逆向设计则从目标光谱或目标功能出发，反向生成满足要求的材料与结构方案。对于辐射制冷而言，这一点尤为重要，因为许多目标本身就带有明确约束，例如在特定颜色、透过率或多功能需求下仍保持高冷却性能，这类问题往往更适合通过逆向设计与生成模型求解。近年来，围绕可透色辐射制冷薄膜和高性能日间辐射制冷材料的研究已经表明，机器学习辅助逆向设计与深度生成模型在该领域具有明显潜力，能够突破传统依赖物理模拟和反复试错的设计路径[24-25]。
综上所述，机器学习被引入辐射制冷设计，并不是简单因为其“新”或“热门”，而是由辐射制冷问题本身的复杂性所决定的：其结构空间高维、目标函数多元、性能评估昂贵、应用约束丰富，传统方法已越来越难以满足高效设计需求。相比之下，机器学习在性能预测、优化搜索和逆向生成等方面展现出明显优势，因而逐渐成为辐射制冷研究从经验驱动走向数据驱动的重要支撑。基于这一认识，后文将进一步围绕机器学习在辐射制冷中的具体应用展开，从材料性能预测方法、正演优化方法和逆向生成方法三个层面系统梳理现有研究进展。

相关文献插入：
杜佳欣, 王富强, 张鑫平, 宋锦涛. 机器学习辅助辐射特性定向调控优化设计研究与应用综述[J]. 东北电力大学学报, 2024, 44(6): 63-73.
17.Cheng M, Fu C-L, Okabe R, Chotrattanapituk A, Boonkird A, Hung N T, Li M. Artificial intelligence-driven approaches for materials design and discovery[J]. Nature Materials, 2025.
18.Fu Z, Wang F, Cheng Z, Zhang Z. Recent advances in spectral radiative properties control with machine learning algorithm: Research methods and applications[J]. International Journal of Heat and Mass Transfer, 2026, 256: 128190.
19.Peurifoy J, Shen Y, Jing L, Yang Y, Cano-Renteria F, DeLacy B G, Tegmark M, Joannopoulos J D, Soljačić M. Nanophotonic particle simulation and inverse design using artificial neural networks[J]. Science Advances, 2018, 4(6): eaar4206.\\
20.Shahriari B, Swersky K, Wang Z, Adams R P, de Freitas N. Taking the human out of the loop: A review of Bayesian optimization[J]. Proceedings of the IEEE, 2016, 104(1): 148-175.
21.Leu P W, Chen J, Yao H, Zhao H, Pilania G. Multi-BOWS: multi-fidelity multi-objective Bayesian optimization with warm starts for optical device design[J]. Digital Discovery, 2024, 3(4): 913-922.
22.Guo J, Ju S, Shiomi J. Design of a highly selective radiative cooling structure accelerated by materials informatics[J]. Optics Letters, 2020, 45(2): 343-346.
23.Yan S, Liu Y, Wang Z, Lan X, Wang Y, Ren J. Designing radiative cooling metamaterials for passive thermal management by particle swarm optimization[J]. Chinese Physics B, 2023, 32(5): 057802.
24.Guan Q, Raza A, Mao S S, Vega L F, Zhang T. Machine Learning-Enabled Inverse Design of Radiative Cooling Film with On-Demand Transmissive Color[J]. ACS Photonics, 2023, 10(3): 715-726.
25.Le Q-T, Chang S-W, Chen B-Y, Phan H-A, Yang A-C, Ko F-H, Wang H-C, Chen N-Y, Chen H-L, Wan D, Lo Y-C. AI-enabled design of extraordinary daytime radiative cooling materials[J]. Solar Energy Materials and Solar Cells, 2024, 278: 113177.
 
2.按方法分类综述：机器学习在辐射制冷中的应用
2.1 数据驱动的正向筛选方法
数据驱动的正向筛选方向，主要是指在给定材料组成、结构参数或环境条件的前提下，利用机器学习模型快速预测候选材料或结构的光谱响应与冷却性能，从而在大量设计方案中高效筛选出更具潜力的对象。对于辐射制冷而言，这一方向具有明确的现实意义：一方面，太阳波段反射、中红外发射以及净冷却性能之间存在复杂耦合关系；另一方面，多层膜、颗粒复合材料和微纳结构等体系通常包含大量连续或离散设计变量，若完全依赖高保真电磁仿真逐一评估，不仅计算成本高，而且不利于大规模设计空间探索。因此，正向筛选的核心价值在于：先利用已有仿真或实验样本训练机器学习代理模型，再由代理模型代替部分高成本仿真，对未知结构进行快速性能预测与初步筛选，从而为后续优化和逆向设计提供基础[26-28]。
 
图2  数据驱动正向筛选流程示意图
Fig.2  Data-Driven Positive Screening Process Diagram
从模型类型来看，当前辐射制冷中的正向预测研究大体可以分为两类：一类是基于传统机器学习的材料性能预测方法，如K-nearest neighbor（KNN）、Random Forest（RF）和XGBoost等；另一类是基于神经网络的光谱与性能预测方法，如人工神经网络（ANN）和卷积神经网络（CNN）等。前者通常更适合处理中小规模样本、参数表达较清晰的预测任务，具有训练开销较低、部署方便和一定可解释性等优点；后者则更擅长学习复杂非线性关系和高维光谱特征，更适合处理变量耦合更强、光谱响应更复杂的辐射制冷问题[29]。

表2-1  正向筛选中不同模型的适用对象与特点比较
Tab.1  Comparison of Suitable Targets and Characteristics of Different Models in Positive Selection
 2.1.1 基于传统机器学习的材料性能预测
在辐射制冷材料设计中，传统机器学习模型最直接的用途是建立结构参数与冷却性能之间的快速映射关系，从而实现大规模候选结构的初步筛选。其输入通常包括粒径、膜厚、层数、周期参数、孔径分布或材料组成等结构特征，输出则包括太阳波段吸收/反射、中红外发射率、散射效率以及综合冷却性能等指标。由于这类问题往往具有较明确的参数化表达，KNN、RF和XGBoost等模型能够在不依赖超大样本规模的前提下提供较好的预测能力，因此成为辐射制冷正向筛选中最早落地的一类方法。
以KNN为代表的距离度量型方法，已经被直接用于日间辐射制冷超表面的结构参数与光谱性能预测。相关研究在超表面日间辐射冷却器中构建了机器学习设计框架，并采用K-nearest neighbor算法预测最优结构参数及其对应的吸收/发射性能，结果表明KNN在参数化清晰的冷却结构中能够实现较高预测精度和较好的模型稳定性。其基本思想是“结构参数相近的样本往往具有相似的光谱响应”，且已被用于构建结构参数与光谱性能之间的映射模型，并成功应用于仿生辐射制冷超材料的设计与优化[30]。因此对于变量定义明确、样本规模不大的辐射制冷体系，KNN可作为一种简单而有效的初步筛选工具。
随机森林更适合处理变量关系更复杂、非线性更强的辐射制冷预测问题。已有研究利用RF回归模型对超表面日间辐射冷却器进行预测与设计增强，结果显示RF在结构参数与吸收/发射性能映射方面表现出较高精度，并优于部分其他传统模型。除最终冷却性能外，传统机器学习还被用于被动日间辐射制冷材料的散射效率预测。相关研究表明，基于机器学习的模型能够较准确地预测 0.3–2.5μm波段的散射效率，这意味着正向筛选不仅可以服务于最终冷却效果预测，也可以用于中间光学特征的快速评估，从而为材料结构优化提供更细粒度的信息支持[31]。
XGBoost 及其他梯度提升类方法，则在辐射制冷材料热性能预测中显示出较强优势。针对辐射冷却气凝胶的研究构建了机器学习性能预测模型，并比较了多种算法的效果，结果表明优化后的XGBoost模型在测试集上具有更高的预测精度和更低误差，能够较准确地估计辐射冷却气凝胶的热性能。更重要的是，该研究还结合模型解释方法分析了不同输入因素对冷却效果的影响，这表明XGBoost不仅可以作为高效预测工具，还能帮助识别关键材料与环境变量[32]。
总体而言，传统机器学习方法在辐射制冷正向筛选中的优势主要体现在三个方面：其一，模型训练门槛相对较低，适合中小规模样本数据；其二，对参数化清晰的结构体系适配性较好，便于快速建立代理模型；其三，部分模型具有一定可解释性，有助于识别关键影响因素。但其局限也很明显，即对连续高维光谱的复杂模式学习能力有限，对极复杂结构或跨结构体系泛化能力相对不足。因此，当研究对象从“简单参数—单一性能”的映射进一步发展到“复杂光谱—多目标响应”的建模时，往往需要引入表达能力更强的神经网络方法。
 
图3. 辐射冷却设计中数据驱动前向筛选的典型传统机器学习策略：（a）KNN（b）随机森林（c）XGBoost。
Figure 3. Representative traditional machine-learning strategies for data-driven forward screening in radiative cooling design: (a) KNN (b)RF(c) XGBoost.
2.1.2 基于神经网络的光谱与性能预测
与传统机器学习相比，神经网络更适合处理高维、强非线性和复杂耦合的结构—性能映射问题。在辐射制冷研究中，材料的反射率、发射率以及净冷却功率往往由多个结构参数共同决定，不同波段之间还存在复杂关联，因此ANN、CNN等神经网络模型在处理这类问题时具有天然优势。它们能够通过多层非线性变换自动提取输入变量中的复杂特征，从而学习更抽象、更高阶的结构—光谱—性能关系。这使得神经网络不仅适合用作正向代理模型，也成为后续逆向设计和生成式设计的重要基础。
ANN是辐射制冷及相关光谱设计问题中最基础也最常见的神经网络模型之一。针对热带气候区辐射冷却窗体的研究构建了ANN模型，用于预测不同城市和不同气候条件下调节窗体红外发射率所带来的长期辐射冷却效果。结果表明，ANN能够较好地学习红外发射率设计与长期冷却性能之间的关系，从而为实际应用中的参数选择提供高效工具[33]。虽然这一问题偏向应用层面的热效应预测，但它清楚说明了：当输入变量与辐射冷却效果之间存在复杂非线性关系时，ANN可以作为传统仿真计算的重要补充，实现更快的性能估计。
从更一般的方法学角度来看，ANN在纳米光子学结构正向响应预测中的成功，也为辐射制冷研究提供了直接借鉴。经典研究表明，人工神经网络可以有效学习纳米粒子结构参数与电磁响应之间的关系，并在此基础上进一步支持逆向设计。这一方法学意义在于：辐射制冷本质上同样属于光谱调控问题，因此只要能够构建具有代表性的训练数据集，ANN就有潜力在辐射制冷结构中学习“几何参数—光谱响应—冷却性能”之间的复杂映射[34]。
相较于 ANN，CNN更擅长从序列或局部模式中自动提取特征，因此在光谱数据建模中具有独特优势。对于辐射制冷而言，反射率和发射率本身就是典型的波长序列数据，局部波段特征往往决定整体冷却表现，因此CNN特别适合处理这类问题。已有研究在辐射制冷材料设计中引入深度学习方法，用于学习复杂光谱需求与结构参数之间的映射，并进一步服务于逆向设计与候选结构生成。虽然该研究更偏向逆向生成设计，但其中CNN所承担的功能本质上就是从高维光谱或材料描述中自动提取有效特征，因此同样说明了CNN在辐射制冷正向建模中的可行性[35]。
此外，深度神经网络已经被用于彩色日间辐射冷却器的结构—性能关系学习。相关研究采用tandem neural network架构，在颜色与冷却性能并存的设计约束下建立深度神经网络模型，以实现复杂结构与目标响应之间的映射。因此，从正向筛选角度看，神经网络的引入并不只是意味着“更复杂的算法”，更代表着能够处理传统机器学习模型较难覆盖的复杂光谱特征、多目标耦合关系以及更高维的结构表达[36]。
需要说明的是，目前辐射制冷材料正向预测研究主要集中在KNN、RF、XGBoost、ANN和CNN等模型上。相比之下，GNN在辐射制冷材料预测中的直接应用报道仍较少，因此现阶段将其作为本领域已成熟的方法并不合适。不过，考虑到GNN在复杂材料拓扑表示、多尺度热学建模和图结构材料性质预测方面的潜力，未来其有望被进一步引入到复杂微纳辐射制冷结构的性能预测与设计中。总体来看，在数据驱动正向筛选中，传统机器学习更适合快速筛选和参数级预测，神经网络则更适合复杂光谱与高维结构响应建模，两者共同构成了辐射制冷数据驱动设计的第一层方法基础。
 
图4.  用于辐射冷却设计中光谱和冷却性能前向预测的典型神经网络策略:(a)ANN(b) CNN以及(c)DNN/串联神经网络。
Figure 4. Representative neural-network-based strategies for forward prediction of spectral and cooling performance in radiative cooling design: (a) ANN, (b) CNN, and (c) DNN/tandem neural network.
（首先介绍基于传统机器学习的性能预测，如KNN、RF、XGBoost等。在介绍基于神经网络的光谱与性能预测如ANN、CNN、GNN等。后面说明一下适用于辐射制冷的预测任务类型，如太阳反射率预测、红外发射率预测、制冷功率预测和平衡温度预测。最后小结指出这类方法最适合做快速筛选和代理评估。）
相关文献插入：
26.Nguyen B D, Potapenko P, Demirci A, Govind K, Bompas S, Sandfeld S. Efficient surrogate models for materials science simulations: Machine learning-based prediction of microstructure properties[J]. Machine Learning with Applications, 2024, 16: 100544.
27.Bhowmik R, Barabash R, Bazhirov T. Interpretable machine learning for materials design[J]. MRS Bulletin, 2023, 48(12): 1082-1090.
28.Nyshadham C, Rupp M, Bekker B, Shapeev A V, Mueller T, Rosenbrock C W, Csányi G, Wingate D W, Hart G L W. Machine-learned multi-system surrogate models for materials prediction[J]. npj Computational Materials, 2019, 5: 51.
29.Su W, Ding Z, Luo Y, Ye L, Wu H, Yao H. Machine learning-enabled design of metasurface based near-perfect daytime radiative cooler[J]. Solar Energy Materials and Solar Cells, 2023, 260: 112488.
30.Ding Z M, Li X, Ji Q X, Zhang Y C, Li H, Zhang H L, Pattelli L, Li Y, Xu H B, Zhao J P. Machine-learning-assisted design of a robust biomimetic radiative cooling metamaterial[J]. ACS Materials Letters, 2024.
31.Shi C, Zheng J Y, Wang Y, et al. Machine Learning-Driven Scattering Efficiency Prediction in Passive Daytime Radiative Cooling[J]. Atmosphere, 2025, 16(1): 95
32. Yuan C, Shi Y, Ba Z, Liang D, Wang J, Liu X, Xu Y, Liu J, Xu H. Machine Learning Models for Predicting Thermal Properties of Radiative Cooling Aerogels[J]. Gels, 2025, 11(1): 70.
33.Fei Y, Xu B, Chen X, Pei G. Optimization of infrared emissivity design for radiative cooling windows using artificial neural networks: Considering the diversity of climate and building features[J]. Renewable Energy, 2024: 121027. DOI: 10.1016/j.renene.2024.121027.
34.Malkiel I, Mrejen M, Nagler A, Arieli U, Wolf L, Suchowski H. Plasmonic nanostructure design and characterization via deep learning[J]. Light: Science & Applications, 2018, 7(1): 60.[1]
35.Kim M J, Kim J T, Hong M J, Park S W, Lee G J. Deep learning-assisted inverse design of nanoparticle-embedded radiative coolers[J]. Optics Express, 2024, 32(9): 16235-16247.
36.Li H, Chen Z, Jiang H, et al. Intelligent design of colored passive cooling multilayer films using bidirectional neural networks and genetic algorithms[J]. Progress in Organic Coatings, 2025, 199: 109018.
37.Keawmuang H, Badloe T, Lee C, Park J, Rho J. Inverse design of colored daytime radiative coolers using deep neural networks[J]. Solar Energy Materials and Solar Cells, 2024, 271: 112848.
________________________________________
2.2 正演优化方法
与2.1节侧重于“在已有候选中快速预测和筛选”的数据驱动正向筛选不同，正演优化方法更关注在已知参数化设计空间内主动搜索性能更优的材料组成与结构参数。换言之，2.1的核心是利用机器学习代理模型替代部分高成本仿真，以实现候选方案的快速评估；而2.2则是在此基础上进一步回答“在给定参数边界内，怎样找到更优解”这一问题。因此，正演优化不仅要求“算得快”，还要求“找得准”，其重点在于将代理模型、快速光谱计算与智能优化算法结合起来，在高维、多目标、强耦合的设计空间中提升全局寻优能力。对于辐射制冷而言，这一点尤为重要，因为材料性能往往需要在太阳波段高反射、大气窗口高发射、净制冷功率提升以及颜色、透过率、厚度和可制造性等附加约束之间取得平衡，这使得正演优化天然具有多目标协同优化的特征。已有研究和相关综述均表明，针对高成本黑箱问题，遗传算法、粒子群优化、贝叶斯优化等方法能够显著提高搜索效率，并逐渐成为机器学习辅助辐射制冷设计的重要组成部分4。
从一般流程上看，正演优化通常由三个环节构成：首先，利用传输矩阵法、FDTD、RCWA、Mie理论或蒙特卡洛方法等高保真模型构建“结构参数—光谱响应—冷却性能”数据集；其次，训练机器学习代理模型，或者借助快速光谱求解工具降低单次评价成本；最后，将代理模型或快速求解器与智能优化算法耦合，在参数空间内执行全局搜索。由于这种方法并不直接跳出既定结构范式，而是在明确变量空间内寻找最优方案，因此特别适用于多层/叠层薄膜、透明或彩色辐射冷却窗、颗粒填充型涂层以及参数化微纳结构等体系。Carne等1开发的FOS程序便是这一思路中的典型辅助工具，该程序将Mie理论、蒙特卡洛求解、并行计算以及预训练机器学习预测集成在同一框架中，可快速输出纳米颗粒介质的反射、吸收和透射光谱，从而为颗粒型辐射制冷材料的高通量参数搜索提供底层支撑。
贴图做一张三列对比图，图标用鸟群（PSO）、DNA螺旋（GA）、概率曲线图（BO）
2.2.1 基于遗传算法（GA）的参数优化
遗传算法（Genetic Algorithm，GA）是一类模拟自然选择和遗传进化机制的随机搜索算法，通过选择、交叉和变异等操作使种群不断进化，最终收敛到最优解2。与PSO主要适用于连续变量优化不同，GA在处理离散变量和混合整数优化问题方面具有天然优势，这使得它在多层薄膜和超表面辐射制冷结构的设计中应用尤为广泛——在这类问题中，设计变量不仅包括各层厚度等连续参数，还涉及材料类型的选择和层的排列顺序等离散变量，GA的二进制编码或整数编码方式能够自然地对这些离散选项进行表达和搜索。
在辐射制冷正演优化中，遗传算法是最常见的一类方法，如图展示了遗传算法优化设计辐射结构流程。我们发现尤其适用于多层膜系和混合离散—连续变量并存的设计问题，这是因为多层辐射制冷结构通常同时涉及材料种类、层数、层厚和排列顺序等多种变量，其中既包含连续参数，也包含离散选择，而GA能够通过选择、交叉和变异等操作对复杂组合空间进行全局搜索，因此在这类问题中表现出较好的鲁棒性和适配性。
 
You等1将遗传算法与传输矩阵法结合，提出了面向多层辐射制冷薄膜的灵活混合优化策略，并将辐射冷却功率密度直接纳入适应度函数，从而实现了膜层材料组合与厚度参数的协同寻优。该研究说明，GA不仅能够优化单一光谱指标，还可以直接面向综合热学目标进行搜索。随后，Kim等1针对多层日间辐射制冷结构开展优化分析，利用遗传算法同时处理层数、材料选择和厚度调节问题，进一步验证了GA在多层膜参数化设计中的有效性。Mira等1则在遗传搜索的基础上引入局部改进机制，采用模因算法优化多层选择性被动日间辐射制冷器，使结构在大气窗口内获得更高选择性发射，这表明将GA与局部精修结合有助于提高复杂膜系优化的收敛质量。
随着机器学习代理模型的引入，GA在辐射制冷中的作用进一步从“直接搜索”发展为“代理模型驱动的快速搜索”。有案列将机器学习与遗传算法结合，通过代理模型加速候选结构评估并由GA搜索最优膜层参数，形成典型的“代理模型+遗传优化”正演工作流；类似地，利用GA对堆叠式辐射冷却窗的层厚与周期进行优化可有效改善可见光透过率与近红外阻隔之间的平衡2。
2025年以来，遗传算法在辐射制冷多层膜与超表面设计中取得显著进展，代表性工作包括利用遗传算法优化透明彩色辐射冷却器中DMDMD多层膜的材料与厚度以实现高可见光透射率、高近红外反射率和大窗口高发射率的协同调控，以及通过遗传算法设计超表面集成多层太阳能反射器以将太阳波段透过率压至0.25%并最终获得91.87%太阳反射率与111.7 W/m²净冷却功率，此外在系统级优化层面遗传算法亦被证实可在不依赖代理模型时高效可靠地提升日间辐射天空冷却器性能，相关综述将其列为多层堆叠结构全局优化的核心算法之一4。由此可见，GA 特别适合用于参数边界清晰、层状结构明确、且需要同时处理性能与功能约束的辐射制冷体系。
综上所述，遗传算法在辐射制冷正演优化中的核心价值在于：第一，能够自然处理离散与连续混合的设计变量，特别适合多层膜的材料选择和厚度优化；第二，不需要目标函数的梯度信息，适用于黑箱性能评价；第三，易于扩展至多目标优化（如NSGA-II）。其局限性在于：种群规模较大时收敛速度较慢，且对于评价成本极高的电磁仿真问题，纯GA往往需要结合代理模型使用才能保持实用性。
2.2.2 基于粒子群优化（PSO）的连续参数寻优
粒子群优化（Particle Swarm Optimization，PSO）是一种模拟鸟群或鱼群集体觅食行为的群体智能优化算法，因其实现简单、收敛速度快、适合连续参数优化等特点，被广泛引入辐射制冷微结构的设计之中，如图所示。PSO的基本思想是在搜索空间中初始化一群粒子，每个粒子代表一组候选结构参数，粒子通过追踪自身历史最优位置和群体历史最优位置来不断更新自身位置，最终使群体收敛到全局最优解附近1。在辐射制冷设计中，PSO与机器学习代理模型相结合的优势尤为显著：代理模型可以在极短时间内预测任意候选结构的光谱响应或冷却性能，而PSO则利用这一快速评价能力在整个连续设计空间中进行高效搜索，二者协同工作，能够在显著减少昂贵电磁仿真次数的同时定位最优参数组合。与GA相比，粒子群优化更适合处理以连续变量为主的参数空间，例如微结构周期、占空比、高度、颗粒粒径、体积分数以及膜厚等。PSO 通过模拟粒子群体在解空间中的协同搜索过程，在参数数量较多但表达形式清晰的连续优化任务中具有收敛速度快、参数设置相对简单等优点，因此在辐射制冷微结构、超材料以及颗粒型体系中得到了较多应用。
 
Chae等1在无机多层选择性发射体设计中采用PSO优化层厚组合，获得了兼顾低太阳吸收和高大气窗口发射的辐射冷却结构，说明PSO在连续膜厚寻优问题中同样具有较好表现。2025—2026年间，刘博等1针对周期性四棱台辐射制冷微结构提出“FDTD仿真—神经网络代理—自适应粒子群优化”三级工作流，实现了大气窗口发射率高精度预测（R²=0.99841）与近单位平均发射率的最优参数锁定。PSO亦拓展至多目标协同优化，代理辅助PSO能以约2000次评估获得30变量问题的Pareto前沿近似，并在多层光栅辐射器（发射81.8%、净冷却功率118.17 W/m²）及Ag/Al₂O₃/Si₃N₄/SiO₂无机多层发射体4的优化制备中得到有效验证。
PSO的应用并不限于规则微结构，在颗粒填充和随机介质体系中同样表现出良好潜力。Bu 和 Bao1针对低厚度随机纳米颗粒涂层设计，利用PSO搜索颗粒参数和膜层厚度，以实现有限厚度条件下的高效辐射冷却。与规则多层膜相比，这类体系的光学行为更依赖统计散射与吸收竞争关系，因此单纯依赖经验调参往往效率较低，而 PSO 配合快速光谱求解器可以更高效地完成参数寻优。总体而言，PSO特别适合用于连续变量占主导、仿真代价较高且目标函数缺乏显式梯度的辐射制冷问题，尤其是在微结构、超表面与颗粒型材料设计中具有明显优势。
综上，机器学习结合粒子群优化的方法在辐射制冷材料设计中展现出以下优势：第一，适合连续参数空间的全局搜索，尤其适用于微结构几何参数和多层膜厚等连续变量的优化；第二，与神经网络代理模型结合后可极大降低FDTD等昂贵仿真的调用次数；第三，便于扩展至多目标优化场景。其局限性在于：PSO在高维离散变量（如材料种类选择）问题中的表现不如遗传算法，且对于评价成本极低的代理模型而言，PSO的迭代开销可能成为新的瓶颈。
2.2.3 基于贝叶斯优化（BO）的高样本效率搜索
贝叶斯优化（Bayesian Optimization，BO）是一种基于序列模型的全局优化策略，特别适用于评估代价高昂、无显式梯度且噪声较小的黑箱函数优化问题1，如图所示。当辐射制冷设计面临更高的仿真成本、更大的候选空间或更严格的样本预算限制时，贝叶斯优化显示出比传统启发式算法更高的样本效率。其核心思想并不是在整个空间内大量试探，而是通过概率代理模型或不确定性评估，在“探索未知区域”和“利用当前最优区域”之间动态平衡，从而尽可能用更少的评价次数逼近最优解。因此，这类方法尤其适合复杂多目标、评价昂贵的辐射制冷窗口和光子结构设计问题。
 
贝叶斯优化在辐射制冷领域的开创性工作由Guo等人于2020年完成，首次将RCWA仿真与BO结合，仅用不到1%的候选样本即锁定大气窗口内选择性高发射结构，奠定了方法论基础；后续该团队又将BO拓展至彩色辐射冷却器设计，以同等样本效率实现“颜色+冷却性能”多目标协同优化。此外，BO与FDTD结合已被用于VO₂相变多层板自动搜索，可在无需预设相变阈值下精确锁定最优几何参数2。Gunay和Shiomi 1将贝叶斯优化引入彩色兼容辐射制冷结构设计，对透射型与反射型彩色冷却器进行光子结构搜索，并在较小评估预算下识别出性能较优的设计方案，说明BO在“颜色—辐射冷却性能”这类多目标权衡问题中具有很强的应用潜力。与GA和PSO相比，BO的优势不在于处理超大规模迭代，而在于当单次评价昂贵时，能够更高效地决定“下一个最值得计算的样本”。这使其特别适合辐射制冷中那些依赖高保真电磁仿真、且每次计算成本较高的结构优化任务。
在更广泛的材料信息学视角下，贝叶斯优化与深度学习、量子计算一起被列为调控热辐射的关键算法进展。BO在辐射制冷中的适用性源于以下特点：第一，极高的样本效率，适合每次仿真成本高昂的场景；第二，天然支持噪声观测，能够稳健地处理实验测量中的不确定性；第三，提供不确定性量化，便于进行主动学习和自适应采样。然而，BO也面临一些局限：当设计空间维度超过20时，高斯过程的建模和采集函数的优化本身会变得困难，限制了其在极高维问题中的应用1；此外，BO是序列优化方法，难以像PSO或GA那样进行大规模并行搜索。
正演优化方法构成了数据驱动性能预测与实际辐射冷却材料设计之间的关键桥梁。与纯粹的正向筛选方法相比，这些方法主动引导搜索朝向高维设计空间中的最优或Pareto最优解，大幅减少了所需昂贵电磁仿真次数。基于PSO的方法在微结构几何和多层构型的连续参数优化中表现出色；基于GA的方法对于多层膜中材料选择和层序等离散及混合整数问题尤为有效；贝叶斯优化为昂贵黑箱评估提供了无与伦比的样本效率，通常在评估候选空间不足1%后即可识别最优设计。也正因为如此，正演优化可以被视为连接“前向预测”与“逆向生成”的关键中间层：它在方法上比2.1更强调搜索能力，但在设计哲学上仍建立在预设参数空间之内，这也为后续逆向生成方法的引入提供了自然过渡。
________________________________________
2.3 逆向生成方法（前沿热点）
逆向设计方法能够通过机器学习模型反向推算出满足特定性能要求的材料或结构参数，具有非常重要的实际应用价值。深度学习，尤其是生成对抗网络（GAN）和变分自编码器（VAE），被广泛应用于辐射制冷的逆向设计任务中，可以在多目标优化的框架下，设计出满足特定要求的冷却材料。
（首先写逆向设计的基本思想与研究价值，强调 inverse design 相比 forward search 的意义；然后介绍基于逆向神经网络的设计方法，如直接学习“性能→参数”；再介绍基于生成模型的候选结构生成，如 VAE、GAN、扩散模型等。接着可以介绍面向多目标需求的逆向生成设计是如何的，最后指出这一节是全文最前沿的部分。）
相关文献插入：
1．	Inverse design of colored daytime radiative coolers using deep neural networks（这篇很适合用来支撑“深度神经网络逆向设计”这一部分）

3. 机器学习驱动辐射制冷材料的典型案例
3.1 颗粒填充型聚合物辐射制冷材料
1.先介绍颗粒嵌入聚合物的基本光学机制；
2.再写关键设计变量：粒径、体积分数、膜厚、折射率等；
3.再说明为什么适合引入机器学习。
Optical properties of the polymeric radiative cooler with embedded nano/micro-particles（作为颗粒填充型体系的基础案例）
3.2 多层/叠层薄膜辐射制冷材料
1.先写多层膜依赖干涉效应和层间折射率对比；
2.关键变量：层数、层厚、材料组合、排列顺序；
3.强调其参数化程度高，非常适合 ML 建模与优化。
基于神经网络的多层薄膜结构红外辐射计算和逆向设计（作为多层薄膜体系中的神经网络案例）
3.3 彩色/透明辐射制冷薄膜
1.重点强调它是典型多目标设计问题；
2.要同时兼顾颜色/透光率/视觉功能与热管理性能；
3.最能体现逆向设计与生成设计的价值。
Machine Learning-Enabled Inverse Design of Radiative Cooling Film with On-Demand Transmissive Color（这篇就是本节最核心的主案例）
3.4 微纳结构与超表面辐射制冷材料
1.强调设计自由度高，但仿真成本也高；
2.关键变量：周期、占空比、高度、孔径、拓扑；
3.特别适合代理模型 + 智能优化。
Machine learning-enabled design of metasurface based near-perfect radiative cooling emitters
（这篇非常适合放在微纳结构/超表面这一节）
3.5 典型案例比较与启示
主要做横向总结。

4. 核心挑战与未来展望
4.1 核心挑战
尽管机器学习在辐射制冷领域取得了一定进展，但仍面临许多挑战，特别是在数据质量、模型泛化能力和实验验证等方面。以下是该领域的主要挑战：
当前，机器学习在辐射制冷中的应用面临数据稀缺的问题。尤其是高质量的实验数据和仿真数据尚不充分，且不同来源的数据存在域差异，这些问题影响了模型的训练和泛化能力。
深度学习等复杂模型虽然在特定任务中表现出色，但往往缺乏可解释性，这使得其在实际应用中的可信度和可靠性受到限制。此外，现有的模型通常在特定的数据集上表现良好，但在新的设计空间和材料系统中可能会出现过拟合或泛化能力差的问题。
4.2未来展望
随着计算资源和数据的不断积累，机器学习在辐射制冷领域的应用将更加广泛，尤其是在逆向设计、多目标优化和高效仿真加速等方面。未来的研究可以进一步探索自适应优化和闭环设计，通过机器学习与实验的紧密结合，实现从设计到验证的自动化闭环。
发展方向上，随着高效数据生成方法、自动化实验平台和物理约束融合技术的发展，机器学习将在辐射制冷设计中发挥更大的作用，特别是在多目标设计和生成模型方面。借助先进的生成模型和深度强化学习技术，辐射制冷材料的设计将更加智能化，突破传统设计方法的局限，开辟新的研究路径。
本章主要引用文献:
Artificial intelligence-driven approaches for materials design and discovery(这一篇最适合放在第五章，适合支撑对“从正向筛选到逆向生成”“生成模型的潜力与挑战”“闭环与未来平台化趋势”的讨论。)
AI-enabled design of extraordinary daytime radiative cooling materials(这篇可以放在“未来展望”部分，用来体现生成式方法已经开始进入辐射制冷材料设计。)
