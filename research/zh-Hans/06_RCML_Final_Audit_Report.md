# RCML 最终审计报告（中文摘要版）

这份中文版本保留了原报告最重要的结论：截至 2026 年 4 月，本地 radiative-cooling ML pipeline 处于一个“可审计、可复现、而且已经接近当前数据规模本地上限”的状态。最关键的判断不是“模型还能不能继续调”，而是“现在保留哪条工作流最合理，以及下一步应该把资源投入到哪里”。

## 执行结论

报告的最终结论可以压缩成四句话：

1. WPTherml + 公共 optical constants 仍然是当前最强、最自由可复现的数据路径。
2. 4096 条记录的数据集是干净的，没有发现破坏性质量问题。
3. categorical-material decoder 作为主要开放假设已经被认真测试，但没有胜出。
4. 当前最应该保留的默认工作流仍然是 continuous-decoder CVAE + surrogate shortlist + WPTherml verification。

## 数据路径结论：WPTherml 不是妥协，而是合理核心

报告特别强调，当前并不存在可直接替代的开放 RC inverse-design benchmark。也就是说，使用 WPTherml 生成训练数据并不是“因为没有更好的办法才凑合”，而是当前最合理、最可复现的公共路线。

## 数据集洁净度审计

审计确认了几个关键事实：

- 总记录数为 4096。
- duplicate check 结果为 0。
- 目标指标覆盖了低到高性能区间。
- 没有明显的 degenerate simulation 样本污染训练集。

这意味着后续模型比较是站在干净数据基础上的，而不是建立在一个被隐藏数据问题破坏的前提上。

## 环境审计与修复

另一个关键点是训练环境。报告确认并修复了原先 CPU-only PyTorch 的问题，把环境升级到了 CUDA-enabled 路线，使 RTX 3080 可以真正进入训练与审计环节。

这一步很重要，因为如果 categorical decoder 分支要被公平地测试，就不能让它建立在劣化的运行环境上。

## 模型状态：谁表现稳定，谁只是看起来合理

报告对主要模型的判断是：

- forward surrogate 的 MAE 大约在 0.023–0.024，足以支撑 shortlist ranking。
- tandem inverse model 是有意义的 baseline，但不是最强方案。
- continuous CVAE 在完整 verification 后仍是最佳 generator。
- diffusion 有竞争力，但没有超过保留工作流。

也就是说，真正的胜负并不是只看训练指标，而是看“生成 → 排序 → physics verification”这整条链路之后谁还能站住。

## 审计中发现并验证的主要假设

报告并没有停留在“怀疑 categorical decoder 可能更好”的层面，而是把这个想法直接实现并测试了。其核心问题是：旧版 CVAE 在训练材料时是 soft 表示，但在解码时却使用 hard argmax，这可能导致 mismatch。

于是项目新增了 categorical decoder 分支，并让它走完整审计路径。结果是：这个问题虽然真实存在、而且值得检验，但把它修正之后并没有带来更好的最终验证结果。

## 最终验证比较

报告里最关键的数字包括：

- continuous CVAE shortlist 在 sample255 上达到约 0.0946 total error。
- continuous CVAE shortlist 在 sample777 上达到约 0.0712 total error。
- categorical CVAE 对应结果明显更差，说明它并没有击败保留 baseline。

因此，最终优胜者不是“看起来更理论正确”的分支，而是“在真实 verification loop 里仍然赢”的那条分支。

## 最终建议

报告最强的工程判断是：当前系统已经接近本地上限，再继续做小幅超参数微调，收益大概率有限。真正值得投入的下一步是：

1. 把模拟数据规模从 4096 明显扩展上去。
2. 引入实验反馈，形成真实 closed-loop。
3. 更换真正不同的算法成分，而不是重复微调现有家族。
4. 扩展 design space，不再只停留在 5-layer dielectric stack。

这份审计报告真正提供的价值，不只是“保留哪个模型”，而是明确告诉你：现在该停在哪里、下一步该往哪里真正用力。
