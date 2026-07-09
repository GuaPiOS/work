# 设计审查与验收清单

## 一、认知测试

你是否能不用原文复述，而独立解释：

- 什么是 context
- 为什么 context 会退化
- 为什么压缩和优化不是同义词
- 为什么工具设计是上下文设计
- 为什么多 agent 的核心价值是隔离 context

## 二、架构测试

面对一个新 agent 项目，你是否能给出：

- context budget
- tool strategy
- filesystem strategy
- memory strategy
- evaluation strategy
- single-agent / multi-agent / hosted-agent 的选择理由

## 三、案例测试

你是否能把四个主案例分别映射到主技能，不混淆主次：

- `digital-brain-skill`
- `x-to-book-system`
- `book-sft-pipeline`
- `llm-as-judge-skills`

## 四、写作测试

任选一章，你的草稿是否满足：

- 有问题定义
- 有自己的定义
- 有机制解释
- 有案例证据
- 有反模式
- 有工程取舍

## 五、最终成书验收

至少达到以下状态：

- 13 章都有章节草稿
- 每章都有 1 个核心论点
- 每章都有本地仓库证据
- 全书有统一术语
- 全书没有把 Context Engineering 写成 prompt tip 集合

