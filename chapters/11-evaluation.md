# 第 11 章：Evaluation

## 章节定位

本章是验证层入口，负责回答“你怎么知道自己真的做对了”。

## 对应官方 skill

- `skills/evaluation/SKILL.md`

## 必读材料

- `skills/evaluation/SKILL.md`
- `examples/llm-as-judge-skills/README.md`

## 问题

没有评估，context engineering 很容易退化成玄学。本章解决“如何把设计目标变成可检验标准”。

## 核心论点

Evaluation 不是项目末尾的验收动作，而是前面所有 context 设计的反向约束。没有评估，所有“优化”都只是主观感觉。

## 定义

Evaluation 指的是：用明确的质量维度、测试样本、评分规则和持续比较机制，判断一个 agent system 是否真正达成了预期效果，并找出变化是改善还是退化。

对于 Context Engineering 来说，evaluation 的重点不是验证模型会不会回答，而是验证某种上下文设计、工具结构、记忆策略或多 agent 架构，是否真的提升了结果质量、效率和稳定性。

## 机制

重点解释：

- rubric design
- test set design
- context engineering evaluation
- continuous evaluation

## 技术模式

- outcome-focused evaluation
- multi-dimensional rubric
- representative test sets
- evaluation attached to design changes

## 案例证据

- `llm-as-judge-skills` 的整体结构
- `x-to-book-system` 中对 source accuracy / coherence 的多维评分

## 边界比较

### Evaluation vs Demo

- Demo 证明“某次看起来能跑通”。
- Evaluation 证明“在一组任务和约束下，系统是否稳定达标”。
- Demo 是展示，evaluation 是判断。

### Evaluation vs Advanced Evaluation

- Evaluation 关注评估框架、rubric、test set、连续跟踪。
- Advanced Evaluation 关注 judge 技术本身如何实现、校准和去偏。
- 前者是评估系统设计，后者是评估引擎工程。

## 反模式

- 只看一次 demo
- 只做单一指标
- 没有人类复核触发条件

## 写作练习

写 800-1200 字，回答：

“为什么一个 agent system 的 Context Engineering 水平，最终必须通过评估体系而不是自我感觉来证明？”

## 章节草稿

到了第四周，我们终于来到一个特别关键、也最容易被忽视的部分：evaluation。很多团队在做 agent system 时，把评估理解为最后补几条 benchmark、跑几次 demo、看起来没问题就上线。`evaluation` 这份 skill 对这种做法的态度非常明确：如果没有系统评估，Context Engineering 很快就会退化成玄学，因为你根本不知道自己改的是不是有效、是改善了还是只是换了个表面样子。

为什么 evaluation 在 agent 系统里尤其重要？因为 agent 不是普通软件函数。它是非确定性的，可能通过不同路径到达相同结果，也可能在相似任务上表现出完全不同的稳定性。一个 agent 这次搜索了 3 个页面，下次可能搜索了 10 个页面；这次从工具 A 找到答案，下次可能从工具 B 找到。你不能用传统软件测试那种“必须按预定步骤执行”来评价它。仓库因此强调 outcome-focused evaluation，也就是：评价的重点是结果是否正确、过程是否合理，而不是路径是否完全一致。

这就引出多维 rubric 的必要性。agent 质量从来不是单一维度。一个回答可能事实准确，但不完整；可能内容完整，但引用不准；可能最终答案没错，但用了过多无效工具调用。仓库给出的框架非常务实：至少要从 factual accuracy、completeness、citation accuracy、source quality、tool efficiency 等维度去看。也就是说，evaluation 不是一个总分，而是一张质量剖面图。

`x-to-book-system` 恰好是很好的例子。它不是只看“这本书写出来了吗”，而是进一步拆成 Source Accuracy、Thematic Coherence、Completeness、Insight Quality、Readability 五个维度。这种做法非常值得学，因为它把“结果像不像样”拆成了可以被解释、被比较、被优化的不同面向。对于 Context Engineering 来说，这一点尤其重要：你需要知道一个设计改动到底改善了 factual grounding，还是只是让 prose 看起来更顺。

本章的第二个关键点是 test set design。评估如果只挑最好看的几个样例，几乎一定会误导。仓库建议按复杂度分层：simple、medium、complex、very complex。这个建议背后有一个非常扎实的工程逻辑。因为 context engineering 的很多问题，不会在简单样本上暴露，只会在长链路、多工具调用、高歧义、长上下文任务里出现。你如果不故意设计复杂样本，很多退化和边界问题根本看不见。

还有一个经常被低估的点，是 evaluation 与 token budget 的关系。仓库提到 BrowseComp 的 95% finding，其中 token usage 解释了大部分性能差异。这不是让我们得出“多花 token 就行”的浅结论，而是提醒我们：评估必须在现实资源约束下进行。一个系统在无限预算下表现好，不代表它在真实产品预算下也成立。对 Context Engineering 而言，这意味着 evaluation 不只是看质量，还要看质量是以什么资源代价换来的。

因此，这一章最重要的结论是：evaluation 不是后置验证，而是前置设计的裁判。你对 context 的任何判断，无论是 compression、optimization、filesystem offloading、memory retrieval，还是 multi-agent coordination，最后都必须通过 evaluation 才能从“方法”变成“证据”。没有这一层，系统再复杂，也只是工程师对自己设计的信心；有了这一层，才开始变成可以持续改进的工程实践。

## 学习检查

1. 为什么 agent system 需要 outcome-focused evaluation？
2. 为什么多维 rubric 比单一总分更适合 agent 评估？
3. 为什么评估必须覆盖不同复杂度层级的任务？
