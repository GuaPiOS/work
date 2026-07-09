# Second Brain OS

Second Brain OS 是一套面向 `ChatGPT + Codex` 的 file-based context operating system。

它不是某个具体项目，而是一层主控骨架，用来统一这些事情：

- 项目分类
- 项目工作区结构
- context 路由
- context 压缩
- 全局状态管理
- artifact 交接
- 跨项目记忆沉淀

## 设计原则

- `write`：把上下文写进文件，而不是堆在对话里
- `select`：按项目、阶段、任务读取最小必要上下文
- `compress`：把临时材料压缩成 summaries、artifacts、memory
- `isolate`：用项目工作区隔离不同任务类型的上下文
- `handoff`：让下一轮或下一个 agent 直接接收 artifact 和 compact state

## 目录地图

```text
second-brain-os/
├── AGENTS.md
├── brain/
├── state/
├── docs/
├── inbox/
├── projects/
├── ops/
└── agents/
```

## 核心层

- `brain/`：系统主控层，定义原则、术语、分类规则、全局记忆
- `state/`：系统级状态层，记录当前 OS 的整体阶段和近 1-2 周焦点
- `projects/`：项目工作区和模板
- `docs/`：架构说明、升级设计、字段字典、项目文件职责、案例

## 快速开始

1. 先读 `AGENTS.md`
2. 再读 `docs/context-os-upgrade.md`
3. 再读 `docs/second-brain-os-sop.md`
4. 再读 `brain/project-routing.md`
5. 看 `state/system-status.md` 和 `state/current-focus.md`
6. 需要开新项目时运行：

```bash
python agents/scripts/new_project.py \
  --title "内部 AI 周报助手" \
  --slug internal-ai-weekly \
  --category build \
  --domain work
```

7. 项目建立后，从 `session-brief.md` 和 `context/routing/current-readset.md` 进入，不先读整个项目目录

## 使用手册

- 架构图与结构说明：`docs/architecture.md`
- 升级设计总说明：`docs/context-os-upgrade.md`
- 新手完整操作指南：`docs/second-brain-os-sop.md`
- Codex 新线程绑定模板：`docs/codex-thread-template.md`
- 项目工作区职责：`docs/project-workspace-guide.md`
- 字段解释：`docs/field-dictionary.md`

## 当前约束

- 路径和 schema 用英文
- 文档正文用中文
- `.jsonl` 一律 append-only
- 不上数据库、向量库、hosted agents
- artifact 优先于聊天和临时草稿
