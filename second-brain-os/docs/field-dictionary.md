# Field Dictionary

这份文档定义 Second Brain OS 里的关键字段，避免脚本和人工填写时语义漂移。

## `projects/index.jsonl`

| 字段 | 含义 |
|---|---|
| `id` | 全局唯一项目 ID |
| `slug` | 项目目录名 |
| `title` | 项目标题 |
| `category` | 执行模式 |
| `domain` | 领域 |
| `status` | `draft | active | blocked | paused | completed | archived` |
| `automation_profile` | 自动化等级 |
| `priority` | `P0 | P1 | P2 | P3` |
| `updated_at` | 最近更新时间 |
| `path` | 项目路径 |

## `project.yaml`

| 字段 | 含义 | 填写说明 |
|---|---|---|
| `id` | 唯一 ID | 不手动改 |
| `slug` | 短路径名 | 小写、短横线 |
| `title` | 项目名 | 用自然语言写清楚 |
| `category` | 项目分类 | 必须来自固定枚举 |
| `domain` | 项目领域 | 必须来自固定枚举 |
| `status` | 当前状态 | 初始一般为 `draft` 或 `active` |
| `current_phase` | 当前阶段 | 如 `intake / discovery / draft / build / review` |
| `objective` | 最终要解决什么 | 只写结果，不写过程 |
| `success_criteria` | 什么算完成 | 尽量写成可验证条件 |
| `stakeholder` | 服务对象是谁 | 可写个人、团队、老板、客户 |
| `owner` | 负责人 | 默认你自己 |
| `priority` | 优先级 | `P0-P3` |
| `automation_profile` | 自动化方式 | `manual | assisted | delegated` |
| `default_read_policy` | 默认读取规则文件 | 通常指向 `context/routing/read-policy.yaml` |
| `current_readset` | 当前 read set 文件 | 通常指向 `context/routing/current-readset.md` |
| `compact_state` | 当前压缩状态文件 | 通常指向 `context/summaries/compact-state.md` |
| `working_summary` | 当前工作摘要文件 | 通常指向 `context/summaries/working-summary.md` |
| `artifact_registry` | artifact 索引文件 | 通常指向 `artifacts/registry.jsonl` |
| `primary_artifact` | 当前主 artifact | 写 canonical artifact 路径或 ID |
| `created_at` | 创建时间 | 自动生成 |
| `updated_at` | 更新时间 | 每次关键变更更新 |
| `tags` | 检索标签 | 3-6 个足够 |

## `worklog.jsonl`

| 字段 | 含义 |
|---|---|
| `timestamp` | 动作发生时间 |
| `actor` | 谁执行的 |
| `action` | 做了什么 |
| `summary` | 结果摘要 |
| `artifact_refs` | 涉及哪些 artifact |
| `next_step` | 下一步是什么 |

## `artifacts/registry.jsonl`

| 字段 | 含义 |
|---|---|
| `artifact_id` | artifact 唯一 ID |
| `title` | artifact 标题 |
| `type` | artifact 类型 |
| `stage` | 所属阶段 |
| `status` | `draft | active | archived | superseded` |
| `canonical_path` | artifact 文件路径 |
| `summary` | 简短摘要 |
| `source_refs` | 来源引用 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## `memory/facts.jsonl`

| 字段 | 含义 |
|---|---|
| `timestamp` | 记录时间 |
| `fact` | 稳定事实 |
| `source` | 来源 |
| `confidence` | 置信度 |
| `scope` | `project | cross_project | global` |
| `status` | `active | archived` |
| `last_verified` | 最近一次核验时间 |

## `memory/decisions.jsonl`

| 字段 | 含义 |
|---|---|
| `timestamp` | 决策时间 |
| `decision` | 决了什么 |
| `rationale` | 为什么这么定 |
| `alternatives` | 放弃了什么 |
| `owner` | 谁做的决定 |
| `scope` | `project | cross_project | global` |
| `status` | `active | archived` |
| `supersedes` | 被取代的旧决策 ID 或说明 |

## `memory/lessons.jsonl`

| 字段 | 含义 |
|---|---|
| `timestamp` | 记录时间 |
| `lesson` | 学到了什么 |
| `trigger` | 由什么事件触发 |
| `impact` | 造成什么影响 |
| `prevention` | 下次如何避免或复用 |
| `scope` | `project | cross_project | global` |
| `status` | `active | archived` |

## `memory/procedures.jsonl`

| 字段 | 含义 |
|---|---|
| `timestamp` | 记录时间 |
| `procedure` | 流程或 playbook 名称 |
| `trigger` | 什么情况下触发 |
| `steps` | 默认步骤 |
| `artifact_target` | 默认产出哪种 artifact |
| `stop_condition` | 到什么条件停止 |
| `scope` | `project | cross_project | global` |
| `status` | `active | archived` |

## `context/manifests/*.jsonl`

| 字段 | 含义 |
|---|---|
| `timestamp` | 本轮会话时间 |
| `goal` | 本轮目标 |
| `files_read` | 读了哪些文件 |
| `files_written` | 写了哪些文件 |
| `summary` | 本轮摘要 |
| `carry_forward` | 下一轮需要继承什么 |
