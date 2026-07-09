# 《Context Engineering》书稿第一版（第三部）

# 第三部：从单 Agent 走向系统级架构

## 第 8 章 Multi-Agent Architecture Patterns

很多人对多 agent 的第一反应是“把一个人做的事分给几个人做”。这个说法不完全错，但会把问题讲浅。多 agent 的核心价值，不在于组织学，而在于上下文工程。更准确地说，多 agent 的首要作用不是模拟团队分工，而是把一个过载的 context 拆成多个可控 context。

这也是为什么本章会把多 agent 定义为：将复杂任务分配给多个拥有独立上下文窗口、独立工具集或独立职责边界的 agent，通过协调机制完成单一上下文难以稳定完成的任务。从 Context Engineering 角度看，多 agent 的本质不是模拟公司组织结构，而是通过上下文隔离减少注意力稀释、上下文污染和工具冲突，让每个 agent 在更窄、更干净的任务面上工作。

为什么单 agent 会先坏在这里？因为任务复杂度上升时，最先遇到的不是“不会思考”，而是 context bottleneck。历史消息越来越长，检索资料越来越多，工具输出越堆越厚，结果就是一个上下文里既有原始数据、又有中间计划、又有失败记录、又有多轮决策。到这一步，即使模型本身还很强，它也要在一个混杂环境里持续切换注意力，失误率自然上升。

多 agent 提供的解决方案不是神秘的“集体智能”，而是更朴素的分区。让不同 agent 只看到与自己阶段相关的上下文：研究 agent 只关心搜索与资料，分析 agent 只关心抽象主题和模式，写作 agent 只关心局部内容生成，编辑 agent 只关心审阅和改写。每个 agent 都在更窄的任务面里工作，因此 attention budget 更集中，工具选择也更清晰。

`x-to-book-system` 是这一点最典型的案例。这个系统为什么采用 supervisor/orchestrator，而不是 swarm？不是因为“中台更高级”，而是因为它的工作流本身有清晰阶段：scrape、analyze、synthesize、write、edit。这样的任务天然适合中央协调，因为阶段之间存在质量门、状态依赖和人类监督需求。选择 supervisor 的原因，不是架构偏好，而是任务结构使然。

但 supervisor 也有一个经典问题，就是 telephone game。也就是子代理把结果给协调者，协调者再转述给下一层或用户，信息在每一层摘要中逐渐失真。这也是为什么真正有效的 supervisor 系统，必须减少协调者的二次解释负担。`x-to-book-system` 的做法就是：raw tweet 和 phase outputs 主要落到文件系统，orchestrator 只看阶段摘要，不搬运原始数据。

这也解释了为什么多 agent 不能简单理解成“多模型一起聊聊”。如果多个 agent 最终还是共享一份大上下文、依赖同一条消息链来同步状态，那你并没有真正获得隔离，只是引入了更多通信成本。真正有效的多 agent，一定有清晰的 isolation 机制：独立上下文、有限 handoff、文件系统共享状态或明确的 summary schema。

本章还必须面对一个现实：多 agent 很贵。复杂多 agent 任务可能达到单 agent chat 的十几倍 token 消耗。所以我们不能把多 agent 当默认答案。它只在三种情况下值得：第一，任务天然可分阶段或可并行；第二，不同子任务确实需要不同工具和不同上下文；第三，单 agent 的上下文退化已经开始伤害质量。否则，多 agent 只是在用更多成本包装一个本可由单 agent 完成的流程。

因此，本章真正要建立的判断是：多 agent 是一种 context partitioning architecture。它服务于一个非常具体的工程目标：让不同推理过程在不同上下文中发生，减少互相干扰，并通过协调层把结果重新拼回任务目标。

## 第 9 章 Hosted Agents

到这一步，我们已经知道 agent 会遇到上下文退化，也知道可以通过 filesystem、memory 和 multi-agent 去缓解。但还有一个经常被忽略的问题：如果 agent 本身要长时间运行、要调用很多工具、要保留文件状态、还要并行执行，那么“它跑在哪里”会直接反过来影响上下文管理。Hosted agents 讨论的正是这个层面。

很多人会把 hosted agents 当成“把 agent 部署到云上”。这个理解太弱。更准确的定义是：运行在远程沙箱、预热环境或托管基础设施中的 agent 系统。它们不再依赖用户本地机器作为唯一执行现场，而是把文件系统、依赖环境、会话快照、并行会话和多人协作一起纳入 agent runtime。从 Context Engineering 的角度看，hosted 不是“换台机器跑”，而是让 environment state 也成为上下文的一部分。

这一点为什么重要？因为用户不应该把等待环境准备、依赖安装、仓库同步、缓存预热这些基础设施成本，误认为是 agent 的工作成本。也就是说，hosted infrastructure 的首要任务，是把环境准备从交互时刻前移，给 agent 提供一个几乎随时可工作的外部上下文现场。

这就引出了 image registry、warm pool 和 snapshot 这些模式。它们不是运维技巧，而是 runtime context engineering。预构建镜像意味着依赖、仓库、缓存和初始运行状态已经在用户开始前准备好；warm pool 意味着 agent 会话不必每次从冷启动开始；snapshot 则意味着文件系统状态本身可以被恢复，而不是只恢复几条聊天记录。对 coding agent 来说，这一点尤其关键，因为真正决定连续性的往往不是 messages，而是工作区已经改到了哪、依赖跑到了哪、临时文件和测试产物处在什么状态。

这也是 hosted agents 与 filesystem context 的深层连接。文件系统在前一章承担的是外置上下文和动态发现；到了 hosted agents，这个文件系统已经不只是目录树，而是一个可快照、可恢复、可多人共享、可并发复制的运行时状态载体。换句话说，environment state 也开始进入 Context Engineering 的版图。

另一个容易被忽略的点是 predictive warm-up。系统可以在用户开始输入时就启动 sandbox 预热，而不是等用户按下回车。这不是小的体验修饰，而是在减少 agent 从“空环境”到“可行动环境”的等待时间，使系统更接近真正的连续工作流。一个总在冷启动中的 agent，即使模型再强，也很难在用户心智里形成“它在持续工作”的感觉。

Hosted agents 还把多 agent 的问题进一步放大。前一章里，多 agent 主要还是逻辑拆分；到了这里，agent 甚至可以 self-spawn，开启新的会话去并行做研究、改不同 repo、拆多个 PR。此时我们处理的已经不是“多个上下文窗口”，而是“多个沙箱中的多个上下文窗口”。如果基础设施层没有 per-session isolation、状态同步和轻量 check-in 机制，多 agent 架构就很容易在运行时变得不可控。

因此，hosted agents 的关键价值不在于“能远程跑”，而在于把 agent 的上下文管理从 message-level 扩展到了 runtime-level。你开始要管理的不只是 prompt、history、docs 和 tool outputs，还包括镜像、快照、会话数据库、并发沙箱、用户身份和客户端同步。Context Engineering 到这里，已经不再只是 prompt 或架构问题，而是完整的系统运行时设计问题。

## 第 10 章 Project Development Methodology

在很多 LLM 项目里，最大的失败不是 prompt 写得不好，也不是模型能力不够，而是项目一开始就选错了问题。Project Development 这一章的第一个动作不是建系统，而是 task-model fit recognition。这个顺序特别重要，因为它在提醒我们：不是所有看上去“可以让 AI 做”的任务，都值得交给 LLM 或 agent。

这也是为什么本章要把 project development 定义为：在构建 LLM 或 agent 系统前，先验证任务与模型能力是否匹配，再用分阶段、可缓存、可调试的方式组织数据流、LLM 调用和输出解析，逐步增加复杂度。它不是通用项目管理框架，而是专门面向 LLM 系统的开发方法论。它要解决的不是“怎么排期”，而是“什么该让模型做、什么不该让模型做、什么时候该引入更复杂的 agent 架构”。

仓库列出的判断标准非常实用。LLM 更适合做跨来源综合、带 rubric 的主观判断、自然语言生成、允许一定误差的批处理任务；不适合做精确计算、严格实时、必须完全确定、或者高度依赖隐藏私有数据的工作。这个判断不是抽象理念，而是直接决定你后面该不该写代码。如果任务本身和模型能力错位，后面无论是 tool design、memory 还是 multi-agent，都只是在为错误方向增加复杂度。

所以这一章强调的第二个关键动作是 manual prototype。也就是，在自动化之前，先拿一个代表性样本去手工喂给目标模型，看看它到底会不会、效果大概到什么程度、失败模式是什么。这个动作非常朴素，但极其重要。它会在几十分钟内回答一个价值极高的问题：这个项目是值得继续搭，还是应该马上止损。很多工程浪费，其实都发生在“手工试一下就能知道不行”的地方。

一旦 task-model fit 成立，方法论就转入 pipeline architecture。经典顺序是 acquire → prepare → process → parse → render。这个顺序看起来像普通数据流水线，但对 LLM 项目尤其重要，因为它把“贵且不稳定的 LLM 调用”从其他确定性阶段隔离出来。这样一来，你可以重复调试 prepare、parse 和 render，而不用每次重跑最贵的那一步。

`book-sft-pipeline` 是这里最好的案例。它把整套工作拆成 extraction、segmentation、instruction generation、dataset construction、training、validation。你可以把它看成 acquire/prepare/process/parse/render 的扩展版。这个案例的价值，不只是它做了一个风格迁移训练系统，而是它示范了怎样把一个看似“大而模糊”的生成任务，拆成多个有清晰边界、可单独验证、可反复迭代的阶段。复杂系统不是靠一次性大 prompt 搞定，而是靠阶段化设计逐层收束。

本章的另一个关键视角，是 file system as state machine。项目状态最好不要一开始就塞进复杂数据库或内存状态机，而是用文件存在与否、目录阶段产物、可读中间文件来表示“进行到哪一步”。这和前面的 filesystem context 形成了非常自然的衔接。因为在 LLM 项目里，最贵、最难 debug 的部分往往不是 deterministic logic，而是那一次已经花钱跑出来的模型结果。只要中间文件可见，你就拥有了缓存、调试和重跑边界。

这一章还必须把“要不要用 multi-agent”这个问题从偏好里拉出来。multi-agent 的主理由仍然是 context isolation，而不是“项目显得更高级”。如果一个任务天然是批处理、单 item 独立、阶段线性清晰，那么 single pipeline 往往已经足够。只有当任务开始超出单上下文容量、需要并行探索、或者阶段间的上下文差异非常大时，多 agent 才开始有正收益。

因此，Project Development 这一章真正要建立的，是一套起步顺序：先判断问题是否适合模型，再手工试一个样本，再用阶段化流水线组织成本和状态，再根据上下文压力决定是否升级到多 agent 或 hosted runtime。成熟的方法论，不是更快开始写 prompt，而是更早知道该不该开始。
