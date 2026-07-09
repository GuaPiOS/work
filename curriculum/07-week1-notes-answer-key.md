# Week 1 学习笔记答案版

## 一、4 章核心结论

### 第 1 章 Fundamentals

- Context 是模型一次推理可见的完整状态，不只是 prompt。
- 真正被工程化的是“信息如何进入模型注意力”。
- Progressive disclosure 是 Context Engineering 的基本装载原则。

### 第 2 章 Degradation

- 上下文失败通常先于窗口耗尽。
- 退化的五种主模式是位置损失、污染、分心、混淆、冲突。
- 诊断系统问题时，要先看 context 病理，再看模型能力。

### 第 3 章 Compression

- Compression 目标是 tokens-per-task，而不是 tokens-per-request。
- 真正难保留的是 artifact trail，而不是主题摘要。
- 高质量 compression 依赖结构化保真，而不是自由总结。

### 第 4 章 Optimization

- Optimization 关注当前上下文的高信号组织方式。
- Observation masking 是最核心的运行时优化动作之一。
- 当单上下文再怎么整理都不够时，应转向 partitioning。

## 二、重点边界题答案

### 1. `compression` vs `optimization`

- `compression` 是在上下文过长后，为了继续执行任务而进行的高保真压缩。
- `optimization` 是更广义的运行时管理，包含 compaction、masking、cache ordering、partitioning。
- 前者主要解决续航，后者主要解决效率与信号密度。

### 2. 为什么说 tool outputs 是 Context Engineering 的关键对象？

- 因为在真实 agent 系统中，最大 token 消耗常来自工具输出而不是用户输入。
- 工具输出一旦不被管理，会迅速挤压任务目标与决策信号。
- 所以后续才需要 masking、compaction、filesystem offloading。

### 3. 为什么 degradation 是病理学基础？

- 因为 compression、optimization、filesystem、multi-agent 都不是孤立技巧。
- 它们之所以存在，是为了应对 attention 退化、污染、噪声竞争和冲突累积。
- 不理解 degradation，就会把后续章节误解为工具箱，而不是系统疗法。

## 三、推荐复述题

试着不用原文，自己回答下面 4 题：

1. 为什么 Context Engineering 不能被降格为 Prompt Engineering？
2. 为什么 agent 系统最危险的状态常常是“能跑但已偏”？
3. 为什么 summary 做得像人写的不一定适合 agent 续航？
4. 为什么 observation masking 常常比继续加更多文档更有效？

## 四、Week 1 最低达标标准

到这一周结束时，你应该能做到：

- 用自己的话定义 context、degradation、compression、optimization
- 解释这四章之间的先后关系
- 用 `x-to-book-system` 说明 masking 的价值
- 用 `context-compression` skill 说明为什么 artifact trail 难保留
- 说清楚 compression 和 optimization 的边界

## 五、下一步衔接

Week 2 会把抽象原则落到工程结构：

- 为什么 tool 是上下文契约
- 为什么 filesystem 是外置上下文的地面层
- 为什么 memory 的关键不在存储，而在可检索与时序有效性
