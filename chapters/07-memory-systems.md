# 第 7 章：Memory Systems

## 章节定位

本章解释“外置上下文”如何上升为“可持续知识系统”。

## 对应官方 skill

- `skills/memory-systems/SKILL.md`

## 必读材料

- `skills/memory-systems/SKILL.md`
- `examples/digital-brain-skill/HOW-SKILLS-BUILT-THIS.md`
- `examples/x-to-book-system/SKILLS-MAPPING.md`

## 问题

不是所有写到文件里的东西都叫 memory。本章解决 filesystem persistence 与 memory architecture 的边界问题。

## 核心论点

Memory 的难点从来不是存储，而是“以后能否按正确方式取回”。一个记不准、取不对、分不清时效的 memory system，往往比没有 memory 更危险。

## 定义

Memory Systems 指的是 agent 跨时间保留、更新、检索和整合知识的架构层。它不仅包含“把信息放哪里”，还包含“何时写入、按什么索引、用什么策略取回、事实过期时如何处理、多个实体如何保持一致”。

因此 memory 不是 persistence 的同义词。持久化只是前提，真正决定 memory 质量的是 retrieval quality、entity consistency 和 temporal validity。

## 机制

重点解释：

- working memory
- short-term memory
- long-term memory
- entity memory
- temporal knowledge graph

## 技术模式

- start simple, add structure later
- choose retrieval by query type
- use temporal validity for changing facts
- separate storage from retrieval policy

## 案例证据

- `digital-brain-skill` 的 file-based persistent context
- `x-to-book-system` 的 temporal knowledge graph 选择理由

## 边界比较

### Memory Systems vs Filesystem Context

- Filesystem Context 主要解决上下文外置和动态发现。
- Memory Systems 主要解决跨会话知识建模与可检索性。
- 前者偏机制层，后者偏知识架构层。

### Vector RAG vs Temporal KG

- Vector RAG 擅长语义近邻召回。
- Temporal KG 擅长关系推理、时间有效性和事实演化。
- 选择标准不是流行度，而是查询类型和错误代价。

## 反模式

- 一上来就上复杂 memory stack
- 把向量召回当成通用解法
- 不区分“可存储”和“可检索”

## 写作练习

写 800-1200 字，回答：

“为什么记忆系统的核心问题不是存得下，而是以后能不能被正确取回？”

## 章节草稿

走到这一章，我们开始碰到一个特别容易混淆的问题：把东西写到文件里，算不算 memory？答案是，不一定。文件落盘只解决了 persistence，memory system 关心的是另一层问题：以后能不能在正确时刻、以正确形式、拿回正确的信息。也正因为如此，仓库在 `memory-systems` skill 里反复强调一个极其务实的原则：tool complexity matters less than reliable retrieval。

这句话很重要，因为它把 memory 讨论从“用什么酷炫框架”拉回到“能不能真的取对”。很多团队一上来就想做向量库、知识图谱、长时记忆代理，最后却发现 retrieval 本身并不可靠：该取的没取到，不该取的取一堆，过期事实与当前事实混在一起，甚至同一个实体在不同会话里被当成不同对象。这样的系统，表面上 memory 很高级，实际却更容易污染 context。

仓库给出的层次划分很有用：working memory 在上下文窗口里，short-term memory 面向当前会话，long-term memory 跨会话保存稳定信息，entity memory 保证“这个人还是那个人”，temporal KG 则处理“这个事实在不同时间是否仍成立”。这几个层次的价值，不在于命名整齐，而在于提醒我们：不同信息需要不同 retention 和 retrieval 策略。把它们都塞进一个统一桶里，最终只会让系统越来越难判断。

这一章最成熟的工程建议，其实非常克制：start simple, add complexity only when retrieval fails。也就是说，不要因为 graph 很酷就上 graph，不要因为 semantic memory 很流行就默认上 embedding。先用文件系统和结构化文件验证，你到底需要的是什么检索能力。如果问题只是“记住用户偏好和一些项目状态”，文件系统加时间戳可能已经足够。只有当你真的需要关系推理、实体一致性或时序查询时，图结构和 temporal validity 才开始变得必要。

`digital-brain-skill` 正好说明了“简单但有效”的一面。这个案例没有一开始就引入复杂数据库，而是用 JSONL、YAML、Markdown 这样的 agent-friendly 文件格式承担长期信息。为什么这样能工作？因为它的查询需求相对简单，重点是可读、可追踪、可增量更新。换句话说，它不是在追求最强 memory，而是在追求最合适的 retrieval。对很多个人操作系统、创作者系统、轻量 agent 来说，这种设计反而比复杂 memory stack 更稳。

但 `x-to-book-system` 又展示了另一面：当任务开始要求“谁在某段时间支持什么观点”“哪些账号在某个议题上相互认同或冲突”“某个立场是如何演化的”，文件系统就不够了。因为这里的问题不是能不能存，而是能不能做关系遍历和时间过滤。仓库因此选择 temporal knowledge graph，而不是简单 vector store。理由也很明确：向量检索擅长找相似文本，不擅长回答“这条事实在 1 月成立、在 3 月是否还成立”。

这也解释了 memory systems 与 filesystem context 的关系。文件系统是一种很好的 context substrate，适合承载状态、计划、日志和可按需读取的文档；memory system 则更像在这个地面层之上增加索引、关系、时序和实体一致性规则。你可以说 filesystem 是最朴素的 memory substrate，但不能说任何 filesystem persistence 都已经构成 memory architecture。

因此，这章真正要建立的判断是：memory 设计的中心不是 storage，而是 retrieval correctness。一个好的记忆系统，要么简单到足够可靠，要么复杂得有明确理由。最怕的不是 memory 太弱，而是 memory 看上去很强、实际上不断把错的、旧的、无关的东西送回 context。对 Context Engineering 来说，那样的 memory 不是增强器，而是持续污染源。

## 学习检查

1. 为什么 persistence 不自动等于 memory？
2. `digital-brain-skill` 和 `x-to-book-system` 分别代表了哪两类 memory 需求？
3. 为什么说 memory system 的评价核心是 retrieval correctness？
