# Context Engineering 学习与成书工程

这个仓库把 `/Users/guapi/Documents/GitHub/Agent-Skills-for-Context-Engineering` 的官方 13 个 skills，重组为一套可执行的 4 周冲刺课程，同时也是一本中文书的写作骨架。

目标不是复述仓库内容，而是完成三件事：

1. 学会用 Context Engineering 的视角分析 agent 系统
2. 能把官方 skills、docs、examples 重新组织成自己的知识体系
3. 最后能基于这套骨架继续扩写成一本中文书

## 教材边界

仅使用官方 13 个 skills：

- `context-fundamentals`
- `context-degradation`
- `context-compression`
- `context-optimization`
- `multi-agent-patterns`
- `memory-systems`
- `tool-design`
- `filesystem-context`
- `hosted-agents`
- `evaluation`
- `advanced-evaluation`
- `project-development`
- `bdi-mental-states`

明确排除：

- `market-research`
- `scrapling`

## 仓库结构

```text
curriculum/
  00-roadmap.md
  01-4-week-bootcamp.md
  02-writing-protocol.md
  03-case-map.md
  04-review-checklists.md
chapters/
  01-context-fundamentals.md
  02-context-degradation.md
  03-context-compression.md
  04-context-optimization.md
  05-tool-design.md
  06-filesystem-context.md
  07-memory-systems.md
  08-multi-agent-patterns.md
  09-hosted-agents.md
  10-project-development.md
  11-evaluation.md
  12-advanced-evaluation.md
  13-bdi-mental-states.md
manuscript/
  01-part-i-draft.md
```

## 使用顺序

1. 先读 [curriculum/00-roadmap.md](/Users/guapi/Documents/New project/curriculum/00-roadmap.md)
2. 再按 [curriculum/01-4-week-bootcamp.md](/Users/guapi/Documents/New project/curriculum/01-4-week-bootcamp.md) 执行 4 周学习
3. 每周写作时遵循 [curriculum/02-writing-protocol.md](/Users/guapi/Documents/New project/curriculum/02-writing-protocol.md)
4. 查案例映射时使用 [curriculum/03-case-map.md](/Users/guapi/Documents/New project/curriculum/03-case-map.md)
5. 每章学习直接进入 `chapters/` 对应章节文件补写

## 书稿入口

如果你要看连续可读的书稿版本，先读：

- [manuscript/01-part-i-draft.md](/Users/guapi/Documents/New project/manuscript/01-part-i-draft.md)

这份文件目前包含：

- 前言
- 第一部目录
- 第 1-4 章正式书稿第一版

继续阅读：

- [manuscript/02-part-ii-draft.md](/Users/guapi/Documents/New project/manuscript/02-part-ii-draft.md)
- [manuscript/03-part-iii-draft.md](/Users/guapi/Documents/New project/manuscript/03-part-iii-draft.md)
- [manuscript/04-part-iv-v-draft.md](/Users/guapi/Documents/New project/manuscript/04-part-iv-v-draft.md)
- [manuscript/00-full-book-draft.md](/Users/guapi/Documents/New project/manuscript/00-full-book-draft.md)

目前书稿进度：

- 第一部：第 1-4 章
- 第二部：第 5-7 章
- 第三部：第 8-10 章
- 第四、五部：第 11-13 章与结语
- 全书总入口：`manuscript/00-full-book-draft.md`

课程材料继续保留在 `curriculum/` 和 `chapters/`，书稿稿件单独收束在 `manuscript/`。

## 学习原则

- 先讲机制，再讲口号
- 先讲边界，再讲应用
- 先从本地项目取证，再做抽象总结
- 每章必须输出自己的中文解释，而不是翻译原文

## 附加工具：WordyDesk

仓库里新增了一个独立的 macOS 菜单栏小工具源码，现已整理到 `apps/wordydesk/`。

如果要继续开发这个工具，不要只依赖对话历史，先读：

- [apps/wordydesk/README.md](/Users/guapi/Documents/New project/apps/wordydesk/README.md)

功能：

- 在任意 macOS 应用里选中单词后，按 `Option-Command-G` 尝试抓取当前选中文本
- 使用系统美式英语语音朗读单词和例句
- 一键收藏到本地 Markdown 笔记
- 笔记默认保存到 `~/Library/Application Support/WordyDesk/collected-words.md`

运行方式：

1. 用 Xcode 打开 [apps/wordydesk/Package.swift](/Users/guapi/Documents/New project/apps/wordydesk/Package.swift)
2. 选择 `WordyDesk` 目标并运行
3. 首次使用时，到 `System Settings > Privacy & Security > Accessibility` 给应用授权

命令行打包：

1. 运行 `apps/wordydesk/scripts/build_app_bundle.sh`
2. 生成的 app 位于 `apps/wordydesk/dist/WordyDesk.app`
3. 当前已经安装到 `/Applications/WordyDesk.app`

说明：

- 由于当前工具链环境缺少完整 Xcode GUI 运行条件，这里交付的是源码工程
- 全局取词依赖系统辅助功能权限；若权限未开启，按钮和快捷键可能拿不到外部应用里的选中文本
