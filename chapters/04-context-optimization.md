# 第 4 章：Context Optimization

## 章节定位

本章处理“如何持续把上下文变得更高信号”，重点不是摘要，而是重新安排信息进入方式。

## 对应官方 skill

- `skills/context-optimization/SKILL.md`

## 必读材料

- `skills/context-optimization/SKILL.md`
- `README.md`

## 问题

知道 context 会退化和需要压缩，还不够。工程师还要决定：哪些输出该遮蔽、哪些内容该重排、哪些阶段该分区。

## 核心论点

Optimization 的重点不是让上下文“更短”，而是让高价值信息在当前时刻更容易被模型稳定利用。

## 定义

Context Optimization 是对当前上下文进行持续整理、裁剪、遮蔽、重排和分区，以提升有效注意力利用率的工程实践。它不是单次压缩动作，而是围绕“让高信号信息更容易被模型稳定利用”展开的一整套运行时策略。

如果 compression 更偏向“历史太多怎么办”，optimization 更偏向“当前应该怎样组织上下文，才不让模型被低价值内容拖垮”。

## 机制

重点解释：

- compaction
- observation masking
- KV-cache ordering
- context partitioning

## 技术模式

- stable-prefix ordering
- mask verbose outputs
- partition by task phase
- optimize after 70% utilization

## 案例证据

- `x-to-book-system` 的 raw tweet masking
- `digital-brain-skill` 的模块化加载

## 边界比较

### Optimization vs Compression

- Optimization 是广义运行时调度。
- Compression 是其中一类在高压状态下的缩减动作。
- 不是所有 optimization 都需要生成 summary。

### Masking vs Deletion

- Masking 是把原始内容变成可回取引用。
- Deletion 是直接失去访问路径。
- 前者保留按需恢复能力，后者通常破坏任务连续性。

## 反模式

- 把 optimization 当成 summary 同义词
- 不区分稳定前缀与动态内容
- 让原始工具输出反复污染主上下文

## 写作练习

写 800-1200 字，回答：

“为什么 observation masking 是 agent 系统里最容易被低估、但最有效的 Context Engineering 技术之一？”

## 章节草稿

经过前两章，我们已经知道两件事：第一，上下文会退化；第二，长任务必须压缩。但如果工程做到这里就停，系统仍然会很笨，因为大量问题并不是来自“历史太长”，而是来自“当前上下文组织得太差”。`context-optimization` skill 的意义就在这里，它把 Context Engineering 从被动补救推进到主动调度。

本章的起点是一个很朴素的判断：context quality matters more than quantity。很多团队喜欢追求更大的窗口、更长的日志、更全的检索结果，但模型真正需要的不是“尽可能全”，而是“对当前决策最有帮助”。Optimization 的任务，就是把这条原则落实成具体动作。仓库把这些动作概括为 compaction、observation masking、KV-cache optimization 和 context partitioning。它们分别对应不同的浪费来源。

先看 compaction。它和上一章 compression 很接近，但这里更强调它作为运行时优化手段的角色。Compression 讨论的是如何高保真地压旧上下文；Optimization 中的 compaction 更像调度阀门：当利用率接近阈值时，哪些部分应该先被摘要、哪些绝不能碰、哪些可以换成引用。这种 compaction 不是“事后整理”，而是系统在运行中持续维持高信号密度的手段。

真正最容易被低估的是 observation masking。仓库明确指出，tool outputs 往往占 agent context 的 80% 以上。也就是说，模型的大量注意力其实花在看命令输出、文件内容、检索原文和日志，而不是花在想问题。Observation masking 的思想非常直接：如果一个输出已经完成了它当时的决策使命，就不该继续以全文形式霸占上下文。应当把它替换成一个引用或高度压缩的关键结论，必要时再按引用回取。这个模式的价值不在于“偷懒不看原文”，而在于让原文从持续负担变成按需资产。

`x-to-book-system` 是一个极好的证据。这个案例里最重的不是 orchestrator 的思考，而是海量 tweet 数据。如果原始 tweet 一层层穿过 orchestrator、analyzer、writer，整个系统很快就会被数据量压垮。仓库给出的解决方式不是“写一个更好的 prompt”，而是 observation masking + filesystem coordination：raw tweet 不进入核心代理上下文，而是写到外部存储，需要的阶段再分批读取，后续流转的是 summary 而不是原文。这就是优化，而不是压缩。

KV-cache optimization 则把问题推进到更底层。它关心的不是“内容有没有用”，而是“哪些前缀稳定、可以重复利用”。把 system prompt、tool definitions、稳定模板放前面，把动态内容放后面，不只是为了结构清晰，也为了缓存命中率。很多工程师把 prompt 顺序当成美观问题，但从 optimization 视角看，顺序直接影响成本和延迟。

最后是 context partitioning。它代表一种更激进的优化思路：不要总想着在一个上下文里把一切摆平，而应该主动把任务拆进多个上下文，让每个上下文只处理自己该处理的部分。到了这里，你已经可以看出它和后面 multi-agent chapter 的衔接了。Optimization 的终点之一，就是承认有些问题不是再压再排就能解决，而必须从架构层面隔离。

因此，本章要建立的核心判断是：compression 是“把历史缩得还能用”，optimization 是“让当前上下文更值得被看”。前者解决续航，后者解决效率；前者更多处理存量，后者同时处理存量与增量。真正高水平的 agent system 往往不是因为模型更聪明，而是因为它让模型持续工作在一个更干净、更高信号、更少重复负担的上下文环境里。这就是 optimization 的工程价值。

## 学习检查

1. 为什么 observation masking 往往比继续调 prompt 更有效？
2. KV-cache ordering 解决的是哪一类问题？
3. 什么时候应该从 optimization 升级到 partitioning？
