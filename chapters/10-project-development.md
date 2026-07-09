# 第 10 章：Project Development Methodology

## 章节定位

本章把前面的技能整合成项目方法论，防止学习停留在概念层。

## 对应官方 skill

- `skills/project-development/SKILL.md`

## 必读材料

- `skills/project-development/SKILL.md`
- `examples/book-sft-pipeline/README.md`
- `examples/x-to-book-system/README.md`

## 问题

很多 LLM 项目不是死在模型能力，而是死在任务选择和架构起步错误。本章回答“如何从 0 到 1 设计一个值得做的 agent 项目”。

## 核心论点

成熟的 Context Engineering 不从 prompt 开始，而从 task-model fit 开始。先确认模型是否值得用于这个问题，再决定用什么架构、什么工具、什么状态管理。

## 定义

Project Development Methodology 指的是：在构建 LLM 或 agent 系统前，先验证任务与模型能力是否匹配，再用分阶段、可缓存、可调试的方式组织数据流、LLM 调用和输出解析，逐步增加复杂度。

它不是通用项目管理框架，而是专门面向 LLM 系统的开发方法论。它要解决的不是“怎么排期”，而是“什么该让模型做、什么不该让模型做、什么时候该引入更复杂的 agent 架构”。

## 机制

重点解释：

- task-model fit
- manual prototype
- staged pipeline
- file system as state machine
- single vs multi-agent decision

## 技术模式

- validate manually before automating
- use acquire/prepare/process/parse/render
- persist stage outputs
- add complexity only after fit is proven

## 案例证据

- `book-sft-pipeline` 的 pipeline 结构
- `x-to-book-system` 的 architecture decomposition

## 边界比较

### Project Development vs Prompt Tuning

- Prompt tuning 默认问题已经成立，只优化表达。
- Project development 先判断问题是否应该交给模型。
- 前者关注输出改善，后者关注项目成立条件。

### Single Pipeline vs Multi-Agent Architecture

- Single pipeline 适合独立批处理、线性阶段和更低复杂度。
- Multi-agent 适合超出单上下文容量、需要并行探索或角色隔离的任务。
- 决策标准不是“更先进”，而是任务是否真需要额外 coordination cost。

## 反模式

- 没做 manual prototype 就开建
- 一开始就用最复杂架构
- 把不适合 LLM 的问题强行 agent 化

## 写作练习

写 800-1200 字，回答：

“为什么真正成熟的 Context Engineering，不是从 prompt 开始，而是从 task-model fit 开始？”

## 章节草稿

在很多 LLM 项目里，最大的失败不是 prompt 写得不好，也不是模型能力不够，而是项目一开始就选错了问题。`project-development` skill 的第一个动作不是建系统，而是 task-model fit recognition。这个顺序特别重要，因为它在提醒我们：不是所有看上去“可以让 AI 做”的任务，都值得交给 LLM 或 agent。

仓库列出的判断标准非常实用。LLM 更适合做跨来源综合、带 rubric 的主观判断、自然语言生成、允许一定误差的批处理任务；不适合做精确计算、严格实时、必须完全确定、或者高度依赖隐藏私有数据的工作。这个判断不是抽象理念，而是直接决定你后面该不该写代码。如果任务本身和模型能力错位，后面无论是 tool design、memory 还是 multi-agent，都只是在为错误方向增加复杂度。

所以这一章强调的第二个关键动作是 manual prototype。也就是，在自动化之前，先拿一个代表性样本去手工喂给目标模型，看看它到底会不会、效果大概到什么程度、失败模式是什么。这个动作非常朴素，但极其重要。它会在几十分钟内回答一个价值极高的问题：这个项目是值得继续搭，还是应该马上止损。很多工程浪费，其实都发生在“手工试一下就能知道不行”的地方。

一旦 task-model fit 成立，方法论就转入 pipeline architecture。仓库给出的 canonical pipeline 很清楚：acquire → prepare → process → parse → render。这个顺序看起来像普通数据流水线，但对 LLM 项目尤其重要，因为它把“贵且不稳定的 LLM 调用”从其他确定性阶段隔离出来。这样一来，你可以重复调试 prepare、parse 和 render，而不用每次重跑最贵的那一步。

`book-sft-pipeline` 是这里最好的案例。它把整套工作拆成 extraction、segmentation、instruction generation、dataset construction、training、validation。你可以把它看成 acquire/prepare/process/parse/render 的扩展版。这个案例的价值，不只是它做了一个风格迁移训练系统，而是它示范了怎样把一个看似“大而模糊”的生成任务，拆成多个有清晰边界、可单独验证、可反复迭代的阶段。对写书式学习来说，它也很有启发：复杂系统不是靠一次性大 prompt 搞定，而是靠阶段化设计逐层收束。

本章的另一个关键视角，是 file system as state machine。也就是说，项目状态最好不要一开始就塞进复杂数据库或内存状态机，而是用文件存在与否、目录阶段产物、可读中间文件来表示“进行到哪一步”。这和前面的 filesystem context 形成了非常自然的衔接。因为在 LLM 项目里，最贵、最难 debug 的部分往往不是 deterministic logic，而是那一次已经花钱跑出来的模型结果。只要中间文件可见，你就拥有了缓存、调试和重跑边界。

这一章还必须把“要不要用 multi-agent”这个问题从偏好里拉出来。仓库说得很清楚，multi-agent 的主理由仍然是 context isolation，而不是“项目显得更高级”。所以如果一个任务天然是批处理、单 item 独立、阶段线性清晰，那么 single pipeline 往往已经足够。只有当任务开始超出单上下文容量、需要并行探索、或者阶段间的上下文差异非常大时，多 agent 才开始有正收益。

因此，Project Development 这一章真正要建立的，是一套起步顺序：先判断问题是否适合模型，再手工试一个样本，再用阶段化流水线组织成本和状态，再根据上下文压力决定是否升级到多 agent 或 hosted runtime。这样一来，Context Engineering 才不会退化成“给一个本来就不适合模型的问题，搭越来越复杂的外壳”。成熟的方法论，不是更快开始写 prompt，而是更早知道该不该开始。

## 学习检查

1. 为什么 task-model fit 应该先于任何自动化？
2. `book-sft-pipeline` 为什么是 project development 的典型案例？
3. 在什么条件下，single pipeline 比 multi-agent 更合适？
