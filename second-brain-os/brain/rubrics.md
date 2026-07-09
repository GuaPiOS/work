# Rubrics

## 项目质量

### A. 结构完整

- 项目是否有完整工作区
- 关键文件是否齐全
- `session-brief.md` 是否能独立引导会话进入
- `artifacts/registry.jsonl` 是否存在并被使用

### B. 边界清晰

- `brief.md` 是否说清目标
- `scope.md` 是否说清 in / out / risks / dependencies
- 是否存在内容混放

### C. 状态可信

- `status.md` 是否反映当前快照
- `compact-state.md` 是否反映当前可执行状态
- `next-actions.md` 是否是可执行动作
- `worklog.jsonl` 是否持续记录

## Context 质量

### A. 读取是否克制

- 是否默认只读最小必要文件
- 是否按 `current-readset.md` 读取
- 是否把大输出及时落盘

### B. 证据是否可追溯

- 研究结论是否能找到来源
- memory 是否能找到触发事件或出处
- artifact 是否能找到输入和引用来源

### C. 生命周期是否健康

- `pad/` 是否及时清理
- `research/` 和 `memory/` 是否边界明确
- 是否存在清晰的中间压缩层
- 是否存在长期未分类内容

## 执行质量

### A. 会话闭环

- 会话结束前是否更新状态、下一步、日志、manifest
- 是否写了 handoff 和 compact state

### B. 决策显式化

- 关键取舍是否写入 `memory/decisions.jsonl`

### C. 复用能力

- 项目结束后是否能把经验提升到 `brain/memory/`
- procedures 是否被显式记录并可复用
