# Week 3 术语表 v1

## 1. Context Isolation

一句话定义：把不同子任务放入彼此隔离的上下文中执行。
与相邻概念的边界：不同于单纯角色拆分，它强调减少上下文互扰。
在本地仓库中的证据：`skills/multi-agent-patterns/SKILL.md`

## 2. Supervisor Pattern

一句话定义：由中央协调 agent 统一分解、分发和汇总任务的模式。
与相邻概念的边界：比 swarm 更强调控制与检查点。
在本地仓库中的证据：`skills/multi-agent-patterns/SKILL.md`

## 3. Swarm Pattern

一句话定义：agent 之间可直接 handoff、缺少中央固定控制器的协作模式。
与相邻概念的边界：更灵活，但更依赖收敛协议。
在本地仓库中的证据：`skills/multi-agent-patterns/SKILL.md`

## 4. Hierarchical Pattern

一句话定义：按战略、规划、执行等层级组织 agent 的架构模式。
与相邻概念的边界：比 supervisor 更强调抽象层分离。
在本地仓库中的证据：`skills/multi-agent-patterns/SKILL.md`

## 5. Telephone Game Problem

一句话定义：信息在多层 agent 摘要转述中逐渐失真。
与相邻概念的边界：它是协调链损耗问题，不是单个 agent 理解错误。
在本地仓库中的证据：`skills/multi-agent-patterns/SKILL.md`

## 6. Handoff Protocol

一句话定义：agent 之间转交任务和状态的明确机制。
与相邻概念的边界：不是普通消息，而是有边界和格式的控制流切换。
在本地仓库中的证据：`skills/multi-agent-patterns/SKILL.md`

## 7. Sandbox Infrastructure

一句话定义：为 hosted agents 提供隔离执行环境的基础设施层。
与相邻概念的边界：它不仅隔离代码运行，也承载会话状态与环境一致性。
在本地仓库中的证据：`skills/hosted-agents/SKILL.md`

## 8. Warm Pool

一句话定义：预先准备好的可快速分配给新会话的沙箱池。
与相邻概念的边界：不同于普通 autoscaling，它强调交互前预热。
在本地仓库中的证据：`skills/hosted-agents/SKILL.md`

## 9. Snapshot and Restore

一句话定义：对工作区文件系统状态做快照并支持恢复。
与相邻概念的边界：比保存聊天记录更接近真实工作连续性。
在本地仓库中的证据：`skills/hosted-agents/SKILL.md`

## 10. Predictive Warm-Up

一句话定义：在用户发送请求前就开始准备 agent 运行环境。
与相邻概念的边界：它优化的是运行时可用性，不是模型本身响应速度。
在本地仓库中的证据：`skills/hosted-agents/SKILL.md`

## 11. Self-Spawning Agents

一句话定义：agent 能够启动新的 agent 会话去并行完成子任务。
与相邻概念的边界：比普通 multi-agent 更依赖基础设施支持。
在本地仓库中的证据：`skills/hosted-agents/SKILL.md`

## 12. Task-Model Fit

一句话定义：一个任务是否与 LLM 的能力和局限匹配。
与相邻概念的边界：它先于 prompt 设计与系统实现。
在本地仓库中的证据：`skills/project-development/SKILL.md`

## 13. Manual Prototype

一句话定义：在自动化前，用一个代表性样本人工测试模型能力。
与相邻概念的边界：它不是 demo，而是项目可行性验证。
在本地仓库中的证据：`skills/project-development/SKILL.md`

## 14. Pipeline Architecture

一句话定义：把 LLM 项目拆成清晰、可重跑、可缓存的阶段。
与相邻概念的边界：不同于把所有逻辑塞进一个 agent loop。
在本地仓库中的证据：`skills/project-development/SKILL.md`

## 15. Acquire → Prepare → Process → Parse → Render

一句话定义：LLM 项目的经典阶段化流水线。
与相邻概念的边界：它不是唯一形式，但能明确区分贵且不稳定的 LLM 调用阶段。
在本地仓库中的证据：`skills/project-development/SKILL.md`

## 16. File System as State Machine

一句话定义：用文件存在与否和中间产物来表示项目执行状态。
与相邻概念的边界：不同于把状态藏进数据库或内存结构。
在本地仓库中的证据：`skills/project-development/SKILL.md`

## 17. Structured Output Design

一句话定义：为后续程序解析而设计的严格输出格式规范。
与相邻概念的边界：不只是让回答更整齐，而是为了提高 parsing reliability。
在本地仓库中的证据：`skills/project-development/SKILL.md`

## 18. Architectural Reduction

一句话定义：先用更少、更通用的架构和工具验证系统，而不是预设复杂骨架。
与相邻概念的边界：它不是功能阉割，而是减少无效脚手架。
在本地仓库中的证据：`skills/project-development/SKILL.md`

