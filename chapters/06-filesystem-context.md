# 第 6 章：Filesystem Context

## 章节定位

这是整套课程的工程地面层。本章解释为什么 filesystem 不是临时方案，而是 context engineering 的基础设施。

## 对应官方 skill

- `skills/filesystem-context/SKILL.md`

## 必读材料

- `skills/filesystem-context/SKILL.md`
- `examples/digital-brain-skill/HOW-SKILLS-BUILT-THIS.md`

## 问题

如果上下文装不下，最自然的外置容器是什么？本章回答为什么很多高质量 agent system 最终都会回到文件系统。

## 核心论点

Filesystem 不是权宜之计，而是最通用、最稳定、最可发现的外置上下文层。它让 agent 把“必须长期可访问的信息”从上下文窗口中搬出去，同时保留按需读取的能力。

## 定义

Filesystem Context 指的是：把工具输出、计划、记忆、技能、日志和子代理结果以文件形式持久化，使 agent 不必把所有信息一直带在上下文里，而是通过搜索和按需读取来完成动态上下文发现。

它的价值不只是“能存更多”，而是“能让上下文从静态预装变成动态发现”。这也是它区别于简单存档或日志落盘的地方。

## 机制

重点解释：

- scratch pad
- plan persistence
- sub-agent communication
- dynamic skill loading
- log persistence

## 技术模式

- write outside context
- read just in time
- persist plans and artifacts
- use files as coordination substrate

## 案例证据

- `digital-brain-skill` 的 3 层加载
- `x-to-book-system` 的 file coordination

## 边界比较

### Filesystem Context vs 把内容直接塞进消息历史

- 消息历史适合保留当前对话轨迹。
- 文件系统适合承载大体量、低频回看、需要精确检索的内容。
- 前者天然累积，后者支持 selective retrieval。

### Filesystem Context vs Memory Systems

- Filesystem Context 关注的是外置、发现、读取、持久化机制。
- Memory Systems 关注的是跨会话知识如何建模、检索、合并和保持时序有效。
- 文件系统可以是 memory 的实现地面层，但不自动等于 memory architecture。

## 反模式

- 把 filesystem 仅仅当成“先凑合一下”
- 让共享状态只能在会话上下文中传播
- 不建立可发现的目录结构与命名约定

## 写作练习

写 800-1200 字，回答：

“为什么 file system 在很多 agent 系统里比向量库更像真正的工作记忆地面层？”

## 章节草稿

很多人第一次看到“用文件系统做 context engineering”时，会下意识觉得这只是一个临时替代方案，好像等以后接上数据库、向量库或更高级的 memory framework，就应该把它淘汰掉。这个判断在本仓库语境里是反的。`filesystem-context` 的核心观点是，文件系统不是低配版 memory，而是 agent 最天然的动态上下文基础设施。

原因很简单。上下文窗口再大，也不适合长期背着所有信息跑。真正高质量的 agent 需要一个外部层，能把大量信息写出去、保留下来、以后再按需读回来。文件系统恰好同时满足这几件事：它通用、持久、可搜索、可分层、可版本化，而且模型对它非常熟悉。对 agent 来说，`ls`、`glob`、`grep`、`read_file` 这些动作不只是文件操作，而是一整套 context discovery 机制。

仓库里把这一点说得很清楚：filesystem 提供的是 single interface through which agents can flexibly store, retrieve, and update an effectively unlimited amount of context。这里的重点不是“无限大”，而是“flexibly retrieve”。也就是说，文件系统真正有价值的地方不在存储容量，而在于 agent 可以不把信息一直背在身上，而是在需要时重新发现它。

最直接的应用就是 scratch pad。工具输出往往非常肥，尤其是搜索结果、日志、数据库查询和长文件内容。如果这些内容全部进入 message history，它们就会永久占据上下文预算。文件系统方案的思路则完全不同：大输出写入文件，只把摘要和引用放进上下文。需要细节时，再用 `grep` 或局部读取回看。这和上一章的 observation masking 形成了天然配合，只不过这里强调的是“引用落在哪里”。答案就是：落到可搜索的文件里。

第二个关键模式是 plan persistence。长任务失败，很多时候不是因为模型不会做，而是因为走着走着忘了最初计划。把计划写进结构化文件，让 agent 在关键节点重新读取，等于把任务目标从易漂移的会话上下文，转移到了稳定外部状态。仓库把这件事称为 manipulating attention through recitation，本质上是在利用“可重新读取”来抵抗上下文漂移。

`digital-brain-skill` 是这章最好的正例。它并没有把所有知识一次性塞进主文件，而是建立了 L1 到 L3 的层次：`SKILL.md` 负责总览，模块文件负责域级说明，具体数据文件负责细节。这种三层设计不是文档结构美学，而是 progressive disclosure 的工程实现。稳定元信息常驻，细节内容按任务进入。结果就是：内容创作任务只加载 identity 和 content 模块，不用把 network、operations、knowledge 全背进当前 context。仓库给出的数字很直接，token 从 5000+ 降到约 650。

第三个关键模式是 sub-agent communication via filesystem。在多代理系统里，如果所有子代理都靠消息链层层汇报，就很容易出现 telephone game 问题：每一层都在摘要上一层，信息不断损失。文件系统提供了一种更直接的协作方式：每个代理把结果写到自己的工作区，协调者直接读取源文件，而不是读取“别人对源文件的转述”。`x-to-book-system` 就是这样避免 orchestrator 被原始数据淹没的。

理解这章时，最重要的边界是：filesystem context 不等于 memory systems。文件系统回答的是“信息外置后如何被发现和读取”；memory systems 回答的是“跨时间、跨会话、跨实体的信息如何被建模和检索”。前者更像地面交通系统，后者更像城市规划。你可以在文件系统上做 memory，但文件系统本身不自动提供实体关系、时间有效性或语义检索。

因此，本章的结论应该很明确：文件系统之所以重要，不是因为它土，而是因为它让 agent 拥有了外置上下文的最小完备基础设施。只要一个系统需要长任务、工具输出、计划复用、技能动态加载或多代理共享状态，filesystem context 就不是旁路，而是核心设计层。

## 学习检查

1. 为什么说文件系统的核心价值在“动态发现”而不是“能存很多”？
2. Scratch pad 和 message history 的职责差异是什么？
3. 为什么 `digital-brain-skill` 能作为 filesystem context 的代表案例？
