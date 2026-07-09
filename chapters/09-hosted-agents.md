# 第 9 章：Hosted Agents

## 章节定位

本章把 context engineering 从“提示和架构”推进到“运行时基础设施”。

## 对应官方 skill

- `skills/hosted-agents/SKILL.md`

## 必读材料

- `skills/hosted-agents/SKILL.md`
- `README.md`

## 问题

当 agent 需要长时间运行、读写文件、使用工具、并行执行时，运行环境本身开始决定上下文策略。本章回答为什么 hosted agents 属于 context engineering。

## 核心论点

Hosted agents 不是部署附录，而是运行时上下文工程。它把 context 的管理对象从消息窗口扩展到环境镜像、会话状态、文件快照和并发执行单元。

## 定义

Hosted Agents 指的是运行在远程沙箱、预热环境或托管基础设施中的 agent 系统。它们不再依赖用户本地机器作为唯一执行现场，而是把文件系统、依赖环境、会话快照、并行会话和多人协作一起纳入 agent runtime。

从 Context Engineering 的角度看，hosted 不是“换台机器跑”，而是让 environment state 也成为上下文的一部分，并通过基础设施设计降低启动延迟、状态丢失和并发干扰。

## 机制

重点解释：

- sandbox infrastructure
- warm pools
- snapshots
- self-spawning agents
- multiplayer support

## 技术模式

- move heavy state into environment
- snapshot filesystem, not just messages
- optimize startup path before full sync
- separate API layer from agent runtime

## 案例证据

- 从 `hosted-agents` skill 的 sandbox / warm pool / snapshot 模式取证
- 回连 `filesystem-context` 和 `multi-agent-patterns`

## 边界比较

### Hosted Agents vs Local Agents

- Local agent 主要受限于本地资源、环境漂移和单用户串行执行。
- Hosted agent 把运行环境标准化，并允许高并发与远程持久化。
- 前者的上下文主要在当前会话，后者的上下文还包括远程环境状态。

### Hosted Agents vs Multi-Agent

- Multi-agent 解决的是任务如何拆分与隔离上下文。
- Hosted agents 解决的是这些 agent 在什么运行时环境里工作，以及如何快速恢复、并发和共享状态。
- 两者常常结合，但层次不同：一个偏架构，一个偏基础设施。

## 反模式

- 把 hosted agents 理解成纯部署问题
- 只保存消息，不保存环境状态
- 让远程 agent 冷启动承担全部延迟

## 写作练习

写 800-1200 字，回答：

“为什么 hosted agents 的真正升级，不是把 agent 放到云上，而是把上下文管理扩展到运行环境本身？”

## 章节草稿

到这一步，我们已经知道 agent 会遇到上下文退化，也知道可以通过 filesystem、memory 和 multi-agent 去缓解。但还有一个经常被忽略的问题：如果 agent 本身要长时间运行、要调用很多工具、要保留文件状态、还要并行执行，那么“它跑在哪里”会直接反过来影响上下文管理。`hosted-agents` skill 的价值，就在于把这个基础设施问题重新收回到 Context Engineering 主线中。

很多人会把 hosted agents 当成“把 agent 部署到云上”。这个理解太弱。仓库真正强调的是，session speed should be limited only by model provider time-to-first-token。这句话背后隐含着一个更深的目标：用户不应该把等待环境准备、依赖安装、仓库同步、缓存预热这些基础设施成本，误认为是 agent 的工作成本。也就是说，hosted infrastructure 的首要任务，是把环境准备从交互时刻前移，给 agent 提供一个几乎随时可工作的外部上下文现场。

这就引出了 image registry、warm pool 和 snapshot 这些模式。它们不是运维技巧，而是 runtime context engineering。预构建镜像意味着依赖、仓库、缓存和初始运行状态已经在用户开始前准备好；warm pool 意味着 agent 会话不必每次从冷启动开始；snapshot 则意味着文件系统状态本身可以被恢复，而不是只恢复几条聊天记录。对 coding agent 来说，这一点尤其关键，因为真正决定连续性的往往不是 messages，而是工作区已经改到了哪、依赖跑到了哪、临时文件和测试产物处在什么状态。

这也是 hosted agents 与 filesystem context 的深层连接。前一章里，文件系统承担的是外置上下文和动态发现；到了 hosted agents，这个文件系统已经不只是目录树，而是一个可快照、可恢复、可多人共享、可并发复制的运行时状态载体。换句话说，environment state 也开始进入 Context Engineering 的版图。

另一个容易被忽略的点是 predictive warm-up。仓库建议在用户开始输入时就启动 sandbox 预热，而不是等用户按下回车。这看起来像体验优化，实际上也是上下文优化。因为它减少了 agent 从“空环境”到“可行动环境”的等待时间，使系统更接近真正的连续工作流。一个总在冷启动中的 agent，即使模型再强，也很难在用户心智里形成“它在持续工作”的感觉。

Hosted agents 还把多 agent 的问题进一步放大了。当前两章里，多 agent 主要还是逻辑拆分；到了这里，agent 甚至可以 self-spawn，开启新的会话去并行做研究、改不同 repo、拆多个 PR。这时我们处理的已经不是“多个上下文窗口”，而是“多个沙箱中的多个上下文窗口”。如果基础设施层没有 per-session isolation、状态同步和轻量 check-in 机制，多 agent 架构就很容易在运行时变得不可控。

因此，hosted agents 的关键价值不在于“能远程跑”，而在于把 agent 的上下文管理从 message-level 扩展到了 runtime-level。你开始要管理的不只是 prompt、history、docs 和 tool outputs，还包括镜像、快照、会话数据库、并发沙箱、用户身份和客户端同步。Context Engineering 到这里，已经不再只是 prompt 或架构问题，而是完整的系统运行时设计问题。

## 学习检查

1. 为什么说 hosted agents 不是纯部署问题？
2. Snapshot 为什么是上下文连续性的关键设施之一？
3. Hosted agents 和 multi-agent 的关系是什么？
