# Week 3 学习笔记答案版

## 一、3 章核心结论

### 第 8 章 Multi-Agent

- 多 agent 的核心收益是 context isolation。
- 架构模式选择取决于任务分解方式和协调成本。
- `x-to-book-system` 是 supervisor 模式的标准案例。

### 第 9 章 Hosted Agents

- Hosted agents 把运行环境本身纳入上下文管理范围。
- 预热、快照、沙箱和并发不只是基础设施技巧，而是 runtime context engineering。
- Hosted 不替代 multi-agent，而是为其提供更强的执行底座。

### 第 10 章 Project Development

- 先做 task-model fit，再谈架构与 prompt。
- 手工样本验证是 LLM 项目最划算的一步。
- `book-sft-pipeline` 是阶段化、可缓存、可调试项目方法论的典型案例。

## 二、重点边界题答案

### 1. `multi-agent-patterns` vs `hosted-agents`

- `multi-agent-patterns` 讨论任务如何拆分、如何 handoff、如何隔离上下文。
- `hosted-agents` 讨论这些 agent 在什么运行时里执行、如何快速启动、如何恢复与并发。
- 一个偏系统架构，一个偏基础设施运行时。

### 2. 为什么 `x-to-book-system` 更适合 supervisor？

- 它有清晰阶段：抓取、分析、综合、写作、编辑。
- 阶段之间需要质量门和中央协调。
- 它不适合无中心自由探索型 swarm。

### 3. 为什么 `book-sft-pipeline` 是 project development 主案例？

- 它把原本模糊的“训练风格模型”拆成可验证的多个阶段。
- 它体现了 acquire / prepare / process / parse / render 的方法论精神。
- 它强调 task-model fit、结构化输出、中间文件和 validation，而不是一口气端到端黑箱完成。

## 三、推荐复述题

1. 为什么“给单 agent 更多 token”不等于“解决复杂任务”？
2. 为什么 snapshot 比保存聊天记录更接近真实连续性？
3. 为什么 LLM 项目最应该先验证的是 task-model fit？
4. 什么时候 multi-agent 真正比 single pipeline 更值得？

## 四、Week 3 最低达标标准

到这一周结束时，你应该能做到：

- 解释 supervisor、swarm、hierarchical 的差别
- 说清 hosted agents 为什么属于 Context Engineering
- 用 `x-to-book-system` 解释多 agent 的 context isolation
- 用 `book-sft-pipeline` 解释 staged pipeline 方法论
- 给一个新项目做 single-agent / multi-agent / hosted-agent 的初步判断

## 五、Week 4 衔接

下一周我们会进入闭环阶段：

- 为什么 evaluation 不是末尾补充，而是前面设计的反向约束
- 为什么 advanced evaluation 的重点是 judge 机制工程化
- 为什么 BDI 作为压轴章，代表 Context Engineering 向认知架构升级
