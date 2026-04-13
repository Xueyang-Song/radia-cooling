from __future__ import annotations

from copy import deepcopy
import re
from pathlib import Path


SUPPORTED_LOCALES = ("en", "zh-Hans")


SITE_TRANSLATIONS_ZH = {
    "Radiative Cooling, explained": "辐射制冷，讲清楚",
    "A guided web story for a real ML design project": "一个面向真实 ML 设计项目的引导式网页故事",
    "This app turns a dense radiative-cooling ML workflow into a guided walkthrough. It uses the real local research notes, real dataset outputs, and real model-verification artifacts from the project so you can see what was tried, what the data looked like, and why one workflow was retained over the others.": "这个应用把原本密集难读的辐射制冷 ML 工作流拆解成可跟随的导览。它直接使用项目里的真实本地研究笔记、真实数据集输出和真实模型验证工件，让你看到究竟试了什么、数据长什么样，以及为什么最后保留的是这条工作流。",
    "The retained best workflow is a continuous-decoder CVAE trained on 4096 real WPTherml samples, followed by 256 candidate samples, a surrogate top-16 shortlist, and final WPTherml verification.": "当前保留的最佳工作流是：在 4096 条真实 WPTherml 样本上训练 continuous-decoder CVAE，然后为每个目标采样 256 个候选，用 surrogate 选出前 16 名，再交给 WPTherml 做最终验证。",
    "Real samples": "真实样本",
    "Generated from the open WPTherml thin-film simulator.": "由开源 WPTherml 薄膜模拟器生成。",
    "Wavelength points": "波长点",
    "Every real spectrum spans 0.3 to 25.0 um.": "每条真实光谱都覆盖 0.3 到 25.0 μm。",
    "Papers reviewed": "已审阅论文",
    "External papers studied while building the project story and audit.": "是在构建项目叙事与审计过程中实际研读的外部论文。",
    "Best verified error": "最佳验证误差",
    "Smallest curated target error among the retained reference runs.": "保留参考实验中最小的精选目标误差。",
    "Why the project exists": "为什么要做这个项目",
    "Radiative cooling research is powerful but hard to read if you are not already fluent in optics, ML, and materials science.": "辐射制冷研究很有价值，但如果你不熟悉 optics、ML 和 materials science，就很难读懂。",
    "The app is designed to unpack the whole workflow in plain language while still staying anchored to the real artifacts.": "这个应用的目标，是用直白语言拆解整个工作流，同时始终锚定真实工件。",
    "What the data really is": "数据到底是什么",
    "The main dataset is not a toy spreadsheet. It is a real, reproducible WPTherml simulation corpus for 5-layer dielectric stacks over silver.": "主数据集不是玩具表格，而是一套真实、可复现的 WPTherml 模拟语料，描述的是银反射层之上的 5 层 dielectric stack。",
    "Each sample includes structure details and two full spectra with 256 wavelength points.": "每个样本都包含结构细节，以及两条各有 256 个波长点的完整光谱。",
    "What the trained loop means": "训练后的闭环意味着什么",
    "The project did not stop at training a model. It used a multi-step loop: generate candidates, rank them, then check them again with the physics simulator.": "项目并没有止步于训练一个模型，而是采用多步闭环：生成候选、排序筛选，然后再用 physics simulator 复核。",
    "That final verification step is why the retained result is trustworthy.": "最后那一步验证，就是保留结果可信的原因。",
    "How the final answer was reached": "最终结论是如何得出的",
    "Several branches were tested and compared, including diffusion, tandem, and an audited categorical CVAE branch.": "项目测试并比较了多条分支，包括 diffusion、tandem，以及经过审计的 categorical CVAE 分支。",
    "The continuous-CVAE shortlist workflow stayed on top after the final audit.": "在最终审计之后，continuous-CVAE 的 shortlist 工作流仍然保持领先。",
    "Cooling floor": "低冷却端样本",
    "A real sample near the bottom of the cooling range.": "一个位于冷却能力区间底部附近的真实样本。",
    "Middle of the pack": "中位样本",
    "A real sample near the center of the training distribution.": "一个位于训练分布中心附近的真实样本。",
    "Cooling peak": "高冷却端样本",
    "A real sample near the best cooling proxy in the dataset.": "一个接近数据集中最佳 cooling proxy 的真实样本。",
    "Thin stack": "薄层堆样本",
    "A real sample with unusually low total thickness.": "一个总厚度异常偏低的真实样本。",
    "Window emitter": "窗口发射样本",
    "A real sample with very strong 8-13 um emissivity.": "一个在 8-13 μm 波段具有很强 emissivity 的真实样本。",
    "Continuous winner / sample255": "Continuous 优胜者 / sample255",
    "This retained winner came from the 256-candidate shortlist loop.": "这个保留优胜者来自 256 候选的 shortlist 闭环。",
    "Continuous raw / sample255": "Continuous 原始结果 / sample255",
    "Useful candidate generator, but not the final winner once shortlist verification was added.": "它是有用的候选生成器，但在加入 shortlist 验证后就不再是最终优胜者。",
    "Continuous winner / sample777": "Continuous 优胜者 / sample777",
    "Second reference target that confirmed the retained workflow was not a one-off.": "第二个参考目标，用来确认保留工作流并非一次性偶然命中。",
    "Diffusion raw / sample255": "Diffusion 原始结果 / sample255",
    "Competitive generator, but it did not beat the retained continuous-CVAE shortlist workflow.": "它是有竞争力的生成器，但没有超过保留的 continuous-CVAE shortlist 工作流。",
    "Tandem proposal / sample255": "Tandem 提案 / sample255",
    "Deterministic baseline that produces one structure instead of a sampled pool.": "这是一个确定性 baseline，每个目标只给出一个结构，而不是一个采样候选池。",
    "Categorical raw / sample255": "Categorical 原始结果 / sample255",
    "Audit branch tested after the soft-to-hard material mismatch was identified.": "这是在发现 soft-to-hard 材料失配后专门测试的审计分支。",
    "Categorical shortlist / sample255": "Categorical shortlist / sample255",
    "The shortlist did not rescue this branch on the sample255 target.": "在 sample255 目标上，shortlist 也没能救回这条分支。",
    "Categorical raw / sample777": "Categorical 原始结果 / sample777",
    "Raw best-of-64 sample on the second reference target.": "第二个参考目标上的原始 best-of-64 结果。",
    "Categorical shortlist / sample777": "Categorical shortlist / sample777",
    "The better of the two categorical results for the sample777 target, but still far behind the retained baseline.": "这是 sample777 目标上两个 categorical 结果中较好的那个，但仍远远落后于保留 baseline。",
    "Lock the design space": "锁定设计空间",
    "The project needed a clear, reproducible structure family before any model could be trained.": "在训练任何模型之前，项目必须先定义清晰且可复现的结构族。",
    "5 dielectric layers": "5 层 dielectric",
    "Material pool: SiO2, TiO2, HfO2, Al2O3, Si3N4": "材料池：SiO2、TiO2、HfO2、Al2O3、Si3N4",
    "Thickness bounds: 40-500 nm": "厚度范围：40-500 nm",
    "A fixed multilayer thin-film search space": "固定的多层薄膜搜索空间",
    "Consistent wavelength bands and target metrics": "一致的波段设置与目标指标",
    "Design-space YAML": "设计空间 YAML",
    "Generated manifest": "生成的 manifest",
    "Generate the real dataset": "生成真实数据集",
    "There is no standard public benchmark for this exact inverse-design problem, so the project had to generate a reproducible local corpus.": "针对这个逆向设计问题并不存在标准公开基准，因此项目必须自己生成一套可复现的本地语料。",
    "Open WPTherml backend": "开源 WPTherml 后端",
    "Randomized legal structures": "随机化的合法结构",
    "256 wavelength points per spectrum": "每条光谱 256 个波长点",
    "4096 real records": "4096 条真实记录",
    "Reflectance spectra": "Reflectance 光谱",
    "Emissivity spectra": "Emissivity 光谱",
    "Dataset records preview": "数据集记录预览",
    "Reflectance array summary": "Reflectance 数组摘要",
    "Emissivity array summary": "Emissivity 数组摘要",
    "Train forward surrogates": "训练 forward surrogate",
    "Fast forward models make it possible to score many candidate structures without calling the full simulator every time.": "快速的 forward model 让我们可以为大量候选结构打分，而不必每次都调用完整 simulator。",
    "Real training corpus": "真实训练语料",
    "Holdout thickness-tail split": "holdout thickness-tail 划分",
    "Two spectral tasks: reflectance and emissivity": "两个光谱任务：reflectance 和 emissivity",
    "Torch reflectance surrogate": "Torch reflectance surrogate",
    "Torch emissivity surrogate": "Torch emissivity surrogate",
    "Reflectance surrogate metrics": "Reflectance surrogate 指标",
    "Emissivity surrogate metrics": "Emissivity surrogate 指标",
    "Train inverse and generative models": "训练 inverse 与 generative 模型",
    "Different model families answer different questions: deterministic inverse, candidate generation, or stochastic search over many valid designs.": "不同模型家族解决的问题不同：有的做确定性逆向预测，有的生成候选，还有的在大量合法设计中做随机搜索。",
    "Tandem inverse model": "Tandem inverse model",
    "Continuous CVAE": "Continuous CVAE",
    "Conditional diffusion": "Conditional diffusion",
    "Categorical audit branch": "Categorical 审计分支",
    "Single proposals": "单个提案",
    "Candidate pools": "候选池",
    "Metrics for apples-to-apples comparison": "用于公平对比的指标",
    "Tandem metrics": "Tandem 指标",
    "Continuous CVAE metrics": "Continuous CVAE 指标",
    "Diffusion metrics": "Diffusion 指标",
    "Categorical audit metrics": "Categorical 审计指标",
    "Rank and shortlist candidates": "排序并筛选候选",
    "The best workflow did not trust a raw generator blindly. It scored a large pool, trimmed it, and only then spent physics budget on verification.": "最佳工作流并不会盲目信任原始生成器。它先为大规模候选池打分，再做裁剪，最后才把 physics 预算花在验证上。",
    "256 generated candidates": "256 个生成候选",
    "Surrogate ranking": "surrogate 排名",
    "Top-16 shortlist": "前 16 shortlist",
    "Compact high-value candidate set": "紧凑而高价值的候选集合",
    "Much lower verification cost": "显著更低的验证成本",
    "Continuous shortlist": "Continuous shortlist",
    "Categorical shortlist": "Categorical shortlist",
    "Re-check with WPTherml": "用 WPTherml 复核",
    "This is the truth step. It is what turns an ML guess into an evidence-backed result.": "这是求真的一步。它把 ML 的猜测，变成有证据支撑的结果。",
    "Top shortlist candidates": "shortlist 顶部候选",
    "Original physics simulator": "原始 physics simulator",
    "Target metrics": "目标指标",
    "Verified absolute errors": "已验证的绝对误差",
    "Final retained winner and rejected branches": "最终保留的优胜者与被否决的分支",
    "Continuous verified finalists": "Continuous 已验证入围结果",
    "Categorical verified finalists": "Categorical 已验证入围结果",
    "Continuous CVAE shortlist loop": "Continuous CVAE shortlist 闭环",
    "Train on the 4096-sample real corpus, sample 256 candidates, shortlist the best 16 with the surrogates, then re-check those finalists with WPTherml.": "在 4096 条真实语料上训练，生成 256 个候选，用 surrogate 选出前 16 名，再把这些入围结果交给 WPTherml 复核。",
    "Train on 4096 real WPTherml samples": "在 4096 条真实 WPTherml 样本上训练",
    "Sample 256 candidate stacks for each target": "为每个目标采样 256 个候选层堆",
    "Score them with the forward surrogates": "使用 forward surrogate 为它们打分",
    "Re-run the top 16 through WPTherml": "把前 16 名重新交给 WPTherml",
    "Deterministic inverse": "确定性逆向设计",
    "Useful as a direct structure-from-target baseline. It predicts one structure per target instead of a diverse pool.": "它是一个直接从目标到结构的 baseline。与生成多样候选池不同，它每个目标只预测一个结构。",
    "Generative shortlist winner": "生成式 shortlist 优胜者",
    "The best generator after full verification. Its real strength comes from sampling many candidates and then letting the shortlist plus physics loop sort them.": "在完整验证后表现最好的生成器。它真正的优势在于先采样大量候选，再让 shortlist 加 physics 闭环来完成筛选。",
    "Generative competitor": "生成式竞争者",
    "A serious alternative generator that stayed in the same performance neighborhood as raw CVAE sampling, but never passed the retained shortlist workflow.": "这是一个严肃的替代生成器，性能与原始 CVAE 采样处在同一量级，但始终没有超过保留的 shortlist 工作流。",
    "Rejected audit experiment": "被否决的审计实验",
    "Added after the audit spotted a soft-to-hard material mismatch. The branch trained cleanly but failed under final physics verification.": "这是在审计发现 soft-to-hard 材料失配后加入的分支。它训练过程正常，但在最终 physics 验证中失败了。",
    "Reference target A": "参考目标 A",
    "The high-cooling sample255-like target used throughout the shortlist experiments.": "在 shortlist 实验中反复使用的高冷却 sample255 类目标。",
    "Continuous CVAE shortlist": "Continuous CVAE shortlist",
    "Continuous CVAE raw best-of-64": "Continuous CVAE 原始 best-of-64",
    "Diffusion raw best-of-64": "Diffusion 原始 best-of-64",
    "Tandem single proposal": "Tandem 单个提案",
    "Categorical CVAE raw best-of-64": "Categorical CVAE 原始 best-of-64",
    "Categorical CVAE shortlist": "Categorical CVAE shortlist",
    "Reference target B": "参考目标 B",
    "The second curated target used to check whether the best workflow generalized beyond a single story point.": "第二个精选目标，用来检查最佳工作流是否能泛化到单一案例之外。",
    "A reproducible real dataset replaced hand-wavy examples": "可复现的真实数据集取代了含糊示例",
    "The project settled on a 4096-sample WPTherml corpus so every later claim could point back to concrete structures and spectra.": "项目最终选定 4096 条 WPTherml 语料，这样后续每个判断都能回指具体结构与光谱。",
    "Dataset manifest": "数据集 manifest",
    "Forward surrogates made ranking practical": "forward surrogate 让排序变得可行",
    "Separate reflectance and emissivity surrogates were trained to score many candidate stacks quickly before spending full physics budget.": "项目分别训练了 reflectance 和 emissivity surrogate，在投入完整 physics 预算前先快速给大量候选层堆打分。",
    "The workflow expanded from single predictions to candidate pools": "工作流从单次预测扩展到了候选池",
    "Tandem, continuous CVAE, and diffusion all entered the stack, but the best results came from a generator plus shortlist plus verification loop.": "Tandem、continuous CVAE 和 diffusion 都被纳入了流程，但最佳结果来自“生成器 + shortlist + 验证”的闭环。",
    "Shortlisting changed the leaderboard": "shortlist 改写了排行榜",
    "The turning point was not just a better generator. It was the 256-candidate pool plus top-16 verification strategy that cut the sample255 error to about 0.0946.": "真正的转折点不只是更好的生成器，而是“256 候选池 + 前 16 验证”的策略，把 sample255 的误差压到了约 0.0946。",
    "Retained sample255 verification": "保留的 sample255 验证结果",
    "The final audit checked the data, the environment, and the main open modeling concern": "最终审计检查了数据、环境以及最关键的建模疑点",
    "The audit confirmed the dataset was clean, fixed the Python environment to use the RTX 3080, and tested an explicit categorical-material decoder branch.": "审计确认数据集是干净的，把 Python 环境修正为使用 RTX 3080，并测试了一个显式的 categorical-material decoder 分支。",
    "Final audit report": "最终审计报告",
    "The categorical decoder stayed rejected": "categorical decoder 仍被否决",
    "Even after retraining on CUDA, the categorical branch stayed far behind the retained continuous-CVAE shortlist workflow on both reference targets.": "即使在 CUDA 上重新训练后，categorical 分支在两个参考目标上仍远落后于保留的 continuous-CVAE shortlist 工作流。",
    "Categorical sample255 verification": "Categorical sample255 验证结果",
    "Categorical sample777 verification": "Categorical sample777 验证结果",
    "Passive cooling by reflecting sunlight and sending heat out through the atmosphere's transparent infrared window.": "通过反射太阳光并把热量从大气透明红外窗口辐射出去，实现被动冷却。",
    "The open thin-film simulator used to generate the real dataset and to verify the final candidates.": "用于生成真实数据集并验证最终候选的开源薄膜模拟器。",
    "A fast ML model that estimates what a structure will do without rerunning the full simulator.": "一种快速 ML 模型，用来估计某个结构会产生什么结果，而不必重新运行完整 simulator。",
    "A conditional variational autoencoder. Here it acts as a candidate generator that can sample many possible structures for one target.": "一种 conditional variational autoencoder。在这里它作为候选生成器，可以针对同一个目标采样出许多可能结构。",
    "A ranked subset of generated candidates that gets sent to the full simulator for the final truth check.": "从生成候选中选出的一个排序子集，会被送入完整 simulator 做最终真实性检查。",
    "The total difference between the target metrics and the simulator-confirmed metrics for a proposed structure.": "某个候选结构的目标指标与 simulator 确认指标之间的总差值。",
    "Retained sample255 winner": "保留的 sample255 优胜者",
    "Retained sample777 winner": "保留的 sample777 优胜者",
    "Categorical sample255 raw branch": "Categorical sample255 原始分支",
    "Categorical sample777 shortlist branch": "Categorical sample777 shortlist 分支",
    "Internal guides stay as local markdown. External papers are resolved from the citations we used, and only official open-access PDFs are downloaded into the app automatically.": "内部指南保持为本地 markdown。外部论文则根据项目实际使用的引文来解析，而且只有官方开放获取 PDF 才会被自动下载到应用中。",
    "This notebook view turns the project into a concrete runbook: the actual config, the actual training entrypoints, the actual commands to reproduce the main runs, and the artifact files that decided which model survived.": "这个笔记视图把项目变成一份具体的 runbook：真实 config、真实训练入口、复现主要实验的真实命令，以及决定哪个模型留下来的工件文件。",
    "Stage 1": "阶段 1",
    "Lock the multilayer search space": "锁定 multilayer 搜索空间",
    "Before any model training, the project fixed the structure family: 5 dielectric layers, one Ag reflector, 256 wavelength points, and explicit solar and atmospheric-window targets.": "在训练任何模型之前，项目先固定了结构族：5 层 dielectric、1 层 Ag reflector、256 个波长点，以及明确的 solar 与 atmospheric-window 目标。",
    "This step made every later claim reproducible. It defined exactly what a legal design is and exactly what spectra each sample must carry.": "这一步让后续所有结论都具备可复现性。它精确定义了什么是合法设计，以及每个样本必须携带怎样的光谱。",
    "Samples": "样本数",
    "Real WPTherml records in the final training bundle.": "最终训练包中的真实 WPTherml 记录数。",
    "Wavelengths": "波长数",
    "Each sample stores full reflectance and emissivity spectra.": "每个样本都存储完整的 reflectance 与 emissivity 光谱。",
    "Layer stack": "层堆",
    "5 on Ag": "5 层 + Ag",
    "Dielectric multilayer above a silver reflector.": "银反射层之上的 dielectric multilayer。",
    "Rebuild the dataset bundle": "重建数据集包",
    "Reproduction command for the current 4096-sample bundle.": "用于复现实验的当前 4096 样本数据集命令。",
    "Dataset generator CLI": "数据集生成 CLI",
    "Generated dataset manifest": "生成的数据集 manifest",
    "The design problem was bounded before training, so later results are comparable rather than hand-wavy.": "设计问题在训练前就被严格限定，因此后续结果可以比较，而不是含糊描述。",
    "The dataset is simulator-generated, but it is real project data, not a placeholder table.": "数据集虽然由 simulator 生成，但它是真实项目数据，而不是占位表格。",
    "Every later page depends on this exact config and dataset bundle.": "后面的每个页面都依赖这套确切的 config 和数据集。",
    "Stage 2": "阶段 2",
    "Train the fast forward surrogates": "训练快速 forward surrogate",
    "Two differentiable PyTorch models were trained to predict spectra directly from structure: one for reflectance and one for emissivity.": "项目训练了两个可微的 PyTorch 模型，直接从结构预测光谱：一个负责 reflectance，一个负责 emissivity。",
    "These are the speed layer. They let the pipeline score many candidates before paying the cost of a full WPTherml verification run.": "它们是整条流程的加速层，让系统在付出完整 WPTherml 验证成本之前，先为大量候选打分。",
    "Reflectance MAE": "Reflectance MAE",
    "Holdout-thickness-tail split.": "使用 holdout-thickness-tail 划分。",
    "Emissivity MAE": "Emissivity MAE",
    "Window-band MAE": "窗口波段 MAE",
    "Critical 8-13 um band accuracy.": "关键 8-13 μm 波段的精度。",
    "Train the reflectance surrogate": "训练 reflectance surrogate",
    "Current repo reproduction command for the reflectance bundle.": "当前仓库中复现 reflectance 模型的命令。",
    "Train the emissivity surrogate": "训练 emissivity surrogate",
    "Current repo reproduction command for the emissivity bundle.": "当前仓库中复现 emissivity 模型的命令。",
    "Forward-surrogate CLI": "Forward-surrogate CLI",
    "Reflectance metrics": "Reflectance 指标",
    "Emissivity metrics": "Emissivity 指标",
    "The forward models are not the final answer. They are the fast evaluators that make large candidate pools affordable.": "forward model 不是最终答案，它们是快速评估器，让大规模候选池变得可负担。",
    "The holdout-thickness-tail split matters because it stresses generalization on a harder region of the design space.": "holdout-thickness-tail 划分之所以重要，是因为它会在设计空间中更困难的区域上考验泛化能力。",
    "Both spectra matter because daytime radiative cooling needs high solar reflection and strong atmospheric-window emission.": "两条光谱都重要，因为日间辐射制冷同时需要高 solar reflection 和强 atmospheric-window emission。",
    "Stage 3": "阶段 3",
    "This is where the project tests different ways to go from a target metric set back to a structure: tandem inverse design, a conditional VAE, and a conditional diffusion model.": "这一阶段测试的是：如何从一组目标指标反推结构，包括 tandem inverse design、conditional VAE 和 conditional diffusion model。",
    "The models differ in style. Tandem gives one direct answer. The generative models sample many plausible answers and need later ranking plus verification.": "这些模型风格不同。Tandem 直接给出一个答案；生成式模型会采样出多个合理答案，因此后面还需要排序和验证。",
    "CVAE feature RMSE": "CVAE feature RMSE",
    "Scaled 4096-sample continuous-decoder run.": "在 4096 样本规模下的 continuous-decoder 结果。",
    "Diffusion feature RMSE": "Diffusion feature RMSE",
    "Competitive but not the retained winner.": "有竞争力，但不是最终保留的优胜者。",
    "CVAE material accuracy": "CVAE 材料准确率",
    "Shows why one-shot reconstruction is not the full story.": "这也说明为什么一次性重建并不能代表全部情况。",
    "Train the tandem baseline": "训练 tandem baseline",
    "Reproduction command for the deterministic tandem baseline.": "复现确定性 tandem baseline 的命令。",
    "Train the continuous CVAE": "训练 continuous CVAE",
    "Retained generator family after the full audit.": "在完整审计后仍被保留的生成器家族。",
    "Train the diffusion baseline": "训练 diffusion baseline",
    "Competitive generator that stayed close to raw CVAE sampling but did not beat the shortlist workflow.": "这是一个有竞争力的生成器，表现接近原始 CVAE 采样，但没有超过 shortlist 工作流。",
    "Tandem training entrypoint": "Tandem 训练入口",
    "Conditional VAE entrypoint": "Conditional VAE 入口",
    "Conditional diffusion entrypoint": "Conditional diffusion 入口",
    "The retained CVAE is best judged as a candidate generator, not as a one-shot inverse predictor.": "保留的 CVAE 更适合被看成候选生成器，而不是一次性逆向预测器。",
    "Diffusion is real in this repo, but the decisive performance jump came later from ranking and verification.": "Diffusion 在这个仓库里是真实存在的，但决定性性能提升来自后续的排序与验证。",
    "The notebook keeps the actual training entrypoints visible so the pipeline is inspectable rather than magical.": "笔记页把真实训练入口直接展示出来，让整条流程是可检查的，而不是像黑箱魔法。",
    "Stage 4": "阶段 4",
    "Shortlist candidates, then re-run physics": "先 shortlist 候选，再重跑 physics",
    "The generator did not win by itself. The best workflow sampled 256 candidates, ranked them with the forward surrogates, trimmed to the top 16, and then re-simulated those finalists with WPTherml.": "生成器本身并不是胜负的唯一来源。最佳工作流先采样 256 个候选，用 forward surrogate 排名，裁剪到前 16 名，再用 WPTherml 重新模拟这些入围结果。",
    "This is the trust step. It is why the final winner is a verified physics result instead of a model hallucination.": "这是建立可信度的一步。正因为如此，最终优胜者是经过 physics 验证的结果，而不是模型幻觉。",
    "Sample255 winner": "Sample255 优胜者",
    "Best shortlisted verified error for target A.": "目标 A 上 shortlist 后的最佳验证误差。",
    "Sample777 winner": "Sample777 优胜者",
    "Best shortlisted verified error for target B.": "目标 B 上 shortlist 后的最佳验证误差。",
    "Pool trim": "候选裁剪",
    "Sample broadly, then verify the finalists.": "先广泛采样，再验证入围结果。",
    "Rank a 256-sample candidate pool": "为 256 样本候选池排序",
    "This is the shortlist step that changed the leaderboard.": "这就是改写排行榜的 shortlist 步骤。",
    "Verify the shortlisted finalists with WPTherml": "用 WPTherml 验证 shortlist 入围结果",
    "The final truth check: simulator re-run of the shortlisted proposals.": "最终真实性检查：把 shortlist 提案重新交给 simulator。",
    "Candidate ranking CLI": "候选排序 CLI",
    "Physics verification CLI": "Physics 验证 CLI",
    "Verified shortlist results for sample255": "sample255 的已验证 shortlist 结果",
    "The shortlist stage is more important than just choosing CVAE versus diffusion.": "与其说关键在于选择 CVAE 还是 diffusion，不如说关键在于 shortlist 这一步。",
    "The winning error of about 0.0946 came from the hybrid loop, not from raw best-of-64 generation.": "约 0.0946 的优胜误差来自混合闭环，而不是原始 best-of-64 生成。",
    "The final artifact is a ranked JSON file that can be inspected line by line.": "最终工件是一份可逐行检查的排序 JSON 文件。",
    "Stage 5": "阶段 5",
    "Audit the main open hypothesis and reject the categorical branch": "审计主要开放假设，并否决 categorical 分支",
    "The final audit tested a real model-design concern: the old CVAE trained materials softly but decoded them with a hard argmax. A categorical decoder branch was added, retrained, and then forced through the same verification loop.": "最终审计测试了一个真实的模型设计问题：旧版 CVAE 在训练时对材料是 soft 表示，但在解码时却使用 hard argmax。为此项目新增了 categorical decoder 分支，重新训练后再强制走同样的验证闭环。",
    "The audit matters because it removed a plausible false lead. The newer categorical decoder did not beat the retained continuous-decoder baseline in final verified error.": "审计之所以重要，是因为它排除了一个看起来很合理但实际上错误的方向。新的 categorical decoder 在最终验证误差上并没有超过保留的 continuous-decoder baseline。",
    "Categorical sample255": "Categorical sample255",
    "Shortlist verified error after the audit retrain.": "审计重训之后的 shortlist 验证误差。",
    "Categorical sample777": "Categorical sample777",
    "Still far behind the retained baseline.": "仍然明显落后于保留 baseline。",
    "CUDA status": "CUDA 状态",
    "The audit also corrected the environment to use CUDA.": "审计同时还修正了环境，使其能够使用 CUDA。",
    "Train the categorical audit branch": "训练 categorical 审计分支",
    "The strongest audit hypothesis was tested directly rather than discussed abstractly.": "最强的审计假设不是停留在讨论层面，而是被直接实现并测试了。",
    "Categorical branch metrics": "Categorical 分支指标",
    "The audit did not rubber-stamp the baseline. It tried to break it.": "审计并不是给 baseline 背书，而是试图把它推翻。",
    "The strongest retained workflow is still the continuous-decoder CVAE plus shortlist plus WPTherml verification.": "最强、且仍被保留的工作流，仍然是 continuous-decoder CVAE + shortlist + WPTherml 验证。",
    "The next real jump is more data or a more different algorithmic ingredient, not another tiny tweak.": "下一次真正的跃迁，需要更多数据或更不一样的算法成分，而不是再做一次小修小补。",
    "**Foundational work.** Proved ANNs can predict electromagnetic spectra and perform inverse design. Referenced as [19] in the paper.": "**奠基工作。** 证明 ANN 可以预测电磁光谱并执行逆向设计。在论文中对应文献 [19]。",
    "Conditional deep learning for colored transmissive RC films. Multi-objective: color + cooling + transparency. Referenced as [24].": "针对彩色透射型 RC 薄膜的条件深度学习方法。它是一个多目标问题：color + cooling + transparency。对应文献 [24]。",
    "Tandem neural network for colored RC. Demonstrates the forward-inverse architecture. Referenced as [37].": "面向彩色 RC 的 Tandem neural network，展示了 forward-inverse 架构。对应文献 [37]。",
    "CNN-based inverse design specifically for particle-embedded RC systems. Referenced as [35].": "专门针对 particle-embedded RC 系统的 CNN 逆向设计方法。对应文献 [35]。",
    "Generative ML model for high-performance daytime RC. Referenced as [25].": "面向高性能日间 RC 的生成式 ML 模型。对应文献 [25]。",
    "KNN-based design of biomimetic RC metamaterial. Referenced as [30].": "基于 KNN 的仿生 RC metamaterial 设计方法。对应文献 [30]。",
    "ML framework for metasurface RC emitter design. Referenced as [29].": "面向 metasurface RC emitter 设计的 ML 框架。对应文献 [29]。",
    "**First Bayesian optimization work in RC.** Used <1% of design space. Referenced as [22].": "**RC 领域最早的 Bayesian optimization 工作之一。** 只探索了不到 1% 的设计空间。对应文献 [22]。",
    "Deep Q-Network (DRL) for emissivity design including radiative cooling.": "使用 Deep Q-Network (DRL) 进行 emissivity 设计，其中包含辐射制冷场景。",
    "Deep learning for microstructured thermal radiation control. Open-source based approach.": "用 deep learning 做微结构热辐射控制，属于基于开源方法的路线。",
    "Comprehensive review of AI in materials science. Referenced as [17].": "关于 AI 在材料科学中的综合综述。对应文献 [17]。",
    "Definitive BO tutorial. Referenced as [20].": "权威的 BO 教程型综述。对应文献 [20]。",
    "Review of inverse design approaches in materials science.": "关于材料科学中 inverse design 方法的综述。",
    "Overview of ML for materials inverse design.": "关于 ML 驱动材料 inverse design 的总览。",
    "Deep learning for plasmonic structure design. Referenced as [34].": "面向 plasmonic 结构设计的 deep learning 方法。对应文献 [34]。",
    "Very recent DNN-based reverse design of multilayer films for RC.": "非常新的、基于 DNN 的多层薄膜 RC 逆向设计工作。",
    "RL for thermal control film design — directly applicable to RC.": "使用 RL 进行热控薄膜设计，可直接迁移到 RC。",
    "ML for RC surface temperature prediction using small-batch datasets.": "使用小批量数据集来预测 RC 表面温度的 ML 方法。",
    "ML for building-integrated RC film performance analysis.": "用于建筑集成式 RC 薄膜性能分析的 ML 方法。",
    "Quantum annealing + active ML for transparent RC design. Novel optimization approach.": "将 quantum annealing 与 active ML 结合，用于透明 RC 设计，是一种新颖的优化路线。",
    "ML for emissivity prediction with very small datasets — addresses the data scarcity challenge directly.": "在超小数据集条件下预测 emissivity 的 ML 方法，直接回应了数据稀缺问题。",
    "Open-source FOS tool: Mie + Monte Carlo + ML for nanoparticle RC paint design.": "开源 FOS 工具：把 Mie、Monte Carlo 和 ML 结合起来，用于纳米颗粒 RC 涂料设计。",
}


def _title_from_markdown(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _summary_from_markdown(body: str) -> str:
    paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n", body) if segment.strip()]
    for paragraph in paragraphs:
        cleaned = " ".join(paragraph.split())
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if (
            paragraph.startswith("#")
            or paragraph.startswith(">")
            or paragraph.startswith("|")
            or paragraph.startswith("```")
            or re.fullmatch(r"-+", cleaned)
            or "```" in paragraph
            or cleaned.lower().startswith("table of contents")
            or cleaned.count("](#") >= 2
            or (lines and all(re.match(r"(?:\d+\.|[-*])\s+", line) for line in lines))
        ):
            continue
        if len(cleaned) > 220:
            return f"{cleaned[:217]}..."
        return cleaned
    return ""


def _translate_string(value: str, locale: str) -> str:
    if locale == "en":
        return value
    return SITE_TRANSLATIONS_ZH.get(value, value)


def _translate_recursive(value, locale: str):
    if locale == "en":
        return value
    if isinstance(value, dict):
        return {key: _translate_recursive(item, locale) for key, item in value.items()}
    if isinstance(value, list):
        return [_translate_recursive(item, locale) for item in value]
    if isinstance(value, str):
        return _translate_string(value, locale)
    return value


def localize_site_data(site_data: dict, locale: str) -> dict:
    if locale == "en":
        return deepcopy(site_data)
    return _translate_recursive(deepcopy(site_data), locale)


def localize_research_payload(payload: dict, locale: str, root: Path) -> dict:
    localized = _translate_recursive(deepcopy(payload), locale)
    if locale == "en":
        return localized

    for document in localized.get("documents", []):
        original_path = Path(document["sourcePath"])
        translated_path = root / "research" / locale / original_path.name
        if not translated_path.exists():
            continue

        body = translated_path.read_text(encoding="utf-8")
        document["title"] = _title_from_markdown(body, document["title"])
        document["summary"] = _summary_from_markdown(body)
        document["body"] = body
        document["sourcePath"] = translated_path.relative_to(root).as_posix()

    return localized
