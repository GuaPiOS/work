# Second Brain OS Agent Rules

这个目录是一个 file-based context operating system。任何 agent 在这里工作时，都必须遵守下面的规则。

## 固定规则

1. 新任务先分类，再开工。
2. 先读 `state/`，再读 `brain/`，最后才进入具体项目。
3. 不把“文件存在”当作“应该注入上下文”。先选，再读。
4. 长输出必须落到项目 `context/tool_outputs/`，不要长留在对话里。
5. 摘要、compact state、handoff 和 artifact 优先于聊天内容。
6. 项目级事实、决策、教训、流程只写到项目 `memory/`；跨项目后再晋升到 `brain/memory/`。
7. `pad/` 只放临时草稿，不允许无限堆积。
8. 每次会话结束前，至少要更新项目 `next-actions.md`、`worklog.jsonl`、`context/summaries/compact-state.md`、`context/summaries/handoff.md`，并写入一条 manifest。
9. `status.md` 是人类仪表盘，不承担全部压缩职责。
10. `session-brief.md` 和 `context/routing/current-readset.md` 是项目入口页。进入大项目时先读它们，不默认全量读项目目录。

## 默认读取顺序

### 系统级

1. `state/system-status.md`
2. `state/current-focus.md`
3. `brain/project-routing.md`
4. `brain/principles.md`
5. `brain/ontology.md`

### 项目级

1. `project.yaml`
2. `session-brief.md`
3. `context/routing/current-readset.md`
4. `context/summaries/compact-state.md`
5. `next-actions.md`
6. `workflow.md`
7. `context/summaries/handoff.md`
8. `open-questions.md`

## Context 处理规则

- 原始输入进 `context/inputs/`
- 可信资料进 `context/sources/`
- 已处理研究进 `context/research/`
- 大工具输出进 `context/tool_outputs/`
- 临时推演进 `context/pad/`
- 当前压缩状态进 `context/summaries/`
- 读取规则进 `context/routing/`
- 每轮读写记录进 `context/manifests/`

## Mandatory / Optional / Forbidden

### Mandatory read set

进入项目时默认必须先读：

- `project.yaml`
- `session-brief.md`
- `context/routing/current-readset.md`
- `context/summaries/compact-state.md`
- `next-actions.md`

### Optional read set

只在当前任务需要时才读：

- `workflow.md`
- `open-questions.md`
- `context/summaries/working-summary.md`
- `memory/facts.jsonl`
- `memory/decisions.jsonl`
- `memory/lessons.jsonl`
- `memory/procedures.jsonl`
- 由 `current-readset.md` 点名的 artifact 或 research note

### Forbidden direct read

默认不应直接注入：

- 整个 `context/tool_outputs/`
- 整个 `context/inputs/`
- 整个 `context/research/`
- 整个 `artifacts/archive/`
- 超过预算的原始长文档

先读 summary 或 targeted excerpt，再决定是否读原文。

## Context Budget

- 任意单个文件超过 `160` 行或 `8 KB`，视为长文件
- `tool_outputs/` 下的文件默认 summary-first
- `inputs/` 和 `sources/` 默认只读被 `current-readset.md` 指定的片段或摘要
- 启动时默认直接注入文件不超过 `6` 个
- 需要第 `7` 个文件时，先检查是否已有 compact summary 或 artifact

## Pad 清理规则

每次会话结束时，`context/pad/` 里的内容必须被标记为以下四种处理方式之一：

- 删除
- 继续保留为 working note
- 提升到 `context/research/`
- 提升到 `memory/`

未分类 pad 不应长期累积。

## Artifact-first 规则

- 阶段性成果优先写成 `artifacts/current/` 下的独立 artifact
- `artifacts/registry.jsonl` 是 artifact 索引
- `status.md`、`brief.md`、`working-summary.md` 只保留 artifact 引用和摘要，不重复拷贝全文
- 新结论如果已经形成独立文档，后续引用该 artifact，而不是在多个文件里再写一遍
