# 第 2 章：Context Degradation Patterns

## 章节定位

本章解释长上下文为什么会让系统“看起来还在运行，但已经开始失真”。

## 对应官方 skill

- `skills/context-degradation/SKILL.md`

## 必读材料

- `skills/context-degradation/SKILL.md`
- `docs/blogs.md`

## 问题

上下文失效并不只是 token 不够。很多时候，系统还没超窗，质量已经在下降。本章解决“Context 到底是怎样一步步变坏的”。

## 核心论点

Context failure 更像一组病理过程，而不是一次性崩溃。工程师必须能分辨系统是在“缺容量”，还是在“已退化”。

## 定义

Context Degradation 指的是：即使上下文窗口还没有真正耗尽，模型的有效理解与决策质量也会随着上下文增长、冲突累积和信号稀释而持续下降。它不是单点故障，而是一组可预期的失效模式，包括 lost-in-the-middle、poisoning、distraction、confusion 和 clash。

这一定义的关键在于，它把“上下文过长”与“上下文失效”区分开了。系统可能还在可用窗口内，但由于位置、冲突、噪声和历史污染，已经开始做出错误判断。

## 机制

重点解释：

- lost-in-the-middle
- poisoning
- distraction
- confusion
- clash

## 技术模式

- attention-favored placement
- relevance filtering
- explicit segmentation
- recovery after poisoning

## 案例证据

- 从 `context-degradation` skill 中提取五类失效
- 回连 `x-to-book-system` 中对 raw tweet 的隔离做法

## 边界比较

### Degradation vs Context Limit

- Context limit 说的是技术上还能塞多少。
- Degradation 说的是质量上还能稳定做多少。
- 很多系统在没撞上限前就先退化了。

### Poisoning vs Clash

- Poisoning 通常是错误内容被滚入后续推理。
- Clash 则是多个内容彼此冲突，即使它们各自可能都合理。
- 前者强调污染传播，后者强调冲突管理。

## 反模式

- 只把失败归因于模型笨
- 只盯 token 数，不看信息位置与冲突
- 把错误 summary 继续滚入后续上下文

## 写作练习

写 800-1200 字，回答：

“为什么 agent 系统最危险的状态不是 context 已满，而是 context 已经被污染但工程师还没意识到？”

## 章节草稿

很多工程师把长上下文失败理解为一件简单的事：token 太多了，所以模型记不住。`context-degradation` 这份 skill 纠正了这种过度简化。上下文失效不是等到窗口爆掉才出现，而是从很早就开始。系统表面看起来还在正常工作，工具还能调、回答还能生成，但决策质量已经在下降。这种“还没死，但已经偏了”的状态，才是 agent 系统最危险的阶段。

第一个最经典的失效模式是 lost-in-the-middle。仓库直接指出，模型对上下文的注意力分布呈 U 形：开头和结尾最容易被稳定检索，中间最容易被忽略。这意味着一个很反直觉的工程结论：同一条关键信息，放在中间和放在边缘，系统表现会不同。很多失败不是因为信息不存在，而是因为信息被埋在不利位置。也因此，真正重要的任务目标、约束、当前状态，应该尽量放在 attention-favored positions，而不是相信模型会平均阅读每一段文本。

第二个失效模式是 poisoning，也就是上下文污染。污染比普通错误更危险，因为它会自我强化。一个错误的 tool output、一个带 hallucination 的中间 summary、一个过时但没被标记的检索文档，都可能进入上下文并被后续推理反复引用。一旦错误进入 goals、plans 或 state，它就不再只是“某次回答错了”，而会开始扭曲后续所有动作。很多 agent 之所以越做越偏，不是因为不会纠错，而是因为错误已经沉淀成了它的当前世界观。

第三个失效模式是 distraction。注意，这不是“背景里有点噪声”那么简单。仓库强调，模型并没有真正跳过无关信息的机制。只要你把东西放进 context，它就必须分配注意力给它。于是一个本来无害的冗长日志、一篇并不相关的参考文档、一个多余的工具定义，都可能抢走真正关键问题的注意力。对 agent 来说，distraction 常常表现为：回答内容很多，但没有抓住当前任务的核心。

第四个模式是 confusion。它与 distraction 相近，但更偏向“适用边界混乱”。比如一个系统在同一 session 里先做研究，再做写作，再做代码修改，结果模型开始把前面任务的约束错误地套用到后面的任务上。它不是不知道信息，而是不知道哪些信息属于当前局面。这种混乱往往发生在多任务长会话里，也正是为什么后面的 filesystem context、context partitioning 和 multi-agent isolation 会变得重要。

第五个模式是 clash，即上下文冲突。和 poisoning 不同，clash 不一定来自错误内容，也可能来自两个都“各自正确”的信息源。例如一份旧规范和一份新规范并存、一个版本说明和一段历史代码实现不一致、两个专家观点都合理但彼此矛盾。如果系统没有明确优先级、版本过滤或冲突标记机制，模型就会在矛盾中失去稳定判断。

这一章真正要建立的，不是几个术语，而是一种诊断视角：当 agent 变差时，你不能只问“是不是模型不够强”，而要问“是不是信息位置错了、上下文污染了、噪声太多了、任务边界混了、信息彼此打架了”。从这个角度看，Context Engineering 的后续章节就不再像零散技巧，而像一套治疗方案。Compression 解决的是历史过长后的信息保真，optimization 解决的是高噪声上下文的重新组织，filesystem 和 multi-agent 则是在更高层面隔离和外置这些问题。也就是说，degradation 不是支线知识，而是整套工程方法为什么存在的病理学基础。

## 学习检查

1. Lost-in-the-middle 和 distraction 的差别是什么？
2. 为什么错误 summary 比一次错误回答更危险？
3. 在多任务长会话里，confusion 通常表现为什么？
