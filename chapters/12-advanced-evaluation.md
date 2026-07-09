# 第 12 章：Advanced Evaluation

## 章节定位

本章专注 LLM-as-a-judge 的系统化实现，作为评估工程化的高级章。

## 对应官方 skill

- `skills/advanced-evaluation/SKILL.md`

## 必读材料

- `skills/advanced-evaluation/SKILL.md`
- `examples/llm-as-judge-skills/README.md`

## 问题

有 rubric 还不够，很多系统真正卡在“自动评估怎样尽量不偏”。本章解决 judge pipeline 的可靠性问题。

## 核心论点

Advanced Evaluation 的重点不是“让 LLM 来打分”这么简单，而是把打分本身做成可校准、可解释、可去偏的工程系统。

## 定义

Advanced Evaluation 指的是：围绕 LLM-as-a-Judge 构建一套可重复、可比较、可解释的自动评估机制，并针对 direct scoring、pairwise comparison、rubric generation 和 bias mitigation 设计稳定的评分流程。

它不是 evaluation 的重复版本，而是 evaluation 的实现深化层。Evaluation 决定“评什么”，Advanced Evaluation 决定“自动怎么评得更可靠”。

## 机制

重点解释：

- direct scoring
- pairwise comparison
- position bias
- length bias
- rubric generation

## 技术模式

- choose eval method by task type
- swap positions in pairwise
- separate generation and evaluation models
- require evidence-bearing judgments

## 案例证据

- `llm-as-judge-skills` 的 tool / prompt / test structure
- `advanced-evaluation` skill 中的 bias mitigation 框架

## 边界比较

### Direct Scoring vs Pairwise Comparison

- Direct scoring 更适合 objective criteria，比如 factual accuracy、format compliance。
- Pairwise comparison 更适合 preference judgment，比如 tone、style、persuasiveness。
- 选错方法，评分波动和偏差会显著上升。

### Advanced Evaluation vs Human Review

- Advanced evaluation 负责规模化、一致性和快速反馈。
- Human review 负责边缘案例、低置信度案例和高风险决策兜底。
- 前者不能彻底替代后者，只能缩小后者的工作面。

## 反模式

- 一个评分提示走天下
- 把 subjective preference 当 objective scoring 做
- 不做 bias mitigation

## 写作练习

写 800-1200 字，回答：

“为什么 Advanced Evaluation 的重点不是让 LLM 来打分，而是让打分这件事本身变得可解释、可校准、可复核？”

## 章节草稿

如果说上一章解决的是“为什么必须评”，那么这一章解决的是“自动评这件事怎样才不至于自欺欺人”。很多团队一听到 LLM-as-a-Judge，就会自然地想成：再调用一次模型，让它给前一个模型打个分。`advanced-evaluation` skill 的价值，恰恰在于拆穿这种过度简化。LLM-as-a-Judge 不是一个技巧，而是一整个技术家族。不同任务要用不同 judge 方法，而且每一种方法都有自己常见的偏差。

仓库首先把 judge 方法分成两大类：direct scoring 和 pairwise comparison。这个划分特别重要，因为它不是实现选择，而是任务结构选择。Direct scoring 适合 objective criteria，比如事实正确性、格式遵从、是否覆盖指定要点。这类任务存在相对明确的判准，judge 只需要把响应映射到某个分值尺度。相反，pairwise comparison 更适合偏好判断，比如文风、可读性、说服力。因为这类任务很难定义一个绝对分值，却比较适合说“两个里面哪个更好”。

很多 judge 系统出问题，不是因为模型不够强，而是因为方法选错了。你让模型对创意性写作做绝对打分，评分会很飘；你让模型对格式合规性做 pairwise，效率又会变差。这就是为什么本章要强调 decision framework：先看任务有没有 objective ground truth，再看它是不是 preference judgment，而不是默认所有评估都用同一种提示模板。

Advanced Evaluation 的第二个核心，是 bias mitigation。仓库列得很清楚：position bias、length bias、self-enhancement bias、verbosity bias、authority bias。这些偏差如果不处理，judge 很容易变成“看上去很系统，实际上只是系统化地偏”。尤其在 pairwise comparison 里，position bias 几乎是默认存在的。因此仓库强烈推荐 position swap：把 A/B 顺序交换再评一次，如果前后不一致，就不能再装作这个结论很稳。

`llm-as-judge-skills` 这个案例把这些原则做成了可执行实现。它不仅有 `directScore`、`pairwiseCompare`、`generateRubric` 三类核心工具，还把 bias mitigation 写进了逻辑里，比如 pairwise comparison 自动 position swapping、要求 evidence-bearing justifications、结构化输出和测试用例覆盖。这一点非常关键，因为它说明 advanced evaluation 不是概念讨论，而是可以落成工具、prompt、agent、test 的完整工程层。

本章还要强调 rubric generation 的作用。很多人把 rubric 当成一个静态文档，但这里的意思更接近“评分协议生成器”。好的 rubric 会把模糊标准变成可观察特征、分值边界和边缘情况处理。没有 rubric，judge 更容易随感觉波动；有 rubric 但 rubric 太宽泛，也一样不可靠。所以 advanced evaluation 真正做的是把“标准”工程化，而不是把“打分”自动化。

因此，这一章的结论可以压成一句话：Advanced Evaluation 关心的不是能不能自动打分，而是自动打分是否值得相信。它通过方法选择、rubric 设计、偏差控制、置信度处理和测试验证，把 LLM-as-a-Judge 从一个看似聪明的技巧，变成一个可部署、可复核、可持续优化的系统能力。没有这一层，evaluation 很容易变成高频但低可信的数字噪声；有了这一层，评估才真正开始成为产品与研究可以依赖的反馈回路。

## 学习检查

1. 为什么说 LLM-as-a-Judge 是一组方法，而不是单一技巧？
2. 什么时候应该用 pairwise，而不是 direct scoring？
3. Position bias 为什么足以让一个看似严谨的 judge pipeline 失真？
