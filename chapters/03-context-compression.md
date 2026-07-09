# 第 3 章：Context Compression Strategies

## 章节定位

本章处理长任务中的“如何不失忆”。它不是简单总结聊天记录，而是设计信息保真策略。

## 对应官方 skill

- `skills/context-compression/SKILL.md`

## 必读材料

- `skills/context-compression/SKILL.md`
- `docs/compression.md`

## 问题

当 session 足够长时，压缩不是可选项。问题不再是压不压，而是“压缩后还能不能继续干活”。

## 核心论点

Compression 的本质不是缩短文本，而是保持任务连续性。压缩失败的标志不是摘要不好看，而是 agent 必须返工、重取、重判。

## 定义

Context Compression 是在长任务或长会话中，对已有上下文进行高保真压缩的工程过程。它的目标不是单次请求省 token，而是在尽量不丢失关键决策线索、文件轨迹和后续行动依据的前提下，让任务能够继续推进。

它与普通摘要的区别在于：普通摘要关心“说得短不短”，Context Compression 关心“压完之后系统还能不能继续正确工作”。

## 机制

重点解释：

- tokens-per-task
- artifact trail problem
- anchored iterative summarization
- compression trigger strategies

## 技术模式

- anchored summary
- file/state index preservation
- incremental merge over full regeneration
- probe-based evaluation

## 案例证据

- `context-compression` skill 中的 structured sections
- `book-sft-pipeline` 中分段与信息密度思路的借鉴

## 边界比较

### Compression vs Summarization

- Summarization 主要面向人类阅读理解。
- Compression 面向 agent 后续继续执行任务。
- 前者关注可读性，后者关注可续航性。

### Compression vs Optimization

- Compression 处理的是“历史太多，必须缩”。
- Optimization 处理的是“当前怎么摆更有效”。
- Compression 偏续航，Optimization 偏调度。

## 反模式

- 追求极限压缩率却不看恢复成本
- 每次都重写完整 summary，导致细节漂移
- 不单独记录 files modified / decisions made

## 写作练习

写 800-1200 字，回答：

“为什么 context compression 的正确目标不是每次请求更省 token，而是整个任务完成得更省 token？”

## 章节草稿

一旦 agent 任务跨越足够多轮，对话历史就必然膨胀。这个时候，compression 不是可选优化，而是基本生存条件。但最常见的错误也在这里出现：很多人把 compression 理解成“把旧消息缩写一下”。`context-compression` skill 提供的关键纠正是，压缩的目标根本不是 tokens-per-request，而是 tokens-per-task。也就是说，你不能只看这一次省了多少 token，而必须看整个任务有没有因此少走弯路。

为什么这个视角重要？因为如果压缩丢掉了关键文件路径、错误信息、已做决策或当前状态，agent 很快就会被迫重新搜索、重新读取、重新思考。表面上它的上下文变短了，实际上整个任务消耗反而更大。仓库把这个问题说得很清楚：一个压缩策略哪怕多省 0.5% 的 token，只要造成 20% 的重取成本，它整体就是失败的。真正的工程指标不是“压得多狠”，而是“压完之后还能不能顺着干”。

本章最值得重视的概念是 artifact trail problem。对于编码 agent 或长任务 agent，最脆弱的不是抽象主题，而是具体工作痕迹：哪些文件改过、哪些函数动过、哪个错误最早出现、为什么当时做了某个决定。一般摘要很容易保留“我们在调试认证问题”，却丢掉“`config/redis.ts` 已改、`tests/auth.test.ts` 还没过、根因是 stale Redis connection”这种真正决定后续行动的信息。所以仓库才强调，压缩不仅要保留 narrative，还要保留 artifact index。

Anchored Iterative Summarization 是这里给出的核心方案。它的思路不是每次都重写一份“最新总摘要”，而是先定义固定结构，比如 Session Intent、Files Modified、Decisions Made、Current State、Next Steps；第一次压缩时把旧历史放进这些格子里，后续压缩只总结新增被截断部分，再合并进既有结构。这个方法的价值在于，结构迫使系统保留特定类型的信息，避免每次都凭感觉重新组织，进而产生无声漂移。

这和常见的 full summary regeneration 有本质差别。后者看上去更自然，读起来更像人类总结，但它在多轮压缩后容易逐渐洗掉细节，因为每次都是从“上一个总结”重写“下一个总结”。细节在多轮重写中会不断蒸发。Anchored 方法更像一张稳定表单，每次只更新增量，不把整个历史重新讲一遍，因此更适合 agent 连续工作。

Compression 还需要明确 trigger strategy。仓库给出的几种方式里，固定阈值和 sliding window 最适合多数工程场景。重点不是机械地卡某个 token 数，而是承认压缩需要前置触发，不能等到上下文已经明显退化才动手。你越晚压，越容易把已经受损的内容拿去做总结，等于用坏 context 再生成一层坏 context。

Compression 与下一章 optimization 的边界也必须在这里说清。Compression 主要处理“已有内容太多，必须压缩”；Optimization 处理的是“现有上下文该怎样重新布置、遮蔽和分区，才能更高效”。Compression 更像存档与续航机制，Optimization 更像实时调度机制。把两者混为一谈，会导致工程师只会做摘要，却不会真正管理信息流。

所以，本章真正要建立的是一种 operational view：压缩不是写摘要，而是维护任务连续性；不是为人类读者服务，而是为后续 agent 决策服务；不是追求极限压缩率，而是追求最少重取、最少遗忘、最小偏航。只有这样，长任务 agent 才有可能在几百轮之后仍然知道自己在做什么、改过什么、下一步该做什么。

## 学习检查

1. 为什么 tokens-per-request 会误导 compression 设计？
2. Artifact trail 为什么比主题概括更难保留？
3. Anchored iterative summarization 为什么比 full regeneration 更适合长任务？
