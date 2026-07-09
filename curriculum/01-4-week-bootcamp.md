# 4 周冲刺执行手册

## Week 1：基础科学

学习章节：

- 第 1 章 `context-fundamentals`
- 第 2 章 `context-degradation`
- 第 3 章 `context-compression`
- 第 4 章 `context-optimization`

目标：

- 建立 context 的构成、退化、压缩、优化四段式理解
- 区分“上下文太长”和“上下文失效”不是同一件事
- 能解释 `compression` 和 `optimization` 的边界

本周交付：

- 术语表 v1，至少 20 个词
- 第 1-4 章草稿，每章 800-1200 字
- 一张 Context 生命周期图

建议证据源：

- `README.md`
- `docs/blogs.md`
- `skills/context-fundamentals/SKILL.md`
- `skills/context-degradation/SKILL.md`
- `skills/context-compression/SKILL.md`
- `skills/context-optimization/SKILL.md`

## Week 2：工程结构

学习章节：

- 第 5 章 `tool-design`
- 第 6 章 `filesystem-context`
- 第 7 章 `memory-systems`

目标：

- 建立 tool、file、memory 三层分工
- 理解为什么 filesystem 在本仓库里不是“临时替代品”，而是方法论中心
- 区分 filesystem persistence 与 memory architecture

本周交付：

- Tool / File / Memory 三层分工表
- 第 5-7 章草稿
- `digital-brain-skill` 映射笔记

建议证据源：

- `skills/tool-design/SKILL.md`
- `skills/filesystem-context/SKILL.md`
- `skills/memory-systems/SKILL.md`
- `examples/digital-brain-skill/HOW-SKILLS-BUILT-THIS.md`

## Week 3：系统架构

学习章节：

- 第 8 章 `multi-agent-patterns`
- 第 9 章 `hosted-agents`
- 第 10 章 `project-development`

目标：

- 从“单点优化”上升到“系统设计”
- 建立 single-agent / multi-agent / hosted-agent 的决策框架
- 能用案例解释 why supervisor、why file coordination、why pipeline architecture

本周交付：

- 第 8-10 章草稿
- 架构反推报告 1 份
- 单 Agent vs 多 Agent vs Hosted Agent 决策图

建议证据源：

- `skills/multi-agent-patterns/SKILL.md`
- `skills/hosted-agents/SKILL.md`
- `skills/project-development/SKILL.md`
- `examples/x-to-book-system/README.md`
- `examples/x-to-book-system/SKILLS-MAPPING.md`
- `examples/book-sft-pipeline/README.md`

## Week 4：评估与升维

学习章节：

- 第 11 章 `evaluation`
- 第 12 章 `advanced-evaluation`
- 第 13 章 `bdi-mental-states`

目标：

- 建立评估闭环
- 区分 evaluation framework 和 LLM-as-a-judge pipeline
- 理解 BDI 作为压轴章的意义：把上下文工程升级为认知状态设计

本周交付：

- 第 11-13 章草稿
- 完整中文书稿大纲
- 设计审查清单
- 前言、结语、章节摘要

建议证据源：

- `skills/evaluation/SKILL.md`
- `skills/advanced-evaluation/SKILL.md`
- `skills/bdi-mental-states/SKILL.md`
- `examples/llm-as-judge-skills/README.md`

## 每周固定动作

1. 先读 skill 原文
2. 再找 example 取证
3. 再写“我的定义”
4. 再写“边界比较”
5. 最后写一段可入书正文

