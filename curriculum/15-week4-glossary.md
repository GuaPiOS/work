# Week 4 术语表 v1

## 1. Outcome-Focused Evaluation

一句话定义：根据结果质量而不是固定执行路径来评价 agent。
与相邻概念的边界：不同于传统软件流程校验。
在本地仓库中的证据：`skills/evaluation/SKILL.md`

## 2. Multi-Dimensional Rubric

一句话定义：从多个质量维度而非单一总分评估系统表现。
与相邻概念的边界：它强调质量剖面，不等于简单加权平均。
在本地仓库中的证据：`skills/evaluation/SKILL.md`

## 3. Complexity Stratification

一句话定义：按简单到复杂分层构造测试集。
与相邻概念的边界：不是样本数量问题，而是覆盖层级问题。
在本地仓库中的证据：`skills/evaluation/SKILL.md`

## 4. LLM-as-a-Judge

一句话定义：使用 LLM 对 LLM 或 agent 输出做自动质量评估的方法族。
与相邻概念的边界：不是单个 prompt 技巧，而是一类评估系统。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 5. Direct Scoring

一句话定义：由 judge 模型对单个响应按给定尺度评分。
与相邻概念的边界：更适合 objective criteria。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 6. Pairwise Comparison

一句话定义：由 judge 模型比较两个响应并选出更优者。
与相邻概念的边界：更适合 preference judgment。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 7. Position Bias

一句话定义：pairwise 评估中对先出现响应的系统性偏好。
与相邻概念的边界：它是排序偏差，不等于内容质量差异。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 8. Length Bias

一句话定义：更长响应更容易被误判为更好。
与相邻概念的边界：它反映 judge 偏差，不反映真实必要信息量。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 9. Confidence Calibration

一句话定义：让 judge 的置信度与其一致性和证据强度匹配。
与相邻概念的边界：不是给结果多一个数字，而是约束结果可信程度。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 10. Rubric Generation

一句话定义：为特定任务生成可执行的评分标准与边界说明。
与相邻概念的边界：不是写原则口号，而是生成评分协议。
在本地仓库中的证据：`skills/advanced-evaluation/SKILL.md`

## 11. Belief

一句话定义：agent 认为当前世界中为真的状态。
与相邻概念的边界：belief 引用 world state，但不等于 world state 本身。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

## 12. Desire

一句话定义：agent 希望实现的目标状态。
与相邻概念的边界：它描述想要达成什么，不等于已承诺执行。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

## 13. Intention

一句话定义：agent 已经承诺去执行的目标导向行动状态。
与相邻概念的边界：比 desire 更具行动承诺。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

## 14. Mental Process

一句话定义：导致 mental state 形成、更新和转化的过程。
与相邻概念的边界：state 是持久属性，process 是时序事件。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

## 15. World State Grounding

一句话定义：将 mental states 明确绑定到外部世界状态表示上。
与相邻概念的边界：防止 belief 与真实环境脱钩。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

## 16. Justification

一句话定义：支撑某个 belief 或 intention 的证据说明。
与相邻概念的边界：比普通日志更强调 reasoning trace。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

## 17. Temporal Validity

一句话定义：mental state 在什么时间范围内成立。
与相邻概念的边界：它把认知状态纳入时序约束，而非静态真值。
在本地仓库中的证据：`skills/bdi-mental-states/SKILL.md`

