# Week 2 学习笔记答案版

## 一、3 章核心结论

### 第 5 章 Tool Design

- Tool 是 agent-world contract，不是中性 API。
- Tool description 本身就是上下文的一部分。
- 好工具的关键不是多，而是边界清晰、描述明确、错误可恢复。

### 第 6 章 Filesystem Context

- 文件系统是外置上下文的通用基础设施。
- 它最大的价值不是存储容量，而是动态发现与按需读取。
- Scratch pad、plan persistence、sub-agent communication 都建立在这个层面。

### 第 7 章 Memory Systems

- Memory 的核心不是存储，而是 retrieval correctness。
- 先用简单结构验证需求，再按查询复杂度升级。
- `filesystem-context` 是外置基础设施，`memory-systems` 是知识架构层。

## 二、重点边界题答案

### 1. `tool-design` vs 普通 API 设计

- 普通 API 默认调用者懂 schema、会调试、会纠错。
- Agent tool design 要把何时调用、如何调用、失败后怎么修都写进契约里。
- 所以工具设计本身就是一种上下文设计。

### 2. `filesystem-context` vs `memory-systems`

- `filesystem-context` 解决“如何把信息外置并重新找到”。
- `memory-systems` 解决“如何让跨会话知识被正确组织和正确取回”。
- 前者是承载层，后者是记忆架构层。

### 3. 为什么 `digital-brain-skill` 是 Week 2 的主案例？

- 它同时展示了工具设计、模块化文件系统、渐进加载、JSONL 持久化和轻量记忆。
- 它把抽象 skill 变成了清晰的工程形态。
- 它能让我们看见 tool/file/memory 三层如何协同，而不是停留在定义层。

## 三、推荐复述题

1. 为什么工具描述写得差，会直接污染 agent 的推理路径？
2. 为什么文件系统不是“低配版 memory”，而是 agent 的地面基础设施？
3. 为什么很多项目一开始不应该直接上 graph memory？
4. 为什么 retrieval correctness 比 storage sophistication 更重要？

## 四、Week 2 最低达标标准

到这一周结束时，你应该能做到：

- 用自己的话解释 `tool-design`、`filesystem-context`、`memory-systems`
- 说清楚 tool / file / memory 三层分工
- 用 `digital-brain-skill` 说明 progressive disclosure 怎样落地
- 说清楚为什么 `x-to-book-system` 需要 temporal KG 而不是只用 vector retrieval
- 说清楚 `filesystem-context` 和 `memory-systems` 的边界

## 五、Week 3 衔接

下一周我们会把工程结构提升为系统架构：

- 为什么多 agent 的本质是 context isolation
- 为什么 hosted agents 属于运行时 context engineering
- 为什么 project development 要从 task-model fit 开始
