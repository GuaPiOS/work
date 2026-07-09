# Week 3 案例报告：从 `x-to-book-system` 与 `book-sft-pipeline` 反推架构选择

## 一、为什么 `x-to-book-system` 选择 Multi-Agent

### 任务结构

- 数据来源大且连续
- 原始 tweet 数量巨大
- 输出不是简单总结，而是结构化长文
- 阶段之间存在清晰顺序和质量门

### 关键风险

- Orchestrator 若直接持有 raw tweets，会迅速 context saturation
- 单 agent 会在抓取、分析、综合、写作之间不断切换任务面
- 工具输出体量过大，容易造成观察污染

### 选择理由

- 用 supervisor 统一协调阶段
- 用文件系统做共享状态，避免电话游戏
- 用 context budgets 控制各 agent 的工作面
- 用 observation masking 隔离原始数据

### 结论

`x-to-book-system` 的架构核心不是“很多 agent 协作更酷”，而是“单一上下文不再可靠，必须把任务拆成多个可控上下文”。

## 二、为什么 `book-sft-pipeline` 更像 Pipeline-First 项目

### 任务结构

- 输入和输出边界清晰
- 阶段顺序明确
- 大量工作是批处理
- 中间产物需要被验证和重跑

### 关键风险

- 如果 extraction、segmentation、instruction generation 混成一团，难以 debug
- 如果不把训练前数据构造拆开，很难知道问题到底出在文本、提示还是训练配置
- 如果没有 validation，容易误把内容记忆当风格学习

### 选择理由

- 用 staged pipeline 管理昂贵且不稳定的 LLM 调用
- 用中间文件保存阶段结果，支持缓存和重跑
- 用 structured outputs 让下游能稳定解析
- 用 modern scenario test 验证真正学到的是 style 而不是 content

### 结论

`book-sft-pipeline` 展示的不是“多 agent 越多越好”，而是“当问题天然是阶段化批处理时，pipeline-first 往往比复杂 agent 架构更优”。

## 三、两者的共通方法论

- 都没有从 prompt 开始，而是从任务结构开始
- 都把昂贵、易膨胀的上下文留在受控边界内
- 都使用文件系统保存阶段状态
- 都把评估和验证嵌入设计，而不是最后补上

## 四、两者的关键差异

| 维度 | `x-to-book-system` | `book-sft-pipeline` |
| --- | --- | --- |
| 主结构 | Multi-agent supervisor | Stage-based pipeline |
| 核心问题 | 上下文隔离与协调 | 阶段拆分与可验证性 |
| 主要风险 | 协调失真、上下文过载 | 黑箱化、难 debug |
| 主要外置层 | 文件系统 + temporal KG | 文件系统 + structured outputs |

## 五、给你的实战判断句

如果你面对的新任务：

- 更像多阶段内容生产、跨阶段质量门、超大原始数据流
优先考虑 `x-to-book-system` 路线。

- 更像批处理、数据预处理、模型调用、解析和验证的流水线
优先考虑 `book-sft-pipeline` 路线。
