# Ontology

这份文件用来统一 Second Brain OS 里的核心对象定义，避免 agent 在不同会话里漂移。

## 对象字典

| 对象 | 是什么 | 不是什么 | 应该存在哪 | 生命周期 |
|---|---|---|---|---|
| `project` | 一个需要跨会话推进、有目标和边界的工作单元 | 一条待办、一篇笔记、一段聊天 | `projects/active/<slug>/` | 创建 -> 活跃 -> 完成/归档 |
| `task` | 项目中的一个可执行动作 | 项目本身 | `next-actions.md` 或 `plan.md` | 打开 -> 执行 -> 完成/重排 |
| `session` | 一次具体会话或工作轮次 | 整个项目历史 | `context/manifests/` 和 `worklog.jsonl` | 开始 -> 产出 -> 关闭 |
| `context` | 为当前任务装配的最小必要信息集合 | 全部文件总和 | `context/` 和当前读取清单 | 按需加载 -> 使用 -> 摘要/沉淀 |
| `read set` | 当前这一轮真正需要读取的文件集合 | 整个项目目录 | `context/routing/current-readset.md` | 会话前更新 -> 会话中使用 -> 会话后重写 |
| `summary` | 压缩后的中间上下文层 | 原始资料或最终产物 | `context/summaries/` | 生成 -> 重写 -> 归档 |
| `compact state` | 下一轮启动时默认注入的机器友好压缩状态 | 全部状态历史 | `context/summaries/compact-state.md` | 每轮重写 |
| `memory` | 跨会话仍值得保留的结构化知识 | 任意草稿或原始资料 | `memory/` 或 `brain/memory/` | 记录 -> 校验 -> 晋升/归档 |
| `fact` | 相对稳定、可验证的事实 | 个人判断或推测 | `memory/facts.jsonl` | 来源出现 -> 写入 -> 过期/归档 |
| `decision` | 关键取舍及其理由 | 普通动作记录 | `memory/decisions.jsonl` | 决策发生 -> 跟踪 -> 复盘 |
| `lesson` | 可复用的方法教训、失败模式、有效做法 | 单次随机感想 | `memory/lessons.jsonl` | 事件触发 -> 总结 -> 跨项目复用 |
| `procedure` | 某类任务的可复用操作模式或 playbook | 一次性的 next action | `memory/procedures.jsonl` | 多次验证 -> 沉淀 -> 复用/失效 |
| `artifact` | 一个独立可引用、可交接、可复用的正式产物 | 聊天里的临时结论 | `artifacts/current/` 和 `artifacts/registry.jsonl` | 产出 -> 成为 canonical -> 归档/替换 |
| `workflow` | 当前项目类型的局部运行规则 | 全局原则 | `workflow.md` | 模板继承 -> 项目适配 |
| `plan` | 项目阶段、里程碑、决策点 | 当前状态 | `plan.md` | 初始化 -> 调整 |
| `status` | 给人读的项目当前快照 | 全部历史或机器压缩状态 | `status.md` | 持续刷新 |
| `next action` | 最近 3-5 个可执行动作 | 长期愿望清单 | `next-actions.md` | 执行 -> 删除/替换 |
| `worklog` | 历史动作轨迹 | 当前快照 | `worklog.jsonl` | 追加写 |
| `session brief` | 项目驾驶舱首页和启动导航 | 完整项目说明书 | `session-brief.md` | 每轮更新 |
| `handoff` | 给下一轮或下一个 agent 的交接页 | 完整会话记录 | `context/summaries/handoff.md` | 每轮重写 |

## 五个容易混淆的边界

### `brief.md` vs `scope.md`

- `brief.md` 讲这个项目为什么存在、要达成什么
- `scope.md` 讲边界是什么、什么不做、有哪些依赖和风险

### `status.md` vs `worklog.jsonl`

- `status.md` 只写现在
- `worklog.jsonl` 记录发生过什么

### `context/research/` vs `memory/facts.jsonl`

- `context/research/` 放处理过但仍偏资料形态的研究内容
- `memory/facts.jsonl` 只放以后还会跨会话直接调用的稳定事实

### `compact-state.md` vs `status.md`

- `compact-state.md` 是机器优先的压缩状态
- `status.md` 是给人读的状态仪表盘

### `artifact` vs `research note`

- artifact 是正式产物，可被稳定引用和交接
- research note 是分析过程中的笔记，不默认是 canonical result

## 什么时候升级为 memory

满足下面至少两条，才适合从 context 升级为 memory：

- 未来还会重复用到
- 可以明确说明来源或触发事件
- 不是一次性中间草稿
- 对判断、执行或复盘有长期价值

## 什么时候成为 artifact

满足下面至少两条，就应考虑写成 artifact：

- 它会被后续多次引用
- 它是阶段成果或正式结论
- 它适合交给下一个会话或下一个 agent
- 它比口头总结更稳定、更可验证

## `scope` 字段规则

所有 memory 条目都必须带 `scope`：

- `project`：只适用于当前项目
- `cross_project`：可能适用于多个项目
- `global`：已被确认适合作为全局脑层记忆
