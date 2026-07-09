# 主案例映射表

## 案例总览

| 案例 | 主技能 | 次技能 | 用途 |
| --- | --- | --- | --- |
| `digital-brain-skill` | `filesystem-context`, `memory-systems`, `tool-design` | `context-optimization`, `evaluation`, `project-development` | 展示模块化文件系统、低 token 运行、个人 OS 式设计 |
| `x-to-book-system` | `multi-agent-patterns`, `memory-systems`, `context-optimization` | `tool-design`, `evaluation`, `project-development` | 展示 supervisor、多阶段流水线、上下文隔离 |
| `book-sft-pipeline` | `project-development`, `context-compression` | `multi-agent-patterns`, `evaluation`, `context-fundamentals` | 展示 staged pipeline 与“从系统到写作产物”的路径 |
| `llm-as-judge-skills` | `evaluation`, `advanced-evaluation` | `tool-design`, `context-fundamentals` | 展示评估从理论到实现的闭环 |

## 章节与案例绑定

### 第 1-4 章

以 `README.md`、`docs/blogs.md` 为主，目标是建立大图景。

### 第 5-7 章

以 `digital-brain-skill` 为主，目标是理解文件、工具、记忆如何分工。

### 第 8-10 章

以 `x-to-book-system` 和 `book-sft-pipeline` 为主，目标是理解架构选择与系统化方法。

### 第 11-12 章

以 `llm-as-judge-skills` 为主，目标是理解评估设计、偏差控制、rubric 和 pipeline。

### 第 13 章

以 `bdi-mental-states` 自身的理论结构为主，必要时回连多代理与记忆章节。

## 关键边界说明

### `filesystem-context` vs `memory-systems`

- `filesystem-context` 关注外置上下文如何被写入、发现、读取、持久化
- `memory-systems` 关注长期知识怎样建模、检索、更新、保持实体一致性

### `multi-agent-patterns` vs `hosted-agents`

- `multi-agent-patterns` 关注任务如何拆、context 如何隔离、代理如何协作
- `hosted-agents` 关注这些代理运行在什么环境、如何加速、如何持久化和对外暴露

### `evaluation` vs `advanced-evaluation`

- `evaluation` 关注框架、rubric、test set、continuous evaluation
- `advanced-evaluation` 关注 judge 机制、pairwise、bias mitigation、评分 pipeline

## 推荐阅读顺序

1. `digital-brain-skill`
2. `x-to-book-system`
3. `book-sft-pipeline`
4. `llm-as-judge-skills`

原因：

- 先从 filesystem-grounded 系统开始，最容易看到 context engineering 的具体载体
- 再看多代理系统，理解 context isolation 的规模化表达
- 再看 pipeline，理解任务建模与成书产物的关系
- 最后看评估实现，形成闭环

