# 第 8 章：Multi-Agent Architecture Patterns

## 章节定位

本章是系统架构部分的入口。核心论点固定为：多 agent 首先是 context isolation 技术，其次才是工作分解方式。

## 对应官方 skill

- `skills/multi-agent-patterns/SKILL.md`

## 必读材料

- `skills/multi-agent-patterns/SKILL.md`
- `examples/x-to-book-system/README.md`
- `examples/x-to-book-system/SKILLS-MAPPING.md`

## 问题

为什么系统变复杂后，单 agent 即使还能工作，也开始越来越不可靠？本章回答为什么要用多 agent，以及什么时候不该用。

## 核心论点

多 agent 的首要价值不是“更像团队分工”，而是把一个过载的 context 拆成多个可控 context。它首先是一种上下文隔离技术，其次才是一种任务组织方式。

## 定义

Multi-Agent Architecture Patterns 指的是：将复杂任务分配给多个拥有独立上下文窗口、独立工具集或独立职责边界的 agent，通过协调机制完成单一上下文难以稳定完成的任务。

从 Context Engineering 角度看，多 agent 的本质不是模拟公司组织结构，而是通过上下文隔离减少注意力稀释、上下文污染和工具冲突，让每个 agent 在更窄、更干净的任务面上工作。

## 机制

重点解释：

- supervisor/orchestrator
- swarm
- hierarchical
- context isolation
- telephone game problem

## 技术模式

- isolate by subtask and context
- route through summaries, not raw data
- store shared state outside coordinator context
- select architecture by task decomposition

## 案例证据

- `x-to-book-system` 中 orchestrator 与 phase agents 的分工
- `book-sft-pipeline` 中 staged pipeline 对复杂任务的拆分思想

## 边界比较

### Multi-Agent vs Single Agent with More Tokens

- 给单 agent 更多 token，只是在同一个拥挤上下文里继续塞内容。
- 多 agent 则是主动把任务分裂到多个独立上下文中。
- 前者增加容量，后者改变结构。

### Supervisor vs Swarm

- Supervisor 强在控制、检查点和阶段性质量门。
- Swarm 强在灵活探索与直接 handoff。
- 选择标准不是偏好，而是任务是否有清晰分解与中央协调需求。

## 反模式

- 角色扮演式多 agent
- 所有 agent 都吃同一份大上下文
- supervisor 直接转述大量 worker 原始内容

## 写作练习

写 800-1200 字，回答：

“为什么多 agent 的价值，不在于更像公司组织，而在于把一个过载 context 拆成多个可控 context？”

## 章节草稿

很多人对多 agent 的第一反应是“把一个人做的事分给几个人做”。这个说法不完全错，但会把问题讲浅。`multi-agent-patterns` 里最值得抓住的一句话是：sub-agents exist primarily to isolate context, not to anthropomorphize role division。也就是说，多 agent 的核心价值不是组织学，而是上下文工程。

为什么会这样？因为单 agent 在任务复杂度上升时，最先遇到的不是“不会思考”，而是 context bottleneck。历史消息越来越长，检索资料越来越多，工具输出越堆越厚，结果就是一个上下文里既有原始数据、又有中间计划、又有失败记录、又有多轮决策。到这一步，即使模型本身还很强，它也要在一个混杂环境里持续切换注意力，失误率自然上升。

多 agent 提供的解决方案不是神秘的“集体智能”，而是更朴素的分区。让不同 agent 只看到与自己阶段相关的上下文：研究 agent 只关心搜索与资料，分析 agent 只关心抽象主题和模式，写作 agent 只关心局部内容生成，编辑 agent 只关心审阅和改写。每个 agent 都在更窄的任务面里工作，因此 attention budget 更集中，工具选择也更清晰。

`x-to-book-system` 是这一点最典型的案例。这个系统为什么采用 supervisor/orchestrator，而不是 swarm？不是因为“中台更高级”，而是因为它的工作流本身有清晰阶段：scrape、analyze、synthesize、write、edit。这样的任务天然适合中央协调，因为阶段之间存在质量门、状态依赖和人类监督需求。仓库映射文档里说得很明确，选择 supervisor 的原因是 sequential phases + quality gates。这个判断不是架构偏好，而是任务结构使然。

但 supervisor 也有一个非常经典的问题，就是 telephone game。也就是子代理把结果给协调者，协调者再转述给下一层或用户，信息在每一层摘要中逐渐失真。仓库特别提醒这一点，并给出工程性解决思路：让子代理结果尽量通过文件系统或直通机制保留原始保真，避免协调者成为所有信息的二次解释器。`x-to-book-system` 的做法就是：raw tweet 和 phase outputs 主要落到文件系统，orchestrator 只看阶段摘要，不搬运原始数据。

这也解释了为什么多 agent 不能简单理解成“多模型一起聊聊”。如果多个 agent 最终还是共享一份大上下文、依赖同一条消息链来同步状态，那你并没有真正获得隔离，只是引入了更多通信成本。真正有效的多 agent，一定有清晰的 isolation 机制：独立上下文、有限 handoff、文件系统共享状态或明确的 summary schema。

本章还必须面对一个现实：多 agent 很贵。仓库给出的 token economics 很直接，复杂多 agent 任务可能达到单 agent chat 的十几倍 token 消耗。所以我们不能把多 agent 当默认答案。它应该只在三种情况下变得值得：第一，任务天然可分阶段或可并行；第二，不同子任务确实需要不同工具和不同上下文；第三，单 agent 的上下文退化已经开始伤害质量。否则，多 agent 只是在用更多成本包装一个本可由单 agent 完成的流程。

因此，这一章真正要建立的判断是：多 agent 是一种 context partitioning architecture。它不是为“显得高级”而存在，也不是为模仿组织结构而存在。它服务于一个非常具体的工程目标：让不同推理过程在不同上下文中发生，减少互相干扰，并通过协调层把结果重新拼回任务目标。你只要抓住这一点，后面理解 hosted agents 和 project development 就会轻松得多，因为它们其实都在回答同一个问题：当单一上下文不再可靠时，系统该怎样重新组织工作。

## 学习检查

1. 为什么说多 agent 的本质是 context isolation，而不是角色扮演？
2. `x-to-book-system` 为什么更适合 supervisor，而不是 swarm？
3. Telephone game 问题说明了多 agent 系统的哪类风险？
