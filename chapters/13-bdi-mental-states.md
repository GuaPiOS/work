# 第 13 章：BDI Mental State Modeling

## 章节定位

这是压轴章。作用不是把读者拉进本体论细节，而是展示 Context Engineering 可以继续上升为认知状态建模。

## 对应官方 skill

- `skills/bdi-mental-states/SKILL.md`

## 必读材料

- `skills/bdi-mental-states/SKILL.md`
- `skills/memory-systems/SKILL.md`
- `skills/multi-agent-patterns/SKILL.md`

## 问题

当系统不仅要“看见信息”，还要“解释自己为什么这样行动”时，普通的上下文堆叠已经不够。本章回答为什么 BDI 可以作为 Context Engineering 的高阶抽象。

## 核心论点

BDI 不是要替代 Context Engineering，而是把它推进到“可解释的认知状态建模”层。它让系统不只保存信息，还能表达“相信什么、想要什么、决定做什么”。

## 定义

BDI Mental State Modeling 指的是：把外部世界状态、任务目标和行动计划，分别建模为 belief、desire、intention 等可追踪的认知状态，并通过显式关系连接感知、动机、计划和执行。

对 Context Engineering 来说，它的意义在于：context 不再只是待加载的信息集合，而可以进一步被组织成有认知语义的内部状态结构，从而支持解释、审计与更稳定的 deliberation。

## 机制

重点解释：

- belief
- desire
- intention
- mental processes
- goal-directed planning
- explainability

## 技术模式

- transform world state into mental state
- maintain traceable reasoning chains
- bind plans to explicit intentions
- use formal state to support explanation

## 案例证据

- `bdi-mental-states` skill 自身的 cognitive chain pattern
- 回连 memory 与 multi-agent 的状态协调问题

## 边界比较

### BDI vs 普通 Context Stacking

- 普通 context stacking 只是把相关信息堆到窗口里。
- BDI 试图把信息区分为 belief、desire、intention 及其关系。
- 前者偏输入组织，后者偏认知结构。

### BDI vs Planning

- Planning 主要回答“下一步做什么”。
- BDI 还回答“为什么会有这个目标、这个计划由哪些 belief 支撑、它满足了哪个 desire”。
- 也就是说，BDI 比 planning 多了一层可解释语义。

## 反模式

- 把 BDI 当成入门 prerequisite
- 只有术语，没有系统接口
- 形式化很强，但不能落到 agent 行动和解释上

## 写作练习

写 800-1200 字，回答：

“为什么 BDI 不是要替代 Context Engineering，而是把它推进到可解释认知架构的层次？”

## 章节草稿

把 BDI 放在压轴章，是有意为之。如果一开始就讲 belief、desire、intention，很多人会误以为 Context Engineering 是一门高度形式化、只有做 ontology 才算入门的学问。其实不是。前面 12 章已经证明，Context Engineering 首先是一门非常工程化的 discipline：你在管理 context 组成、退化、压缩、优化、工具、文件、记忆、架构和评估。那为什么最后还要回到 BDI？因为当系统开始不仅要“看见”信息，还要“解释自己为什么这么做”时，纯粹的信息装载已经不够了。

`bdi-mental-states` skill 做的事情，就是把外部世界状态翻译成认知状态。Belief 表示代理认为什么是真的，Desire 表示它希望达成什么，Intention 表示它真正承诺要做什么。这个划分听起来像哲学，但在工程上非常有用。因为很多 agent 的不稳定，并不是不会规划，而是没有清楚地区分“知道了什么”“想实现什么”“已经决定做什么”。当这三件事混在一起时，系统就容易在长任务中丢目标、变计划、互相冲突却没有解释能力。

仓库里的 cognitive chain pattern 给了一个非常清晰的最小例子：belief store_open 促成 desire buy_groceries，再支持 intention go_shopping，并最终关联到具体 plan。这个结构的价值，不在于它看上去很学术，而在于它把一条原本隐含在自然语言里的推理链，显式写成了可以追踪、查询、验证的状态关系。于是系统不只是“做了一个动作”，而是能够回答：“我为什么形成这个目标？我基于什么 belief 做了这个 commitment？这个 intention 对应哪条 plan？”

这和前面几章其实是连续的。memory systems 解决的是知识如何跨时间取回；multi-agent patterns 解决的是不同上下文如何协同；evaluation 解决的是结果如何判断。BDI 则把这些能力再往上收束成认知视角：一个多 agent 系统不只是多个上下文在跑，还可能是多个 belief structures、goal commitments 和 plan states 在交互。一个 memory system 不只是保存事实，还可能为 belief 提供时序支持。这样一来，Context Engineering 开始从“输入管理”升级到“认知状态管理”。

这里特别值得强调的是 explainability。现代 agent 系统经常给人一种“看起来会做，但说不清为什么”的感觉。BDI 的价值之一，就是给出一种更结构化的说明方式。系统不只是回溯日志说“我执行了这些步骤”，而是能说明“因为我感知到这个 world state，所以形成了这个 belief；因为这个 belief 激发了这个 desire，所以我承诺了这个 intention；因为这个 intention 被 plan 支持，所以我执行了这些 task”。这比普通日志更接近 reasoning audit。

当然，这一章也不应该被神化。不是所有 agent 项目都需要 BDI。本书把它放在最后，就是为了建立一个正确分层：先把 Context Engineering 作为工程 discipline 学会，再把 BDI 看作其中一条高阶延展路径。对多数系统来说，你完全可以在没有正式 BDI ontology 的情况下，依然做好 context budgeting、filesystem offloading、memory retrieval 和 evaluation。只有当系统开始要求更强解释性、复杂目标管理或 neuro-symbolic integration，BDI 才会成为值得引入的下一层结构。

因此，本章的结论是：BDI 不是 Context Engineering 的前提，而是它的升维版本。它让我们看到，Context Engineering 最终不一定停留在“哪些信息该放进窗口里”，还可能继续走向“这些信息在系统内部被组织成怎样的认知现实”。这正是它作为压轴章的价值。

## 学习检查

1. 为什么 BDI 适合放在全书最后，而不是最前面？
2. BDI 相比普通 planning，多增加了哪一层解释能力？
3. 为什么说 BDI 是 Context Engineering 的升维，而不是替代？
