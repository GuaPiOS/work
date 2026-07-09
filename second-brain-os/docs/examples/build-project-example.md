# Build Project Example

这个案例演示一个 `build` 类型工作项目如何使用升级后的 Second Brain OS。

## 项目背景

项目名：为团队搭一个内部 AI 周报助手

分类应为：

- `category: build`
- `domain: work`
- `automation_profile: assisted`

## `project.yaml` 应该怎么填

```yaml
id: "proj_20260315_internal_ai_weekly"
slug: "internal-ai-weekly"
title: "内部 AI 周报助手"
category: "build"
domain: "work"
status: "active"
objective: "4 周内完成一个可运行 PoC，让周报整理时间减少 50%"
success_criteria:
  - "可读取 3 个固定数据源"
  - "能生成标准周报草稿"
  - "团队试用后认为可继续迭代"
stakeholder: "部门负责人"
owner: "guapi"
priority: "P1"
automation_profile: "assisted"
current_phase: "discovery"
default_read_policy: "context/routing/read-policy.yaml"
current_readset: "context/routing/current-readset.md"
compact_state: "context/summaries/compact-state.md"
working_summary: "context/summaries/working-summary.md"
artifact_registry: "artifacts/registry.jsonl"
primary_artifact: "artifacts/current/20260315_discovery_internal-ai-weekly_architecture-note.md"
created_at: "2026-03-15T00:00:00+08:00"
updated_at: "2026-03-15T00:00:00+08:00"
tags:
  - "weekly-report"
  - "internal-tool"
  - "ai-agent"
```

## `brief.md` 应该写什么

- 为什么做：周报整理耗时高，重复劳动多
- 想达成什么：做出一个内部可试用 PoC
- 成功标准：能稳定生成草稿，并节省一半整理时间
- 服务对象：内部团队和负责人
- 约束：不接外部敏感 API，不自动发送邮件

## `scope.md` 应该写什么

### In

- 读取 3 个固定来源
- 合并信息
- 产出标准周报草稿
- 人工复核后再发布

### Out

- 自动对外发送
- 全公司推广
- 实时聊天机器人接口

### Risks

- 数据格式不统一
- 周报标准可能还没定型

## `session-brief.md` 应该怎么用

它只保留本轮最重要的入口信息，例如：

- 当前阶段：PoC 设计期
- 本轮最可能工作：确认输入字段、搭第一版生成链路
- Mandatory Read：`project.yaml`、`current-readset.md`、`compact-state.md`、`next-actions.md`
- Forbidden Direct Read：旧的工具输出、旧的 research、历史 artifact archive
- 最大风险：上游数据结构还不稳定

## `compact-state.md` 应该写什么

- 当前阶段
- 当前目标
- 激活中的事实
- 激活中的决策
- 当前主 artifact
- 最近 3 个动作

它的作用不是给人讲故事，而是让下一轮 agent 快速接上。

## `next-actions.md` 典型前三项

1. 整理 3 个数据源样本
2. 确认周报模板字段
3. 建第一版生成链路

## `artifacts/registry.jsonl` 例子

```json
{"artifact_id":"art_001","title":"第一版周报助手架构说明","type":"architecture-note","stage":"discovery","status":"active","canonical_path":"artifacts/current/20260315_discovery_internal-ai-weekly_architecture-note.md","summary":"定义输入、流程和第一版边界。","source_refs":["brief.md","scope.md"],"created_at":"2026-03-15T10:00:00+08:00","updated_at":"2026-03-15T10:00:00+08:00"}
```

## `memory/decisions.jsonl` 例子

```json
{"timestamp":"2026-03-16T10:00:00+08:00","decision":"第一版只做周报草稿，不做自动发送","rationale":"先验证生成质量，再处理分发风险","alternatives":"直接集成发送链路","owner":"guapi","scope":"project","status":"active","supersedes":""}
```

## 这个案例说明什么

- `build` 项目重点不是资料堆积，而是阶段推进
- `session-brief.md` 和 `current-readset.md` 可以显著减少进入项目的读取负担
- `compact-state.md` 是机器优先的启动状态
- architecture note 这类结果应该先成为 artifact，再被其他文件引用
- 关键取舍不应只留在聊天里，而应进入 `memory/decisions.jsonl`
