# Project Workspace Guide

这份文档不展开完整 SOP，只定义项目工作区里每个文件和目录的职责。

## 必备文件

| 文件 | 目的 | 使用方式 |
|---|---|---|
| `project.yaml` | 项目主元数据入口 | 新建项目后先补它 |
| `session-brief.md` | 项目驾驶舱首页和启动导航 | 每次进入项目时先读 |
| `workflow.md` | 当前项目类型的局部运行规则 | 继承模板，按项目做轻调整 |
| `brief.md` | 项目存在的理由和目标定义 | 讲清为什么做、做成算什么 |
| `scope.md` | 边界控制 | 讲清 in / out / assumptions / risks / dependencies |
| `plan.md` | 阶段与里程碑 | 拆阶段，不替代当前状态 |
| `status.md` | 给人看的项目快照 | 只保留现在，不写全部历史 |
| `next-actions.md` | 最近 3-5 个动作 | 每项都必须可执行 |
| `open-questions.md` | 未决问题 | 记录阻塞和待定问题 |
| `worklog.jsonl` | 历史动作轨迹 | 会话结束时追加一条或多条 |

## Routing 与 Summaries

| 文件 | 放什么 |
|---|---|
| `context/routing/read-policy.yaml` | 这个项目类型的默认读取策略和预算阈值 |
| `context/routing/current-readset.md` | 当前这一轮真正该读的文件集合 |
| `context/summaries/compact-state.md` | 机器优先的当前压缩状态 |
| `context/summaries/working-summary.md` | 当前阶段的中层压缩 |
| `context/summaries/rolling-summary.md` | 多轮滚动压缩历史 |
| `context/summaries/handoff.md` | 给下一轮或下一个 agent 的交接页 |

## Context 原始层

| 目录 | 放什么 |
|---|---|
| `context/inputs/` | 用户输入、会议记录、截图、附件说明 |
| `context/sources/` | 权威来源、内部文档、固定链接 |
| `context/research/` | 已处理研究和研究 note |
| `context/tool_outputs/` | 长工具输出和抓取结果 |
| `context/pad/` | 临时草稿和推演 |
| `context/manifests/` | 每轮读写记录 |

## Artifacts 目录

| 文件或目录 | 放什么 |
|---|---|
| `artifacts/registry.jsonl` | 项目 artifact 唯一索引 |
| `artifacts/current/` | 当前 canonical artifact |
| `artifacts/archive/` | 已替代或冻结的 artifact |

## Memory 目录

| 文件 | 放什么 |
|---|---|
| `memory/facts.jsonl` | 稳定事实 |
| `memory/decisions.jsonl` | 关键决策和理由 |
| `memory/lessons.jsonl` | 可复用教训和失败模式 |
| `memory/procedures.jsonl` | 可复用流程和 playbook |

## 读取建议

默认先读：

1. `project.yaml`
2. `session-brief.md`
3. `context/routing/current-readset.md`
4. `context/summaries/compact-state.md`
5. `next-actions.md`
6. `workflow.md`

不默认全量读：

- 整个 `context/tool_outputs/`
- 整个 `context/inputs/`
- 全部 `research/`
- 全部 `artifacts/archive/`

## 更新建议

- 改目标、状态、优先级、主 artifact 时更新 `project.yaml`
- 会话结束时更新 `next-actions.md`、`worklog.jsonl`、`compact-state.md`、`handoff.md`
- 有阶段成果时先写 `artifacts/`
- 有稳定知识时再写 `memory/`
- `pad/` 在会话结束时必须分类处理
