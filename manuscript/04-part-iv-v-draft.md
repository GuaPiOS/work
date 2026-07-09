# 《Context Engineering》书稿第一版（第四、五部）

# 第四部：让系统可验证、可迭代

## 第 11 章 Evaluation

到了这里，我们终于来到一个特别关键、也最容易被忽视的部分：evaluation。很多团队在做 agent system 时，把评估理解为最后补几条 benchmark、跑几次 demo、看起来没问题就上线。这种做法的问题不是不做测试，而是把评估放错了位置。对于 Context Engineering 来说，如果没有系统评估，所有“优化”都只是主观感觉。

为什么 evaluation 在 agent 系统里尤其重要？因为 agent 不是普通软件函数。它是非确定性的，可能通过不同路径到达相同结果，也可能在相似任务上表现出完全不同的稳定性。一个 agent 这次搜索了 3 个页面，下次可能搜索了 10 个页面；这次从工具 A 找到答案，下次可能从工具 B 找到。你不能用传统软件测试那种“必须按预定步骤执行”来评价它。因此，这一章的出发点就是 outcome-focused evaluation：评价的重点是结果是否正确、过程是否合理，而不是路径是否完全一致。

这也是为什么 evaluation 不能被理解为“跑几个样例看感觉”。更准确的定义是：用明确的质量维度、测试样本、评分规则和持续比较机制，判断一个 agent system 是否真正达成了预期效果，并找出变化是改善还是退化。对于 Context Engineering 来说，evaluation 的重点不是验证模型会不会回答，而是验证某种上下文设计、工具结构、记忆策略或多 agent 架构，是否真的提升了结果质量、效率和稳定性。

本章最重要的结构，是 multi-dimensional rubric。agent 质量从来不是单一维度。一个回答可能事实准确，但不完整；可能内容完整，但引用不准；可能最终答案没错，但用了过多无效工具调用。评价如果只压成一个总分，系统会失去可解释性。你不知道它到底进步在什么地方，也不知道它退化在什么地方。多维 rubric 的价值，就在于把“系统好不好”拆成可观察、可比较、可权衡的质量剖面。

`x-to-book-system` 是很好的例子。它不是只看“这本书写出来了吗”，而是进一步拆成 Source Accuracy、Thematic Coherence、Completeness、Insight Quality、Readability 五个维度。这种做法非常值得学，因为它把“结果像不像样”拆成了可以被解释、被比较、被优化的不同面向。对 Context Engineering 来说，这一点尤其重要：你需要知道一个设计改动到底改善了 factual grounding，还是只是让 prose 看起来更顺。

本章的第二个关键点是 test set design。评估如果只挑最好看的几个样例，几乎一定会误导。必须按复杂度分层：simple、medium、complex、very complex。这个建议背后有一个非常扎实的工程逻辑。因为 context engineering 的很多问题，不会在简单样本上暴露，只会在长链路、多工具调用、高歧义、长上下文任务里出现。你如果不故意设计复杂样本，很多退化和边界问题根本看不见。

还有一个经常被低估的点，是 evaluation 与 token budget 的关系。一个系统在无限预算下表现好，不代表它在真实产品预算下也成立。对 Context Engineering 而言，这意味着 evaluation 不只是看质量，还要看质量是以什么资源代价换来的。没有预算约束的评估，很容易把昂贵但不可落地的方案误判为最佳实践。

因此，这一章最重要的结论是：evaluation 不是后置验证，而是前置设计的裁判。你对 context 的任何判断，无论是 compression、optimization、filesystem offloading、memory retrieval，还是 multi-agent coordination，最后都必须通过 evaluation 才能从“方法”变成“证据”。没有这一层，系统再复杂，也只是工程师对自己设计的信心；有了这一层，才开始变成可以持续改进的工程实践。

## 第 12 章 Advanced Evaluation

如果说上一章解决的是“为什么必须评”，那么这一章解决的是“自动评这件事怎样才不至于自欺欺人”。很多团队一听到 LLM-as-a-Judge，就会自然地想成：再调用一次模型，让它给前一个模型打个分。这种理解的问题，不在于方向错，而在于过度简化。LLM-as-a-Judge 不是一个技巧，而是一整个技术家族。不同任务要用不同 judge 方法，而且每一种方法都有自己常见的偏差。

这也是为什么本章要先给出更严格的定义：Advanced Evaluation 指的是围绕 LLM-as-a-Judge 构建一套可重复、可比较、可解释的自动评估机制，并针对 direct scoring、pairwise comparison、rubric generation 和 bias mitigation 设计稳定的评分流程。它不是 evaluation 的重复版本，而是 evaluation 的实现深化层。Evaluation 决定“评什么”，Advanced Evaluation 决定“自动怎么评得更可靠”。

本章的第一个关键区分，是 direct scoring 与 pairwise comparison。Direct scoring 适合 objective criteria，比如事实正确性、格式遵从、是否覆盖指定要点。这类任务存在相对明确的判准，judge 只需要把响应映射到某个分值尺度。相反，pairwise comparison 更适合偏好判断，比如文风、可读性、说服力。因为这类任务很难定义一个绝对分值，却比较适合说“两个里面哪个更好”。

很多 judge 系统出问题，不是因为模型不够强，而是因为方法选错了。你让模型对创意性写作做绝对打分，评分会很飘；你让模型对格式合规性做 pairwise，效率又会变差。方法选择不是实现细节，而是任务结构判断。只要这一步错了，后面再怎么调 rubric、换模型、加提示，稳定性都上不去。

Advanced Evaluation 的第二个核心，是 bias mitigation。Judge 并不天然中立。position bias、length bias、self-enhancement bias、verbosity bias、authority bias，都可能让一个看似严谨的评估系统持续输出系统性偏差。尤其在 pairwise comparison 里，position bias 几乎是默认存在的。于是 position swap 不再是“一个可选技巧”，而是最低限度的卫生规范：把 A/B 顺序交换再评一次，如果前后不一致，就不能再装作这个结论很稳。

`llm-as-judge-skills` 这个案例把这些原则做成了可执行实现。它不仅有 `directScore`、`pairwiseCompare`、`generateRubric` 三类核心工具，还把 bias mitigation 写进了逻辑里，比如 pairwise comparison 自动 position swapping、要求 evidence-bearing justifications、结构化输出和测试用例覆盖。这一点非常关键，因为它说明 advanced evaluation 不是概念讨论，而是可以落成工具、prompt、agent、test 的完整工程层。

本章还要强调 rubric generation 的作用。很多人把 rubric 当成一个静态文档，但这里的意思更接近“评分协议生成器”。好的 rubric 会把模糊标准变成可观察特征、分值边界和边缘情况处理。没有 rubric，judge 更容易随感觉波动；有 rubric 但 rubric 太宽泛，也一样不可靠。所以 advanced evaluation 真正做的是把“标准”工程化，而不是把“打分”自动化。

因此，这一章的结论可以压成一句话：Advanced Evaluation 关心的不是能不能自动打分，而是自动打分是否值得相信。它通过方法选择、rubric 设计、偏差控制、置信度处理和测试验证，把 LLM-as-a-Judge 从一个看似聪明的技巧，变成一个可部署、可复核、可持续优化的系统能力。没有这一层，evaluation 很容易变成高频但低可信的数字噪声；有了这一层，评估才真正开始成为产品与研究可以依赖的反馈回路。

# 第五部：认知架构与下一层抽象

## 第 13 章 BDI Mental State Modeling

把 BDI 放在压轴章，是有意为之。如果一开始就讲 belief、desire、intention，很多人会误以为 Context Engineering 是一门高度形式化、只有做 ontology 才算入门的学问。其实不是。前面 12 章已经证明，Context Engineering 首先是一门非常工程化的 discipline：你在管理 context 组成、退化、压缩、优化、工具、文件、记忆、架构和评估。那为什么最后还要回到 BDI？因为当系统开始不仅要“看见”信息，还要“解释自己为什么这么做”时，纯粹的信息装载已经不够了。

这也是为什么本章要把 BDI 定义为：把外部世界状态、任务目标和行动计划，分别建模为 belief、desire、intention 等可追踪的认知状态，并通过显式关系连接感知、动机、计划和执行。对 Context Engineering 来说，它的意义在于：context 不再只是待加载的信息集合，而可以进一步被组织成有认知语义的内部状态结构，从而支持解释、审计与更稳定的 deliberation。

Belief 表示代理认为什么是真的，Desire 表示它希望达成什么，Intention 表示它真正承诺要做什么。这个划分听起来像哲学，但在工程上非常有用。因为很多 agent 的不稳定，并不是不会规划，而是没有清楚地区分“知道了什么”“想实现什么”“已经决定做什么”。当这三件事混在一起时，系统就容易在长任务中丢目标、变计划、互相冲突却没有解释能力。

仓库里的 cognitive chain pattern 给了一个非常清晰的最小例子：belief store_open 促成 desire buy_groceries，再支持 intention go_shopping，并最终关联到具体 plan。这个结构的价值，不在于它看上去很学术，而在于它把一条原本隐含在自然语言里的推理链，显式写成了可以追踪、查询、验证的状态关系。于是系统不只是“做了一个动作”，而是能够回答：“我为什么形成这个目标？我基于什么 belief 做了这个 commitment？这个 intention 对应哪条 plan？”

这和前面几章其实是连续的。memory systems 解决的是知识如何跨时间取回；multi-agent patterns 解决的是不同上下文如何协同；evaluation 解决的是结果如何判断。BDI 则把这些能力再往上收束成认知视角：一个多 agent 系统不只是多个上下文在跑，还可能是多个 belief structures、goal commitments 和 plan states 在交互。一个 memory system 不只是保存事实，还可能为 belief 提供时序支持。这样一来，Context Engineering 开始从“输入管理”升级到“认知状态管理”。

这里特别值得强调的是 explainability。现代 agent 系统经常给人一种“看起来会做，但说不清为什么”的感觉。BDI 的价值之一，就是给出一种更结构化的说明方式。系统不只是回溯日志说“我执行了这些步骤”，而是能说明“因为我感知到这个 world state，所以形成了这个 belief；因为这个 belief 激发了这个 desire，所以我承诺了这个 intention；因为这个 intention 被 plan 支持，所以我执行了这些 task”。这比普通日志更接近 reasoning audit。

当然，这一章也不应该被神化。不是所有 agent 项目都需要 BDI。本书把它放在最后，就是为了建立一个正确分层：先把 Context Engineering 作为工程 discipline 学会，再把 BDI 看作其中一条高阶延展路径。对多数系统来说，你完全可以在没有正式 BDI ontology 的情况下，依然做好 context budgeting、filesystem offloading、memory retrieval 和 evaluation。只有当系统开始要求更强解释性、复杂目标管理或 neuro-symbolic integration，BDI 才会成为值得引入的下一层结构。

因此，本章的结论是：BDI 不是 Context Engineering 的前提，而是它的升维版本。它让我们看到，Context Engineering 最终不一定停留在“哪些信息该放进窗口里”，还可能继续走向“这些信息在系统内部被组织成怎样的认知现实”。这正是它作为压轴章的价值。

## 结语：从管理上下文，到设计认知系统

走到最后，我们已经不再把 Context Engineering 看成“提示词写法”的延伸，也不再把它当成一些零散的 agent 小技巧。它逐渐显出自己的完整轮廓：一门围绕有限注意力、动态上下文、外置状态、系统架构和质量闭环展开的工程 discipline。

全书的推进顺序，其实也是一条能力升级路径。一开始，我们先承认 context 是有限资源，并学习它如何退化、如何压缩、如何优化。接着，我们把这些原则落到工具、文件系统和记忆系统这些工程结构上。再往后，我们开始面对更复杂的系统：什么时候需要多 agent，什么时候需要 hosted runtime，什么时候应该先停下来判断 task-model fit。最后，我们用 evaluation 让所有设计接受证据检验，再用 BDI 展示这条路线可能继续走向怎样的认知建模层。

如果前面章节是在教你如何让 agent 更能工作，那么最后几章其实在教你如何让 agent 更能被理解、被比较、被迭代。这是这本书真正的收束点。Context Engineering 最有价值的地方，不只是提升某次结果，而是让系统变得可诊断、可演化、可解释。

你现在手里拥有的，已经不只是 13 个 skills 的读书笔记，而是一整套可继续扩写的书稿骨架、一张案例与方法论的映射图，以及一种足以支撑未来项目判断的视角。接下来你可以继续做两件事：要么把每章扩成完整书稿，要么把这套方法论直接拿去审视你接下来会做的 agent 系统。

真正成熟的 Context Engineer，不是会背几个术语的人，而是能在系统开始失真之前看出问题，在系统还没跑偏时设计好边界，在系统规模变大时仍然知道该把哪些信息放进 context、把哪些状态放到外部、把哪些判断交给评估。

最后要留下的一句话很简单：

Prompt 决定模型怎么说，Context Engineering 决定系统怎样思考、怎样行动、怎样持续工作。

