# 第 5 章：Tool Design for Agents

## 章节定位

本章把 tools 从“功能接口”重新定义成“上下文契约”。

## 对应官方 skill

- `skills/tool-design/SKILL.md`

## 必读材料

- `skills/tool-design/SKILL.md`
- `examples/digital-brain-skill/HOW-SKILLS-BUILT-THIS.md`

## 问题

为什么很多 agent 不是不会推理，而是被糟糕的工具定义误导？本章解决“tool 为什么是 context engineering 的一部分”。

## 核心论点

Tool 不是附加功能，而是 agent 与世界交互的上下文契约。工具设计得含混，agent 的推理再强也会在行动层失真。

## 定义

Tool Design for Agents 的核心，不是把 API 暴露给模型，而是把“什么时候该调用、调用时要提供什么、返回后该如何继续”编码进工具契约里。因为模型不是按强类型编译器方式理解接口，而是通过描述、示例、命名和错误反馈去推断工具意图，所以工具定义本身就是上下文的一部分。

从 Context Engineering 视角看，工具描述不仅决定功能可用性，还直接决定 agent 会把注意力投向哪些动作、如何理解 workflow，以及在失败时是否有恢复路径。

## 机制

重点解释：

- tool as contract
- consolidation principle
- response format optimization
- actionable error messages

## 技术模式

- single comprehensive tool
- description as prompt
- error-guided recovery
- namespace discipline

## 案例证据

- `x-to-book-system` 中从 15+ 工具收敛到 3 个 consolidated tools
- `llm-as-judge-skills` 中 tool definitions 的结构化实现

## 边界比较

### Tool Design vs 普通 API Design

- 普通 API 主要面向开发者，假设调用者能读文档、理解 schema、手工纠错。
- Agent tool design 面向语言模型，必须把调用条件、输入形状和错误恢复直接写进上下文。
- 因此 tool description 不是注释，而是行为引导。

### Consolidation vs Over-Bundling

- Consolidation 是减少重叠与歧义，让一个工具覆盖一个清晰 workflow。
- Over-bundling 是把互不相干的行为硬塞进一个巨大工具，反而增加判断成本。
- 关键标准不是工具越少越好，而是“人能否清晰说出什么时候该用哪个”。

## 反模式

- 一堆功能重叠的小工具
- 工具描述只写“做什么”，不写“什么时候用”
- 错误信息不能指导恢复

## 写作练习

写 800-1200 字，回答：

“为什么一个工具集合的复杂度，往往先伤害 agent 的上下文判断，再伤害它的功能调用？”

## 章节草稿

很多团队在做 agent 时，会把工具层当成一件很技术、很中性的事情：把后端能力包成函数，挂给模型调用，就算完成了接入。`tool-design` 这份 skill 恰好在反对这种想法。对 agent 来说，工具不是中性的 API 暴露，而是它理解世界、发起行动、判断下一步的接口契约。契约写得差，agent 不是简单地“偶尔用错”，而是会系统性地把错误工具放进自己的推理路径里。

这一章最重要的定义是：tools are contracts between deterministic systems and non-deterministic agents。对人类程序员来说，工具出错时可以回头查文档、看类型、读源码、跑调试。对模型来说，工具的大部分意义来自它在当前上下文里看到的描述。也就是说，工具说明本身就是 prompt engineering，只不过它不是在指导“如何回答”，而是在指导“如何行动”。

这也是为什么仓库把 consolidation principle 放到非常核心的位置。原则很简单，但非常有力：如果一个人类工程师都说不清在某种情况下到底该用哪个工具，模型就更不可能稳定做对。很多 agent 工具集失败，并不是因为模型太笨，而是因为工具集合本身存在重叠、模糊和边界冲突。例如你同时提供 `search_users`、`lookup_profile`、`find_customer`、`query_account`，人类都要犹豫，模型当然更容易乱选。

`x-to-book-system` 正好给了一个很强的反例说明。这个案例没有把所有动作拆成十几种微工具，而是收敛成三类综合工具：`x_data_tool`、`memory_tool`、`writing_tool`。这么做不是偷懒，而是在主动压缩工具选择空间。对于 agent 而言，这等于减少了 action context 的噪声。每少一个描述重复、边界模糊的工具，就少一层选择混乱和上下文负担。

工具设计的第二个关键点，是 tool description as prompt。一个好的描述至少要回答四件事：这个工具做什么，什么时候该用，它接受什么输入，它会返回什么。很多低质量工具说明只回答了第一件事，导致模型必须自己猜后面三件事。这样一来，工具层不是在帮助推理，而是在迫使模型额外做一轮隐式推理。工程上，这等于把本来可以显式编码的约束，转嫁成模型的概率性判断。

第三个关键点是 error message design。对 agent 来说，错误信息不是给开发者看的日志，而是恢复路径的一部分。如果工具只返回“invalid request”，模型很难知道是参数格式错了、上下文不够、对象不存在，还是应该重试。好的错误消息要能支持 self-repair，比如告诉它正确格式、重试条件、缺失字段或下一步动作建议。换句话说，错误信息本身也是上下文资产。

这章还有一个更激进但很重要的观点，叫 architectural reduction。仓库明确指出，很多时候，与其发明一大堆定制工具，不如直接给 agent 一个足够清晰的文件系统与标准命令能力。因为文件系统是模型已经很熟悉的抽象，`ls`、`find`、`grep`、`cat` 这类原语往往比包装过度的业务工具更稳定。这不是反工具，而是在提醒我们：工具设计的目标不是“把一切封装得很精致”，而是“让 agent 以最少歧义接触真实世界”。

因此，本章真正要建立的判断是：工具设计本质上是上下文设计。工具越多，不一定能力越强；描述越短，不一定越高效；封装越厚，不一定越安全。真正好的工具层，会让 agent 更少猜测、更少选错、更容易恢复，并且用更少 token 理解更清晰的行动空间。这就是为什么 tool design 不该被放在实现细节里，而应该被放进 Context Engineering 的主线。

## 学习检查

1. 为什么说 tool description 本身就是一种 prompt engineering？
2. Consolidation principle 想解决的根本问题是什么？
3. 为什么“更多工具”不必然带来“更强 agent”？
