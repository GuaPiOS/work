# WordyDesk Context Hub

如果后续继续开发 `WordyDesk`，不要再从整段对话历史恢复上下文，直接按下面顺序读：

1. [PROJECT_STATE.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/PROJECT_STATE.md)
2. [ARCHITECTURE.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/ARCHITECTURE.md)
3. [BACKLOG.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/BACKLOG.md)
4. [RUNBOOK.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/RUNBOOK.md)

## 使用原则

- `PROJECT_STATE.md` 只写当前真实状态，不写愿景。
- `ARCHITECTURE.md` 只写稳定结构，不写一次性讨论。
- `BACKLOG.md` 只保留还没完成的事，完成后及时删除或迁移到状态文件。
- 每次完成一轮开发后，优先更新这 4 份文件，再继续下一轮。

## 最小恢复路径

一个新会话如果只想快速接手：

1. 读 `PROJECT_STATE.md`
2. 读 `BACKLOG.md`
3. 执行 `RUNBOOK.md` 里的编译和安装命令

这样通常足够继续开发，不需要重新消费长对话。
