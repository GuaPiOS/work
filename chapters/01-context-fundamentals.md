# 第 1 章：Context Engineering Fundamentals

## 章节定位

这是全书入口章。目标不是解释“prompt 怎么写”，而是重新定义“模型在一次推理中到底能看到什么、能处理什么、会被什么约束”。

## 对应官方 skill

- `skills/context-fundamentals/SKILL.md`

## 必读材料

- `README.md`
- `docs/blogs.md`
- `skills/context-fundamentals/SKILL.md`

## 问题

如果 context 是模型在一次推理时的完整可见状态，那么工程师真正设计的就不只是 prompt，而是整套“进入模型注意力预算的信号系统”。本章解决“Context Engineering 到底在工程什么”。

## 核心论点

Context Engineering 的基本单位不是一句提示词，而是一整套待装配的推理现场。谁进入现场、按什么顺序进入、停留多久、是否可按需回取，决定了 agent 是否真正可用。

## 定义

Context Engineering 不是“写一段更聪明的提示词”，而是对模型一次推理中全部可见状态进行设计、裁剪、排序和装载。它关注的对象包括 system prompt、tool definitions、retrieved documents、message history 和 tool outputs，也关注这些信息以什么顺序出现、以多大密度出现、在什么时机被加载。

如果 Prompt Engineering 讨论的是“你对模型说什么”，那么 Context Engineering 讨论的是“你让模型在这一轮推理里看见什么、先看见什么、看多久、为了做哪一步决策而看”。这就是为什么它天然比 prompt 更接近系统设计。

## 机制

重点解释：

- context 的组成：system prompt、tool definitions、retrieved docs、message history、tool outputs
- attention budget 为什么是核心约束
- progressive disclosure 为什么比一次性塞满上下文更重要
- context budgeting 为什么是工程动作，而不是抽象理念

## 技术模式

- anatomy-of-context
- attention-budget-first design
- progressive disclosure
- hybrid loading strategy

## 案例证据

- 从 `README.md` 提取仓库对 context engineering 的定义
- 从 `docs/blogs.md` 提取 write / select / compress / isolate 四种动作

## 边界比较

### Context Engineering vs Prompt Engineering

- Prompt Engineering 主要优化指令表达。
- Context Engineering 设计的是模型整轮推理可见状态。
- Prompt 是 context 的一个部分，不是 context 的全体。

### Context Window vs Attention Budget

- Context window 是理论可容纳长度。
- Attention budget 是模型在该长度内仍能稳定利用的有效能力。
- 工程实践里，后者比前者更决定真实质量。

## 反模式

- 把 context engineering 直接等同于 prompt engineering
- 认为更长 context window 自动等于更强能力
- 把所有资料预加载视为“更充分”

## 写作练习

写 800-1200 字，回答：

“为什么在 agent 系统里，真正被工程化的对象不是 prompt，而是整个 context 的组成、顺序、密度和装载时机？”

## 章节草稿

很多人第一次接触 Context Engineering 时，会把它理解成 Prompt Engineering 的升级版。这种理解不完全错，但层级太低。Prompt 只是 context 的一个组成部分，而不是全部。对 agent 系统来说，真正被送进模型的，不只是几段指令文本，还包括工具定义、历史消息、检索到的资料、外部命令返回结果，以及系统在运行过程中不断追加的中间状态。换句话说，工程师真正管理的不是一条 prompt，而是一整套推理现场。

本地仓库在 `context-fundamentals` 里给出的定义非常关键：context 是模型在 inference 时刻可访问的完整状态。这个定义有两个直接后果。第一，context 不是静态文档，而是动态装配物。第二，context 的问题不是“有没有”，而是“有没有把真正有价值的信号放进去”。这也是为什么仓库反复强调 smallest high-signal token set，而不是 longest possible context。长并不自动等于强，很多时候，长只是让注意力预算更快被稀释。

理解 Context Engineering，必须先理解 context 的五个主要组成。System prompt 决定身份、边界和行为基调；tool definitions 决定模型有哪些可行动作以及如何理解动作含义；retrieved documents 提供任务相关外部知识；message history 承担会话内工作记忆；tool outputs 则是 agent 在真实世界行动后的反馈。这里最容易被低估的是 tool outputs。因为在真实 agent 轨迹里，最耗 token 的往往不是用户消息，而是搜索结果、文件内容、命令输出和 API 返回。也就是说，很多系统不是死于 prompt 太弱，而是死于工具输出太肥。

这就引出本章的第一个核心机制：attention budget。模型的上下文窗口从来不是一个“装满就能用”的背包，而更像一个有限注意力池。你塞进去的每一个 token 都会参与竞争。仓库里对这个问题的表达很直接，context 是 finite resource with diminishing returns。随着上下文增长，模型不是线性地变差，而是越来越难把注意力稳定分配到真正关键的位置。于是，工程的重点不再是“能不能多塞一点”，而是“该不该塞、先塞什么、晚塞什么”。

第二个核心机制是 progressive disclosure。这个概念在 Agent Skills 格式里尤其清楚：启动时只加载 skill 名称和描述，真正命中任务再加载完整 `SKILL.md`。这不是节省几百 token 的小技巧，而是一种通用工程原则。信息不应该在“也许会用到”的时刻预加载，而应该在“当前决策确实需要它”的时刻按需引入。这个原则可以扩展到整个 agent 系统：文档先载入目录，再载入章节；案例先看摘要，再钻取细节；工具输出先看摘要，再按引用回看原文。

第三个核心机制是 context budgeting。预算不是抽象理念，而是明确的设计动作。你要知道 system prompt 大概占多少、工具描述占多少、历史消息什么时候会膨胀、工具输出会不会在三轮之后淹没用户目标。仓库里推荐在 70%-80% 利用率附近触发 compaction，本质上就是承认一个事实：系统不能把 context 当成无限资源来用，而必须像管理 CPU、内存、缓存一样管理它。

本章最重要的结论是：Context Engineering 的目标不是把更多信息搬进模型，而是把更有决策价值的信息，以更合理的顺序和时机搬进模型。Prompt 只是这个系统里的一个入口，不是全部。真正成熟的 agent 设计，会把指令、工具、文档、历史、外部输出一起看作一个待调度的注意力系统。只有从这个层次理解，你后面才会真正看懂为什么会有 degradation、compression、optimization、filesystem context 和 multi-agent isolation 这些章节。

## 学习检查

1. 为什么说 “更长的 context window” 不是 Context Engineering 的充分条件？
2. 在 agent 场景里，为什么 tool outputs 常常比 user messages 更值得优先管理？
3. Progressive disclosure 为什么是一种装载策略，而不是压缩策略？
