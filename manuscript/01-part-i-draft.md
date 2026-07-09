# 《Context Engineering》书稿第一版（第一部）

## 前言

过去两年里，很多人把 agent 能力的进步归因于更强的模型、更长的上下文窗口、更丰富的工具调用接口。这些都重要，但它们并没有自动带来可靠的 agent 系统。真正让系统从“偶尔演示成功”走向“长期稳定可用”的，往往不是单点能力，而是工程师是否学会了管理 context。

所谓 context，并不只是提示词。它是模型在某一轮推理中能看见的一切：系统指令、工具定义、检索材料、历史对话、工具输出，以及这些信息的顺序、密度、位置与装载时机。模型越强，这件事越重要，而不是越不重要。因为能力越强，系统越复杂，context 管理失控时带来的退化也越隐蔽。

这本书不打算再写一本 prompt tips 合集。它要解决的是另一个层级的问题：为什么上下文会退化，为什么工具设计本质上是上下文设计，为什么文件系统和记忆系统是 agent 的外置认知层，为什么多 agent 的真正价值是上下文隔离，为什么评估不是最后补上，而是整套设计的证据基础。

本书所有内容都基于本地项目 `Agent-Skills-for-Context-Engineering` 的官方 skills、docs 和 examples 重新组织而成。我们不按仓库目录顺序讲，而按认知依赖关系讲。这样做的目的很明确：让你不仅能学懂，还能在最后反过来把它重写成你自己的书。

如果你读完这本书，能做到三件事，这本书就达成了目标。第一，面对一个新 agent 项目时，你知道该如何判断它是不是 context 问题。第二，你能从案例中反推出真正的工程原则，而不是停留在经验总结。第三，你能用自己的语言，把 Context Engineering 讲给别人听，甚至写成一本书。

## 目录

### 第一部：建立 Context Engineering 的底层认知

1. Context Engineering Fundamentals
2. Context Degradation Patterns
3. Context Compression Strategies
4. Context Optimization

---

# 第一部：建立 Context Engineering 的底层认知

## 第 1 章 Context Engineering Fundamentals

很多人第一次接触 Context Engineering 时，会把它理解成 Prompt Engineering 的升级版。这种理解不完全错，但层级太低。Prompt 只是 context 的一个组成部分，而不是全部。对 agent 系统来说，真正被送进模型的，不只是几段指令文本，还包括工具定义、历史消息、检索到的资料、外部命令返回结果，以及系统在运行过程中不断追加的中间状态。换句话说，工程师真正管理的不是一条 prompt，而是一整套推理现场。

这也是为什么本书把 Context Engineering 的定义放在最前面：它不是“写一段更聪明的提示词”，而是对模型一次推理中全部可见状态进行设计、裁剪、排序和装载。它关注的对象包括 system prompt、tool definitions、retrieved documents、message history 和 tool outputs，也关注这些信息以什么顺序出现、以多大密度出现、在什么时机被加载。

如果 Prompt Engineering 讨论的是“你对模型说什么”，那么 Context Engineering 讨论的是“你让模型在这一轮推理里看见什么、先看见什么、看多久、为了做哪一步决策而看”。这就是为什么它天然比 prompt 更接近系统设计。前者仍然把模型看成一个接受文本输入的接口，后者已经开始把模型看成一个受限注意力系统。

理解这一点，首先要重新看待 context 的组成。System prompt 决定身份、边界和行为基调；tool definitions 决定模型有哪些可行动作以及如何理解动作含义；retrieved documents 提供任务相关外部知识；message history 承担会话内工作记忆；tool outputs 则是 agent 在真实世界行动后的反馈。这里最容易被低估的是 tool outputs。因为在真实 agent 轨迹里，最耗 token 的往往不是用户消息，而是搜索结果、文件内容、命令输出和 API 返回。也就是说，很多系统不是死于 prompt 太弱，而是死于工具输出太肥。

这就引出本章的第一个核心机制：attention budget。模型的上下文窗口从来不是一个“装满就能用”的背包，而更像一个有限注意力池。你塞进去的每一个 token 都会参与竞争。随着上下文增长，模型不是线性地变差，而是越来越难把注意力稳定分配到真正关键的位置。于是，工程的重点不再是“能不能多塞一点”，而是“该不该塞、先塞什么、晚塞什么”。

这也是为什么“更长的 context window”从来不是 Context Engineering 的充分条件。窗口长度只是理论可容纳长度，attention budget 才是模型在该长度内仍能稳定利用的有效能力。一个拥有更长窗口、但被噪声和重复内容填满的系统，并不会自动比一个上下文更短但信号更高的系统更好。真正成熟的上下文设计，永远首先关心信号质量，而不是绝对容量。

第二个核心机制是 progressive disclosure。这个概念在 Agent Skills 格式里尤其清楚：启动时只加载 skill 名称和描述，真正命中任务再加载完整 `SKILL.md`。这不是节省几百 token 的小技巧，而是一种通用工程原则。信息不应该在“也许会用到”的时刻预加载，而应该在“当前决策确实需要它”的时刻按需引入。这个原则可以扩展到整个 agent 系统：文档先载入目录，再载入章节；案例先看摘要，再钻取细节；工具输出先看摘要，再按引用回看原文。

第三个核心机制是 context budgeting。预算不是抽象理念，而是明确的设计动作。你要知道 system prompt 大概占多少、工具描述占多少、历史消息什么时候会膨胀、工具输出会不会在三轮之后淹没用户目标。只要系统涉及长任务、工具调用或文件检索，就迟早要面对这个问题。仓库中建议在 70%-80% 利用率附近触发 compaction，本质上就是承认一个事实：系统不能把 context 当成无限资源来用，而必须像管理 CPU、内存、缓存一样管理它。

因此，本章真正要建立的不是若干术语，而是一种新的工程视角。Context Engineering 的目标不是把更多信息搬进模型，而是把更有决策价值的信息，以更合理的顺序和时机搬进模型。Prompt 只是这个系统里的一个入口，不是全部。真正成熟的 agent 设计，会把指令、工具、文档、历史、外部输出一起看作一个待调度的注意力系统。只有从这个层次理解，后面你才会真正看懂为什么会有 degradation、compression、optimization、filesystem context 和 multi-agent isolation 这些章节。

## 第 2 章 Context Degradation Patterns

很多工程师把长上下文失败理解为一件简单的事：token 太多了，所以模型记不住。这个判断太粗糙。上下文失效不是等到窗口爆掉才出现，而是从很早就开始。系统表面看起来还在正常工作，工具还能调、回答还能生成，但决策质量已经在下降。这种“还没死，但已经偏了”的状态，才是 agent 系统最危险的阶段。

因此，Context Degradation 指的不是“窗口满了”，而是即使上下文窗口还没有真正耗尽，模型的有效理解与决策质量也会随着上下文增长、冲突累积和信号稀释而持续下降。它不是单点故障，而是一组可预期的失效模式，包括 lost-in-the-middle、poisoning、distraction、confusion 和 clash。

第一个最经典的失效模式是 lost-in-the-middle。模型对上下文的注意力分布往往呈 U 形：开头和结尾最容易被稳定检索，中间最容易被忽略。这意味着一个很反直觉的工程结论：同一条关键信息，放在中间和放在边缘，系统表现会不同。很多失败不是因为信息不存在，而是因为信息被埋在不利位置。也因此，真正重要的任务目标、约束、当前状态，应该尽量放在 attention-favored positions，而不是相信模型会平均阅读每一段文本。

第二个失效模式是 poisoning，也就是上下文污染。污染比普通错误更危险，因为它会自我强化。一个错误的 tool output、一个带 hallucination 的中间 summary、一个过时但没被标记的检索文档，都可能进入上下文并被后续推理反复引用。一旦错误进入 goals、plans 或 state，它就不再只是“某次回答错了”，而会开始扭曲后续所有动作。很多 agent 之所以越做越偏，不是因为不会纠错，而是因为错误已经沉淀成了它的当前世界观。

第三个失效模式是 distraction。只要你把东西放进 context，模型就必须分配注意力给它。于是一个本来无害的冗长日志、一篇并不相关的参考文档、一个多余的工具定义，都可能抢走真正关键问题的注意力。对 agent 来说，distraction 常常表现为：回答内容很多，但没有抓住当前任务的核心。

第四个模式是 confusion。它与 distraction 相近，但更偏向适用边界混乱。比如一个系统在同一 session 里先做研究，再做写作，再做代码修改，结果模型开始把前面任务的约束错误地套用到后面的任务上。它不是不知道信息，而是不知道哪些信息属于当前局面。这种混乱往往发生在多任务长会话里，也正是为什么后面的 filesystem context、context partitioning 和 multi-agent isolation 会变得重要。

第五个模式是 clash，即上下文冲突。和 poisoning 不同，clash 不一定来自错误内容，也可能来自两个都“各自正确”的信息源。例如一份旧规范和一份新规范并存、一个版本说明和一段历史代码实现不一致、两个专家观点都合理但彼此矛盾。如果系统没有明确优先级、版本过滤或冲突标记机制，模型就会在矛盾中失去稳定判断。

这一章真正要建立的，不是几个术语，而是一种诊断视角：当 agent 变差时，你不能只问“是不是模型不够强”，而要问“是不是信息位置错了、上下文污染了、噪声太多了、任务边界混了、信息彼此打架了”。从这个角度看，Context Engineering 的后续章节就不再像零散技巧，而像一套治疗方案。Compression 解决的是历史过长后的信息保真，optimization 解决的是高噪声上下文的重新组织，filesystem 和 multi-agent 则是在更高层面隔离和外置这些问题。

因此，degradation 不是一章附属知识，而是整套工程方法为什么存在的病理学基础。你只有先看见系统如何开始变坏，后面才会真正理解为什么要做 compaction、为什么要做 masking、为什么要用文件系统外置状态、为什么要把任务拆入多个 agent context。

## 第 3 章 Context Compression Strategies

一旦 agent 任务跨越足够多轮，对话历史就必然膨胀。这个时候，compression 不是可选优化，而是基本生存条件。但最常见的错误也在这里出现：很多人把 compression 理解成“把旧消息缩写一下”。这会直接把问题做错。Context Compression 的目标根本不是 tokens-per-request，而是 tokens-per-task。也就是说，你不能只看这一次省了多少 token，而必须看整个任务有没有因此少走弯路。

为什么这个视角重要？因为如果压缩丢掉了关键文件路径、错误信息、已做决策或当前状态，agent 很快就会被迫重新搜索、重新读取、重新思考。表面上它的上下文变短了，实际上整个任务消耗反而更大。一个压缩策略哪怕多省 0.5% 的 token，只要造成 20% 的重取成本，它整体就是失败的。真正的工程指标不是“压得多狠”，而是“压完之后还能不能顺着干”。

这也是为什么本章给 compression 的定义，不是“摘要历史”，而是“在长任务或长会话中，对已有上下文进行高保真压缩的工程过程”。它的目标不是单次请求省 token，而是在尽量不丢失关键决策线索、文件轨迹和后续行动依据的前提下，让任务能够继续推进。它与普通摘要的区别在于：普通摘要关心“说得短不短”，Context Compression 关心“压完之后系统还能不能继续正确工作”。

本章最值得重视的概念是 artifact trail problem。对于编码 agent 或长任务 agent，最脆弱的不是抽象主题，而是具体工作痕迹：哪些文件改过、哪些函数动过、哪个错误最早出现、为什么当时做了某个决定。一般摘要很容易保留“我们在调试认证问题”，却丢掉“`config/redis.ts` 已改、`tests/auth.test.ts` 还没过、根因是 stale Redis connection”这种真正决定后续行动的信息。所以 compression 不仅要保留 narrative，还要保留 artifact index。

Anchored Iterative Summarization 是这里的关键方案。它的思路不是每次都重写一份“最新总摘要”，而是先定义固定结构，比如 Session Intent、Files Modified、Decisions Made、Current State、Next Steps；第一次压缩时把旧历史放进这些格子里，后续压缩只总结新增被截断部分，再合并进既有结构。这个方法的价值在于，结构迫使系统保留特定类型的信息，避免每次都凭感觉重新组织，进而产生无声漂移。

这和常见的 full summary regeneration 有本质差别。后者看上去更自然，读起来更像人类总结，但它在多轮压缩后容易逐渐洗掉细节，因为每次都是从“上一个总结”重写“下一个总结”。细节在多轮重写中会不断蒸发。Anchored 方法更像一张稳定表单，每次只更新增量，不把整个历史重新讲一遍，因此更适合 agent 连续工作。

Compression 还需要明确 trigger strategy。重点不是机械地卡某个 token 数，而是承认压缩需要前置触发，不能等到上下文已经明显退化才动手。你越晚压，越容易把已经受损的内容拿去做总结，等于用坏 context 再生成一层坏 context。

这里必须把 compression 与下一章 optimization 的边界说清。Compression 主要处理“已有内容太多，必须压缩”；Optimization 处理的是“现有上下文该怎样重新布置、遮蔽和分区，才能更高效”。Compression 更像存档与续航机制，Optimization 更像实时调度机制。把两者混为一谈，会导致工程师只会做摘要，却不会真正管理信息流。

因此，本章真正要建立的是一种 operational view：压缩不是写摘要，而是维护任务连续性；不是为人类读者服务，而是为后续 agent 决策服务；不是追求极限压缩率，而是追求最少重取、最少遗忘、最小偏航。只有这样，长任务 agent 才有可能在几百轮之后仍然知道自己在做什么、改过什么、下一步该做什么。

## 第 4 章 Context Optimization

经过前两章，我们已经知道两件事：第一，上下文会退化；第二，长任务必须压缩。但如果工程做到这里就停，系统仍然会很笨，因为大量问题并不是来自“历史太长”，而是来自“当前上下文组织得太差”。Context Optimization 讨论的正是这个层面：不是事后缩短，而是运行中持续整理、裁剪、遮蔽、重排和分区，让高价值信息在当前时刻更容易被模型稳定利用。

这一定义很关键。Optimization 不是单次压缩动作，而是一整套运行时策略。它回答的问题是：“当前应该怎样组织上下文，才不让模型被低价值内容拖垮？”相比之下，compression 更偏向“历史太多怎么办”。前者偏调度，后者偏续航。

本章的起点是一个很朴素但非常实用的判断：context quality matters more than quantity。很多团队喜欢追求更大的窗口、更长的日志、更全的检索结果，但模型真正需要的不是“尽可能全”，而是“对当前决策最有帮助”。Optimization 的任务，就是把这条原则落实成具体动作。常见动作包括 compaction、observation masking、KV-cache ordering 和 context partitioning。

先看 compaction。它和上一章 compression 很接近，但这里更强调它作为运行时优化手段的角色。Compression 讨论的是如何高保真地压旧上下文；Optimization 中的 compaction 更像调度阀门：当利用率接近阈值时，哪些部分应该先被摘要、哪些绝不能碰、哪些可以换成引用。这种 compaction 不是“事后整理”，而是系统在运行中持续维持高信号密度的手段。

真正最容易被低估的是 observation masking。tool outputs 往往占 agent context 的绝大部分。也就是说，模型的大量注意力其实花在看命令输出、文件内容、检索原文和日志，而不是花在想问题。Observation masking 的思想非常直接：如果一个输出已经完成了它当时的决策使命，就不该继续以全文形式霸占上下文。应当把它替换成一个引用或高度压缩的关键结论，必要时再按引用回取。这个模式的价值不在于“偷懒不看原文”，而在于让原文从持续负担变成按需资产。

`x-to-book-system` 是一个极好的证据。这个案例里最重的不是 orchestrator 的思考，而是海量 tweet 数据。如果原始 tweet 一层层穿过 orchestrator、analyzer、writer，整个系统很快就会被数据量压垮。系统之所以能工作，不是因为写了一个更好的 prompt，而是因为引入了 observation masking + filesystem coordination：raw tweet 不进入核心代理上下文，而是写到外部存储，需要的阶段再分批读取，后续流转的是 summary 而不是原文。

KV-cache optimization 则把问题推进到更底层。它关心的不是“内容有没有用”，而是“哪些前缀稳定、可以重复利用”。把 system prompt、tool definitions、稳定模板放前面，把动态内容放后面，不只是为了结构清晰，也为了缓存命中率。很多工程师把 prompt 顺序当成美观问题，但从 optimization 视角看，顺序直接影响成本和延迟。

最后是 context partitioning。它代表一种更激进的优化思路：不要总想着在一个上下文里把一切摆平，而应该主动把任务拆进多个上下文，让每个上下文只处理自己该处理的部分。到了这里，你已经可以看出它和后面 multi-agent chapter 的衔接了。Optimization 的终点之一，就是承认有些问题不是再压再排就能解决，而必须从架构层面隔离。

因此，本章要建立的核心判断是：compression 是“把历史缩得还能用”，optimization 是“让当前上下文更值得被看”。前者解决续航，后者解决效率；前者更多处理存量，后者同时处理存量与增量。真正高水平的 agent system 往往不是因为模型更聪明，而是因为它让模型持续工作在一个更干净、更高信号、更少重复负担的上下文环境里。这就是 optimization 的工程价值。
