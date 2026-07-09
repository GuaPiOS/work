# Part A. 设计诊断

## 当前 OS 的强项

- 已经有 `brain/`、`state/`、`projects/` 的基本分层
- 已经意识到项目状态、项目日志、项目 memory 需要分开
- 已经有 `session-brief.md` 和 `scope` 字段，说明你在控制上下文入口
- 已经用文件系统而不是数据库作为第一层运行时

## 当前 OS 的风险

- 仍然偏“文件组织系统”，还不够像“上下文调度系统”
- 默认读取规则不够明确，agent 仍需要靠猜
- `status.md` 容易被迫承担压缩职责
- `deliverable` 思维强于 `artifact` 思维，交接对象不够稳定
- 缺少 procedural memory，导致流程偏好只能散落在 workflow 或人脑里

## 当前最关键的缺口

1. 缺 `select`：不知道下一轮默认应该读什么
2. 缺 `compress`：没有稳定中间压缩层
3. 缺 `artifact-first`：主结论还容易落在状态文档里
4. 缺 `budget policy`：没有明确文件注入预算
5. 缺 `handoff`：会话结束后的交接对象不够强

# Part B. 建议的新信息架构

```text
second-brain-os/
├── AGENTS.md
├── README.md
├── brain/
│   ├── identity.md
│   ├── principles.md
│   ├── preferences.yaml
│   ├── project-routing.md
│   ├── rubrics.md
│   ├── ontology.md
│   └── memory/
│       ├── facts.jsonl
│       ├── decisions.jsonl
│       ├── lessons.jsonl
│       └── procedures.jsonl
├── state/
│   ├── system-status.md
│   └── current-focus.md
├── docs/
│   ├── architecture.md
│   ├── context-os-upgrade.md
│   ├── second-brain-os-sop.md
│   ├── project-workspace-guide.md
│   ├── field-dictionary.md
│   └── codex-thread-template.md
├── projects/
│   ├── index.jsonl
│   ├── active/
│   ├── archive/
│   └── _templates/
│       ├── base/
│       ├── build/
│       ├── research/
│       ├── operations/
│       ├── writing/
│       ├── delivery/
│       └── learning/
└── ops/
```

推荐的单项目结构：

```text
projects/active/<slug>/
├── project.yaml
├── session-brief.md
├── workflow.md
├── brief.md
├── scope.md
├── plan.md
├── status.md
├── next-actions.md
├── open-questions.md
├── worklog.jsonl
├── context/
│   ├── inputs/
│   ├── sources/
│   ├── research/
│   ├── tool_outputs/
│   ├── pad/
│   ├── routing/
│   │   ├── read-policy.yaml
│   │   └── current-readset.md
│   ├── summaries/
│   │   ├── compact-state.md
│   │   ├── working-summary.md
│   │   ├── rolling-summary.md
│   │   └── handoff.md
│   └── manifests/
├── artifacts/
│   ├── current/
│   ├── archive/
│   └── registry.jsonl
├── memory/
│   ├── facts.jsonl
│   ├── decisions.jsonl
│   ├── lessons.jsonl
│   └── procedures.jsonl
└── reviews/
```

# Part C. 核心文件职责定义

## `project.yaml`

- 作用：项目的稳定元数据入口
- 应存：身份、分类、当前阶段、默认路由文件、compact state 指针、artifact registry 指针
- 不应存：长摘要、长计划、长结论

## `session-brief.md`

- 作用：项目启动导航页
- 应存：当前阶段、当前模式、mandatory read、optional read、forbidden direct read、当前风险
- 不应存：完整研究内容、完整状态历史

## `status.md`

- 作用：人类看的项目仪表盘
- 应存：当前进展、健康度、主要风险、当前 canonical artifact 引用
- 不应存：会话级压缩全量信息

## `next-actions.md`

- 作用：最近 3-5 个可执行动作
- 应存：具体可执行动作
- 不应存：长期愿望、泛泛目标

## `open-questions.md`

- 作用：记录当前阻塞或未决问题
- 应存：问题、影响、负责人、预期决策时间

## `context/routing/read-policy.yaml`

- 作用：项目类型默认路由规则
- 应存：mandatory/optional/forbidden、预算阈值、summary-first 策略

## `context/routing/current-readset.md`

- 作用：当前这一轮真正需要读的文件清单
- 应存：本轮必须读、可选读、禁止直读、被点名的 artifact / research / memory
- 必须每轮重写，而不是无限追加

## `context/summaries/compact-state.md`

- 作用：下一轮启动时默认注入的 compact state
- 应存：当前阶段、目标、关键事实、激活中的决策、当前 artifact、下一步
- 必须短、必须重写、必须可直接注入

## `context/summaries/working-summary.md`

- 作用：当前活跃工作上下文的中层压缩
- 应存：比 compact state 更丰富的阶段性摘要
- 不应变成历史日志

## `context/summaries/rolling-summary.md`

- 作用：跨多轮的压缩历史
- 应存：项目到目前为止的关键进展链
- 应定期重写，不应无限追加

## `context/summaries/handoff.md`

- 作用：给下一轮或另一个 agent 的交接页
- 应存：本轮完成了什么、哪些 artifact 是主交接对象、下一轮先读什么

## `artifacts/*`

- 作用：承载正式成果
- `current/` 放仍有效的 canonical artifact
- `archive/` 放被替代或冻结的 artifact
- `registry.jsonl` 是唯一 artifact 索引

## `memory/*`

- 作用：承载稳定事实、关键决策、经验教训、流程模式
- 应存：未来还会复用的结构化信息
- 不应存：一次性草稿、临时思路、纯资料拷贝

## `context/research/*`

- 作用：分析过程中的研究笔记和处理结果
- 不应直接充当最终交接对象，除非它被提升为 artifact

## `context/tool_outputs/*`

- 作用：承载长工具输出
- 默认禁止直接整份注入
- 先摘要，再按需读片段

## `context/pad/*`

- 作用：临时推演区
- 会话结束必须清理

# Part D. Context Routing 规则

## 启动项目时的默认读取顺序

1. `project.yaml`
2. `session-brief.md`
3. `context/routing/current-readset.md`
4. `context/summaries/compact-state.md`
5. `next-actions.md`
6. `workflow.md`
7. `context/summaries/handoff.md`

## Mandatory read set

- `project.yaml`
- `session-brief.md`
- `context/routing/current-readset.md`
- `context/summaries/compact-state.md`
- `next-actions.md`

## Optional read set

- `workflow.md`
- `open-questions.md`
- `context/summaries/working-summary.md`
- 被 `current-readset.md` 指定的 research note
- 被 `current-readset.md` 指定的 artifact
- 被 `current-readset.md` 指定的 memory 条目

## Forbidden direct read

- 整个 `context/tool_outputs/`
- 整个 `context/inputs/`
- 整个 `context/research/`
- 整个 `artifacts/archive/`
- 任意超过预算的原始长文件

## 长文档处理规则

- 先读 summary 或 excerpt
- 只有在 summary 不足时才读原文
- 任何目录型内容都不应“全量注入”

# Part E. Compression / Compaction 规则

## 哪些内容需要压缩

- 原始输入
- tool outputs
- 长 research notes
- 多轮状态变化
- 子任务阶段结果

## 压缩层放哪里

- `context/summaries/compact-state.md`
- `context/summaries/working-summary.md`
- `context/summaries/rolling-summary.md`
- `context/summaries/handoff.md`

## 更新规则

### `compact-state.md`

- 每次有实质进展就重写
- 保持短小
- 下一轮默认必读

### `working-summary.md`

- 当前阶段上下文明显变化时重写
- 新 artifact 生成后优先更新

### `rolling-summary.md`

- 每 3-5 轮会话重写一次
- 或超过预算后重写

### `handoff.md`

- 每轮结束都应更新
- 下一轮或下一个 agent 先读它

## 触发条件

触发 compact / rewrite 的典型条件：

- 新增或替换 canonical artifact
- `next-actions.md` 变化较大
- 项目阶段切换
- research / tool output 已明显膨胀
- 新决策改变后续路径

## 归档条件

- artifact 被更新版本替代
- 阶段性产物冻结
- 旧 summary 已不再有启动价值
- 旧 tool output 已有高质量摘要和 artifact 覆盖

# Part F. Artifact-first 机制

## 什么应该成为 artifact

- 阶段成果
- 正式结论
- 可被后续多次引用的结构化结果
- 可交给下一个会话继续加工的产物

## 命名规范

推荐：

`YYYYMMDD_<stage>_<slug>_<kind>.md`

例如：

`20260315_discovery_internal-ai-weekly_architecture-note.md`

## Artifact registry

必须有 `artifacts/registry.jsonl`，最少字段：

- `artifact_id`
- `title`
- `type`
- `stage`
- `status`
- `canonical_path`
- `summary`
- `source_refs`
- `created_at`
- `updated_at`

## 引用规则

- `status.md` 只引用 artifact
- `brief.md` 只引用重要 artifact，不拷贝全文
- `handoff.md` 优先交接 artifact，再交接摘要
- 一个结论只有一个 canonical artifact

# Part G. Memory Schema

## `facts`

- 存什么：稳定、可验证、未来还会用到的事实
- 不存什么：推测、临时中间结论
- 何时写：事实被确认后
- 何时读：当前任务需要稳定约束时

建议字段：

- `timestamp`
- `fact`
- `source`
- `confidence`
- `scope`
- `status`
- `last_verified`

## `decisions`

- 存什么：关键取舍及理由
- 不存什么：普通动作记录
- 何时写：路径发生关键分叉时
- 何时读：当前任务依赖历史选择时

建议字段：

- `timestamp`
- `decision`
- `rationale`
- `alternatives`
- `owner`
- `scope`
- `status`
- `supersedes`

## `lessons`

- 存什么：教训、失败模式、有效做法
- 不存什么：一时情绪
- 何时写：复盘或明显踩坑之后
- 何时读：类似任务再次出现时

建议字段：

- `timestamp`
- `lesson`
- `trigger`
- `impact`
- `prevention`
- `scope`
- `status`

## `procedures`

- 存什么：可复用的流程模式、playbook、任务默认步骤
- 不存什么：某次会话的一次性 next action
- 何时写：一类任务的做法已经多次验证后
- 何时读：项目启动或切换到某类任务时

建议字段：

- `timestamp`
- `procedure`
- `trigger`
- `steps`
- `artifact_target`
- `stop_condition`
- `scope`
- `status`

# Part H. 项目类型默认策略

## `research`

- 默认 read set：`project.yaml`、`session-brief.md`、`current-readset.md`、`compact-state.md`、`open-questions.md`
- 默认 summary：research summary 优先，原始 source 次之
- 默认 artifact：evidence brief、comparison matrix、research memo
- 不应直接进入 prompt：全量 sources、全量 tool outputs
- 额外压缩触发：sources 超过 5 份、研究笔记超过 3 篇

## `build`

- 默认 read set：`project.yaml`、`session-brief.md`、`current-readset.md`、`compact-state.md`、`next-actions.md`、`memory/decisions.jsonl`
- 默认 summary：compact state + current build summary
- 默认 artifact：spec、architecture note、prototype result、decision record
- 不应直接进入 prompt：旧 logs、旧 artifact archive、整目录 research
- 额外压缩触发：阶段切换、方案分叉、实现日志膨胀

## `operations`

- 默认 read set：`project.yaml`、`session-brief.md`、`current-readset.md`、`compact-state.md`、`next-actions.md`、`memory/procedures.jsonl`
- 默认 summary：latest operational state + last review
- 默认 artifact：runbook、checklist、review note、dashboard snapshot
- 不应直接进入 prompt：全量历史记录、长期 archive
- 额外压缩触发：周期复盘后、流程变更后

## `writing`

- 默认 read set：`project.yaml`、`session-brief.md`、`current-readset.md`、`compact-state.md`、`brief.md`
- 默认 summary：outline / source summary 优先，原始 research 次之
- 默认 artifact：outline、draft、revision note、final copy
- 不应直接进入 prompt：全量 research、旧版本全文、长 tool outputs
- 额外压缩触发：草稿超过 2 个版本、source notes 过多、结构切换

# Part I. 最终改造清单

## 应新增

- `context/routing/read-policy.yaml`
- `context/routing/current-readset.md`
- `context/summaries/compact-state.md`
- `context/summaries/working-summary.md`
- `context/summaries/rolling-summary.md`
- `context/summaries/handoff.md`
- `artifacts/registry.jsonl`
- `artifacts/current/`
- `artifacts/archive/`
- `memory/procedures.jsonl`
- `brain/memory/procedures.jsonl`
- `writing` 项目类型

## 应删除

- `brain/memory/judgments.jsonl`

## 应合并或降级

- `status.md` 降级为人类仪表盘
- 压缩职责从 `status.md` 分流到 `compact-state.md` / `working-summary.md` / `rolling-summary.md`

## 应改名

- `deliverables/` -> `artifacts/`
- `judgments` -> `decisions`

## 必须升级为硬约束

- 启动时必须先读 mandatory read set
- `tool_outputs/` 默认禁止直接整份注入
- 每个项目必须有 `compact-state.md`
- 每个项目必须有 `artifacts/registry.jsonl`
- 每个项目必须有 `memory/procedures.jsonl`
- `pad/` 必须会话级清理
- artifact 优先于聊天和状态文档
