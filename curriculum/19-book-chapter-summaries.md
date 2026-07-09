# 全书章节摘要

## 第 1 章 Context Engineering Fundamentals

重新定义 context，不把它简化成 prompt，而是把它看成模型可见状态的整体装配系统。

## 第 2 章 Context Degradation Patterns

解释上下文为什么会在未超窗前就先失真，并建立 lost-in-the-middle、poisoning、distraction、confusion、clash 的病理视角。

## 第 3 章 Context Compression Strategies

说明长任务中如何高保真压缩历史，使 agent 在压缩后仍能继续工作，而不是被迫返工。

## 第 4 章 Context Optimization

讨论 compaction、observation masking、KV-cache ordering 和 partitioning，展示如何让当前上下文更高信号。

## 第 5 章 Tool Design for Agents

把 tools 重新定义为 agent-world contract，解释为什么工具设计就是上下文设计。

## 第 6 章 Filesystem Context

说明文件系统如何作为外置上下文与动态发现层，承载 scratch pad、计划、日志和子代理共享状态。

## 第 7 章 Memory Systems

说明 memory 的核心不是存储，而是 retrieval correctness，并区分 filesystem persistence、vector retrieval、temporal KG 等不同层次。

## 第 8 章 Multi-Agent Architecture Patterns

解释多 agent 的真正价值是上下文隔离，而不是角色扮演，并比较 supervisor、swarm、hierarchical 的适用条件。

## 第 9 章 Hosted Agents

把 Context Engineering 扩展到运行时基础设施层，讨论 sandbox、warm pool、snapshot 和 self-spawning agents。

## 第 10 章 Project Development Methodology

说明为什么成熟的 LLM 项目必须从 task-model fit、manual prototype 和 staged pipeline 开始，而不是从 prompt 开始。

## 第 11 章 Evaluation

建立 agent 系统评估框架，用多维 rubric、复杂度分层和连续跟踪验证 context 设计是否真正有效。

## 第 12 章 Advanced Evaluation

深入 LLM-as-a-Judge 的实现细节，说明 direct scoring、pairwise comparison、bias mitigation 与 rubric generation 的工程要点。

## 第 13 章 BDI Mental State Modeling

把 Context Engineering 提升到认知状态建模层，展示 belief、desire、intention 如何支撑更强的解释性与 deliberation。
