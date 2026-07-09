# Week 1 术语表 v1

## 1. Context

一句话定义：模型在一次推理时可访问的完整状态。
与相邻概念的边界：比 prompt 大，包含 prompt、tools、history、docs、outputs。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 2. Context Engineering

一句话定义：对进入模型注意力预算的信息进行设计、裁剪、排序和装载。
与相邻概念的边界：不是单纯写 prompt，而是设计整个可见状态。
在本地仓库中的证据：`README.md`

## 3. Prompt Engineering

一句话定义：围绕提示词内容与表述方式优化模型行为。
与相邻概念的边界：只覆盖 context 的一个组成部分。
在本地仓库中的证据：与 `context-fundamentals` 的对照理解

## 4. System Prompt

一句话定义：定义 agent 身份、约束和行为边界的稳定前缀。
与相邻概念的边界：不同于 task-specific retrieved docs。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 5. Tool Definitions

一句话定义：模型可调用动作的接口说明与行为引导。
与相邻概念的边界：既是 API 描述，也是 prompt 的一部分。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 6. Retrieved Documents

一句话定义：运行时按需拉入的外部知识片段。
与相邻概念的边界：区别于预加载的固定 instructions。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 7. Message History

一句话定义：会话中已经发生的交互与中间推理痕迹。
与相邻概念的边界：属于会话内工作记忆，不等于长期 memory。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 8. Tool Outputs

一句话定义：agent 调用外部工具后返回的结果。
与相邻概念的边界：不同于工具定义本身，通常是最大 token 消耗源。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 9. Attention Budget

一句话定义：模型在一个上下文内可稳定分配的有限注意力资源。
与相邻概念的边界：不是窗口大小本身，而是窗口内有效处理能力。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 10. Progressive Disclosure

一句话定义：只在需要时加载完整信息，而不是一次性预加载全部内容。
与相邻概念的边界：它是装载策略，不是压缩策略。
在本地仓库中的证据：`docs/agentskills.md`

## 11. Context Budgeting

一句话定义：显式规划不同类型信息占用多少上下文配额。
与相邻概念的边界：区别于事后统计 token，它是前置设计动作。
在本地仓库中的证据：`skills/context-fundamentals/SKILL.md`

## 12. Lost-in-the-Middle

一句话定义：处于上下文中段的信息更容易被忽略的注意力退化现象。
与相邻概念的边界：它是位置问题，不等于信息错误。
在本地仓库中的证据：`skills/context-degradation/SKILL.md`

## 13. Context Poisoning

一句话定义：错误信息进入上下文并被后续推理反复强化。
与相邻概念的边界：比一次普通 hallucination 更危险，因为会持续传播。
在本地仓库中的证据：`skills/context-degradation/SKILL.md`

## 14. Context Distraction

一句话定义：无关信息抢占注意力，压制真正有用信息。
与相邻概念的边界：强调噪声竞争，不等于任务边界混淆。
在本地仓库中的证据：`skills/context-degradation/SKILL.md`

## 15. Context Confusion

一句话定义：模型无法判断哪些上下文适用于当前任务。
与相邻概念的边界：强调适用范围混乱，不等于单纯噪声过多。
在本地仓库中的证据：`skills/context-degradation/SKILL.md`

## 16. Context Clash

一句话定义：上下文中存在彼此冲突的信息源或约束。
与相邻概念的边界：不一定谁错，关键是它们同时存在且无优先级。
在本地仓库中的证据：`skills/context-degradation/SKILL.md`

## 17. Compression

一句话定义：在尽量保留工作连续性的前提下缩短上下文。
与相邻概念的边界：重点是历史压缩，不等于所有优化动作。
在本地仓库中的证据：`skills/context-compression/SKILL.md`

## 18. Tokens-per-Task

一句话定义：从任务开始到完成的总 token 成本。
与相邻概念的边界：比 tokens-per-request 更符合真实工程成本。
在本地仓库中的证据：`skills/context-compression/SKILL.md`

## 19. Artifact Trail

一句话定义：任务过程中形成的文件、改动、错误、决定等可追踪痕迹。
与相邻概念的边界：它不是 narrative summary，而是工作轨迹。
在本地仓库中的证据：`skills/context-compression/SKILL.md`

## 20. Anchored Iterative Summarization

一句话定义：在固定结构下增量合并摘要的压缩方法。
与相邻概念的边界：区别于每次重写全量 summary。
在本地仓库中的证据：`skills/context-compression/SKILL.md`

## 21. Compaction

一句话定义：在接近上下文上限时对内容进行摘要重启的动作。
与相邻概念的边界：它是 optimization 中常用手段，也可属于 compression 流程。
在本地仓库中的证据：`skills/context-optimization/SKILL.md`

## 22. Observation Masking

一句话定义：把冗长工具输出替换成可回取的紧凑引用或摘要。
与相邻概念的边界：不是删除信息，而是改变持续驻留方式。
在本地仓库中的证据：`skills/context-optimization/SKILL.md`

## 23. KV-Cache Optimization

一句话定义：通过稳定前缀与顺序设计提高缓存复用率。
与相邻概念的边界：关注推理成本与延迟，不直接改变语义内容。
在本地仓库中的证据：`skills/context-optimization/SKILL.md`

## 24. Context Partitioning

一句话定义：将任务拆入多个隔离上下文，避免单一上下文过载。
与相邻概念的边界：比 compaction 更激进，接近架构级优化。
在本地仓库中的证据：`skills/context-optimization/SKILL.md`

