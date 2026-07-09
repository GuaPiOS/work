# Week 2 术语表 v1

## 1. Tool Contract

一句话定义：agent 与外部世界之间的可行动作契约。
与相邻概念的边界：不同于普通开发者 API 文档，它必须直接服务模型判断与恢复。
在本地仓库中的证据：`skills/tool-design/SKILL.md`

## 2. Tool Description as Prompt

一句话定义：工具描述本身会塑造 agent 对何时、如何调用工具的理解。
与相邻概念的边界：不是补充说明，而是行为引导的一部分。
在本地仓库中的证据：`skills/tool-design/SKILL.md`

## 3. Consolidation Principle

一句话定义：如果人都说不清什么时候该用哪个工具，模型更不可能稳定做对。
与相邻概念的边界：强调减少边界重叠，不等于一味追求工具越少越好。
在本地仓库中的证据：`skills/tool-design/SKILL.md`

## 4. Architectural Reduction

一句话定义：减少定制工具，转而依赖更通用、更原始的能力抽象。
与相邻概念的边界：不是删功能，而是减少不必要的中间包装层。
在本地仓库中的证据：`skills/tool-design/SKILL.md`

## 5. Actionable Error Message

一句话定义：能帮助 agent 纠错和继续推进的错误返回。
与相邻概念的边界：不同于仅供开发者排查的日志信息。
在本地仓库中的证据：`skills/tool-design/SKILL.md`

## 6. Namespace

一句话定义：通过命名分组减少工具选择混乱的组织方式。
与相邻概念的边界：它解决的是认知负担，不直接增加能力。
在本地仓库中的证据：`skills/tool-design/SKILL.md`

## 7. Filesystem Context

一句话定义：把大量上下文外置到文件系统并按需发现、读取、更新的模式。
与相邻概念的边界：不等于简单存档，它强调动态上下文发现。
在本地仓库中的证据：`skills/filesystem-context/SKILL.md`

## 8. Dynamic Context Discovery

一句话定义：agent 在需要时再通过搜索和读取获取外部上下文。
与相邻概念的边界：区别于静态预加载。
在本地仓库中的证据：`skills/filesystem-context/SKILL.md`

## 9. Scratch Pad

一句话定义：承载大体量中间结果的外部文件工作区。
与相邻概念的边界：它承载的是过程信息，不等于长期记忆。
在本地仓库中的证据：`skills/filesystem-context/SKILL.md`

## 10. Plan Persistence

一句话定义：把任务计划写入外部文件并在关键时刻重读。
与相邻概念的边界：不同于只在消息历史里记计划。
在本地仓库中的证据：`skills/filesystem-context/SKILL.md`

## 11. Sub-Agent Communication via Filesystem

一句话定义：子代理通过共享文件而非层层消息转述来共享状态。
与相邻概念的边界：它主要为保真和隔离服务。
在本地仓库中的证据：`skills/filesystem-context/SKILL.md`

## 12. Dynamic Skill Loading

一句话定义：只在任务需要时读取完整技能文件。
与相邻概念的边界：属于上下文装载策略，不是记忆策略。
在本地仓库中的证据：`skills/filesystem-context/SKILL.md`

## 13. Working Memory

一句话定义：只存在于当前上下文窗口中的即时工作状态。
与相邻概念的边界：它不跨会话持久化。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 14. Short-Term Memory

一句话定义：会话范围内可持续读取的短时外部状态。
与相邻概念的边界：比 working memory 稳定，但不一定跨会话。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 15. Long-Term Memory

一句话定义：跨会话保留的重要偏好、事实和知识。
与相邻概念的边界：不同于临时 scratch pad。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 16. Entity Memory

一句话定义：保证同一实体在不同时间和会话中保持身份一致的记忆层。
与相邻概念的边界：比一般事实存储更强调 identity consistency。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 17. Temporal Validity

一句话定义：一个事实在什么时间范围内成立的约束信息。
与相邻概念的边界：区别于静态真值假设。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 18. Temporal Knowledge Graph

一句话定义：带有时间有效区间的图结构记忆系统。
与相邻概念的边界：比向量检索更适合关系推理和事实演化。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 19. Retrieval Correctness

一句话定义：在正确时刻取回正确记忆的能力。
与相邻概念的边界：比单纯存储能力更能决定 memory system 质量。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

## 20. Hybrid Retrieval

一句话定义：结合语义、关键词、关系和时间过滤的检索策略。
与相邻概念的边界：不是新型存储，而是组合式取回策略。
在本地仓库中的证据：`skills/memory-systems/SKILL.md`

