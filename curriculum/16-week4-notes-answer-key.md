# Week 4 学习笔记答案版

## 一、3 章核心结论

### 第 11 章 Evaluation

- Evaluation 是 Context Engineering 的证据层。
- 没有多维 rubric 和复杂度分层，评估很容易失真。
- 评估不是末尾补充，而是反向约束前面所有设计。

### 第 12 章 Advanced Evaluation

- LLM-as-a-Judge 是一组方法，不是单一技巧。
- Direct scoring 与 pairwise comparison 适用于不同任务结构。
- Judge pipeline 的关键是去偏、校准与结构化输出。

### 第 13 章 BDI

- BDI 让 context 管理上升为认知状态建模。
- 它强化了 explainability，而不是替代前面工程章节。
- 放在压轴，是为了展示 Context Engineering 的上限而不是入门门槛。

## 二、重点边界题答案

### 1. `evaluation` vs `advanced-evaluation`

- `evaluation` 决定评估框架、质量维度、测试集与持续跟踪。
- `advanced-evaluation` 决定 judge 如何做得更稳、更少偏、更可解释。
- 一个偏评估系统设计，一个偏 judge 引擎工程。

### 2. 为什么 BDI 是最后一章？

- 因为它不是做好 Context Engineering 的前提。
- 它是在前面所有工程结构已经建立后，对认知状态层的升维。
- 如果太早讲，容易误导成“先学 ontology 才能做 agent”。

### 3. 为什么评估体系会反过来约束前面设计？

- 因为一旦你明确了质量维度和测试样本，就会发现哪些 context 设计真正影响结果。
- 没有评估，前面所有优化都缺少可证据化标准。
- 所以评估不是后验检查，而是前置约束。

## 三、推荐复述题

1. 为什么说一个没有评估体系的 agent 项目，很难真正知道自己是否进步？
2. 为什么 pairwise comparison 比 direct scoring 更适合主观偏好判断？
3. 为什么 BDI 能提升 explainability？
4. 为什么把 BDI 当成入门 prerequisite 会误导学习路径？

## 四、Week 4 最低达标标准

到这一周结束时，你应该能做到：

- 解释 evaluation 与 advanced evaluation 的边界
- 说清楚 direct scoring 和 pairwise 的适用场景
- 用 `llm-as-judge-skills` 说明 judge pipeline 如何落地
- 说明 belief / desire / intention 的区别
- 解释为什么 BDI 是全书压轴而不是全书起点

## 五、课程收束

完成 Week 4 后，你应已具备：

- 13 章完整认知框架
- 从案例反推方法论的能力
- 用中文重写这套体系的能力
- 继续扩写正式书稿的骨架与术语统一性
