# Codex 新线程绑定模板

这份文档专门解决一个问题：

**当你在 Codex 里新开线程时，怎么让它只服务 Second Brain OS 里的某个具体项目。**

## 一条最重要的规则

**Codex 的 workspace 应该固定在 Second Brain OS 根目录，而不是直接开在某个项目目录。**

推荐根目录：

`/Users/guapi/Documents/New project/second-brain-os`

原因：

- 这样 Codex 能看到全局规则
- 能读到 `AGENTS.md`
- 能读到 `brain/`
- 能读到 `state/`
- 还能进入具体项目目录

如果你直接把 workspace 开在：

`projects/active/<slug>/`

Codex 就容易丢掉上层的大脑规则，只看到局部项目。

## 线程分 3 种

### 1. OS 主线程

用来维护 Second Brain OS 本身。

适合做：

- 改 `brain/`
- 改 `state/`
- 改模板
- 改脚本
- 改系统文档

### 2. 项目线程

一个线程只服务一个具体项目。

适合做：

- 推进项目执行
- 更新项目状态
- 收集项目资料
- 产出项目交付物

### 3. 项目子线程

当某个项目上下文太重时，再拆子线程。

适合做：

- 单独处理某个研究子问题
- 单独处理某个交付物子模块
- 单独处理某轮重任务

注意：

项目子线程仍然属于同一个项目目录，不是新项目。

## 推荐的线程命名方式

### OS 主线程

`Second Brain OS / Architecture`

### 项目线程

`<项目标题> / Main`

例如：

`内部 AI 周报助手 / Main`

### 项目子线程

`<项目标题> / Research`
`<项目标题> / Draft`
`<项目标题> / Review`

## 开一个新的项目线程时，正确步骤是什么

### Step 1：确认项目已经存在

先在 Second Brain OS 根目录里创建项目：

```bash
python agents/scripts/new_project.py \
  --title "内部 AI 周报助手" \
  --slug internal-ai-weekly \
  --category build \
  --domain work
```

### Step 2：在 Codex 里打开根目录

工作区固定为：

`/Users/guapi/Documents/New project/second-brain-os`

### Step 3：新开一个线程

这个线程只服务一个项目，不要混多个项目。

### Step 4：把下面这段提示词贴到线程第一条消息

把 `<slug>` 改成你的项目目录名。

---

## 项目线程启动模板

```text
把这个线程绑定到项目：
/Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>

先按这个顺序读取：
1. /Users/guapi/Documents/New project/second-brain-os/AGENTS.md
2. /Users/guapi/Documents/New project/second-brain-os/state/system-status.md
3. /Users/guapi/Documents/New project/second-brain-os/state/current-focus.md
4. /Users/guapi/Documents/New project/second-brain-os/brain/project-routing.md
5. /Users/guapi/Documents/New project/second-brain-os/brain/principles.md
6. /Users/guapi/Documents/New project/second-brain-os/brain/ontology.md
7. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/project.yaml
8. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/session-brief.md
9. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/context/routing/current-readset.md
10. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/context/summaries/compact-state.md
11. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/next-actions.md
12. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/workflow.md
13. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/context/summaries/handoff.md

从现在开始：
- 默认只在这个项目目录下工作
- 不改其他项目
- 不改 brain/ 和 state/，除非我明确要求
- 长输出写到这个项目的 context/tool_outputs/
- 临时草稿写到 context/pad/
- 不要直接全量读取 tool_outputs/、inputs/、research/、artifacts/archive/
- 优先引用 artifacts/current/ 和 compact-state，而不是重复拷贝结论
- 会话结束前更新 next-actions.md、worklog.jsonl、compact-state.md、handoff.md，并写 manifest
```

---

## 如果这个线程是 OS 主线程，用这段

```text
把这个线程绑定到 Second Brain OS 本体：
/Users/guapi/Documents/New project/second-brain-os

先按这个顺序读取：
1. /Users/guapi/Documents/New project/second-brain-os/AGENTS.md
2. /Users/guapi/Documents/New project/second-brain-os/state/system-status.md
3. /Users/guapi/Documents/New project/second-brain-os/state/current-focus.md
4. /Users/guapi/Documents/New project/second-brain-os/brain/project-routing.md
5. /Users/guapi/Documents/New project/second-brain-os/brain/principles.md
6. /Users/guapi/Documents/New project/second-brain-os/brain/ontology.md
7. /Users/guapi/Documents/New project/second-brain-os/brain/rubrics.md
8. /Users/guapi/Documents/New project/second-brain-os/README.md
9. /Users/guapi/Documents/New project/second-brain-os/docs/context-os-upgrade.md

从现在开始：
- 这个线程只维护 Second Brain OS 本体
- 不进入具体项目执行，除非我明确要求
- 优先修改 brain/、state/、docs/、templates/、scripts/
- 所有改动都要保持项目模板和全局规则一致
```

## 如果这个线程是项目子线程，用这段

把 `<slug>` 和 `<focus>` 改掉。

```text
把这个线程绑定到项目：
/Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>

这个线程只处理当前项目中的这个子任务：
<focus>

先按这个顺序读取：
1. /Users/guapi/Documents/New project/second-brain-os/AGENTS.md
2. /Users/guapi/Documents/New project/second-brain-os/brain/ontology.md
3. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/project.yaml
4. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/session-brief.md
5. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/context/routing/current-readset.md
6. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/context/summaries/compact-state.md
7. /Users/guapi/Documents/New project/second-brain-os/projects/active/<slug>/next-actions.md
8. 与这个子任务直接相关的 context/ 和 artifacts/current/ 文件

从现在开始：
- 这个线程只服务这个子任务
- 不重构整个项目
- 长输出写到该项目的 context/tool_outputs/
- 子任务草稿写到 context/pad/
- 子任务结论优先写成 artifact，再回写主项目文件
```

## 一个真实例子

假设你的项目目录是：

`/Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly`

那你新开线程时，第一条消息直接可以写成：

```text
把这个线程绑定到项目：
/Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly

先按这个顺序读取：
1. /Users/guapi/Documents/New project/second-brain-os/AGENTS.md
2. /Users/guapi/Documents/New project/second-brain-os/state/system-status.md
3. /Users/guapi/Documents/New project/second-brain-os/state/current-focus.md
4. /Users/guapi/Documents/New project/second-brain-os/brain/project-routing.md
5. /Users/guapi/Documents/New project/second-brain-os/brain/principles.md
6. /Users/guapi/Documents/New project/second-brain-os/brain/ontology.md
7. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/project.yaml
8. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/session-brief.md
9. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/context/routing/current-readset.md
10. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/context/summaries/compact-state.md
11. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/next-actions.md
12. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/workflow.md
13. /Users/guapi/Documents/New project/second-brain-os/projects/active/internal-ai-weekly/context/summaries/handoff.md

从现在开始：
- 默认只在这个项目目录下工作
- 不改其他项目
- 不改 brain/ 和 state/，除非我明确要求
- 长输出写到这个项目的 context/tool_outputs/
- 临时草稿写到 context/pad/
- 不要直接全量读取 tool_outputs/、inputs/、research/、artifacts/archive/
- 会话结束前更新 next-actions.md、worklog.jsonl、compact-state.md、handoff.md，并写 manifest
```

## 竞品分析项目示例

如果你现在就要开一个“竞品分析”项目，最简单的做法是：

- 把它归到 `category = research`
- 把它放在 `second-brain-os/` 根目录下面管理
- 新线程仍然绑定整个 OS 根目录，但首条消息明确绑定具体项目目录

### Step 1：如果项目还没创建，先创建

在：

`/Users/guapi/Documents/New project/second-brain-os`

里运行：

```bash
python agents/scripts/new_project.py \
  --title "AI Coding Agent 竞品分析" \
  --slug ai-coding-agent-competitive-analysis \
  --category research \
  --domain work \
  --automation-profile assisted \
  --priority P1 \
  --owner guapi
```

### Step 2：新开 Codex 线程时，workspace 固定在根目录

也就是：

`/Users/guapi/Documents/New project/second-brain-os`

不要直接把 workspace 开在：

`/Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis`

### Step 3：线程第一条消息直接贴下面这段

```text
把这个线程绑定到项目：
/Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis

这是一个竞品分析项目，项目类型是 research。
这轮目标是：建立竞品分析的项目骨架，明确研究范围、竞品名单、研究维度和第一版 artifact。

先按这个顺序读取：
1. /Users/guapi/Documents/New project/second-brain-os/AGENTS.md
2. /Users/guapi/Documents/New project/second-brain-os/state/system-status.md
3. /Users/guapi/Documents/New project/second-brain-os/state/current-focus.md
4. /Users/guapi/Documents/New project/second-brain-os/brain/project-routing.md
5. /Users/guapi/Documents/New project/second-brain-os/brain/principles.md
6. /Users/guapi/Documents/New project/second-brain-os/brain/ontology.md
7. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/project.yaml
8. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/session-brief.md
9. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/context/routing/current-readset.md
10. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/context/summaries/compact-state.md
11. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/next-actions.md
12. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/workflow.md
13. /Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis/context/summaries/handoff.md

从现在开始：
- 这个线程只服务这个竞品分析项目
- 不修改其他项目
- 不修改 brain/ 和 state/，除非我明确要求
- 如果要收集外部资料，先把原始资料和长输出放到 context/tool_outputs/ 或 context/research/
- 结论不要散落在聊天里，阶段成果优先写成 artifacts/current/ 下的 artifact
- 不要直接全量读取 tool_outputs/、inputs/、research/、artifacts/archive/
- 这轮结束前更新 next-actions.md、worklog.jsonl、compact-state.md、handoff.md，并写 manifest

当前请先做下面 5 件事：
1. 检查这个 research 项目的模板是否完整
2. 补齐 project.yaml 里的 objective、success_criteria、current_phase、primary_artifact
3. 在 brief.md 里写清研究目标、服务对象、时间范围、输出物
4. 在 scope.md 里写清研究范围、排除范围、假设、风险
5. 给出第一版研究计划，并把本轮应该读取的文件写进 current-readset.md
```

### Step 4：如果项目已经存在，只做这两件事

1. 新开线程，workspace 仍然固定在：
   `/Users/guapi/Documents/New project/second-brain-os`
2. 把上面的首条消息直接贴进去，只把项目路径、项目名、这轮目标改掉

### Step 5：第二轮以后怎么写

第二轮开始，不用每次都写很长。  
你只要保留“绑定项目 + 读取顺序 + 本轮目标”这三件事。

例如：

```text
把这个线程绑定到项目：
/Users/guapi/Documents/New project/second-brain-os/projects/active/ai-coding-agent-competitive-analysis

先读取：
1. AGENTS.md
2. 项目的 project.yaml
3. session-brief.md
4. context/routing/current-readset.md
5. context/summaries/compact-state.md
6. next-actions.md
7. context/summaries/handoff.md

本轮目标：
- 继续推进这个竞品分析项目
- 基于已有研究材料，产出第一版竞品对比 artifact
- 不新增无关结构，不改 brain/ 和 state/

会话结束前更新：
- next-actions.md
- worklog.jsonl
- compact-state.md
- handoff.md
- manifest
```

## 什么时候需要新开线程，而不是在原线程继续

建议新开线程的情况：

- 你要切换到另一个项目
- 当前线程已经跑太久，上下文很重
- 你要把项目拆成单独子任务
- 你要从“项目执行”切回“OS 架构维护”

不建议新开线程的情况：

- 只是同一个项目里的下一步
- 只是补一个小文件
- 只是更新状态

## 如果线程跑偏了，怎么拉回来

如果 Codex 在一个项目线程里开始改别的项目，或者开始动 `brain/`、`state/`，直接贴这段：

```text
这个线程只绑定当前项目，不要修改其他项目，也不要修改 brain/ 和 state/。
请重新回到这个项目的入口文件：
1. project.yaml
2. session-brief.md
3. context/routing/current-readset.md
4. context/summaries/compact-state.md
5. next-actions.md
然后只继续这个项目的当前动作。
```

## 最后记住一句话

**线程绑定靠的不是“换 workspace”，而是“根目录固定 + 首条消息明确绑定项目 + 固定读取顺序”。**
