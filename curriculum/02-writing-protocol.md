# 写作协议

## 每章统一模板

每一章都必须按下面 7 段写：

1. `问题`
说明本章解决什么工程问题。

2. `定义`
用你自己的话定义概念，不允许只翻译原文。

3. `机制`
解释为什么会发生，强调 attention、context budget、tool/output/state 等机制。

4. `技术模式`
把仓库里的做法抽象成可迁移方法，而不是“某项目刚好这么写”。

5. `案例证据`
至少绑定一个本地 example、docs 或 skill 段落。

6. `反模式`
写出常见误解，说明为什么错。

7. `写作练习`
写出 800-1500 字的正文草稿。

## 写作要求

- 先下定义，再举例子
- 先讲边界，再讲价值
- 先讲机制，再讲口号
- 每章至少出现一次“为什么不用别的方案”
- 每章至少出现一个本地仓库证据

## 术语写法

统一格式：

```text
术语：
一句话定义：
与相邻概念的边界：
在本地仓库中的证据：
```

## 章节中的边界比较

以下比较必须写清楚：

- `context-compression` vs `context-optimization`
- `filesystem-context` vs `memory-systems`
- `evaluation` vs `advanced-evaluation`
- `multi-agent-patterns` vs `hosted-agents`
- `project-development` vs “单纯做一个 prompt workflow”

## 证据引用规则

建议每次至少引用 2 类来源：

- 原则来源：`skills/*.md`
- 案例来源：`examples/*`

只有原则没有案例，会变空。
只有案例没有原则，会变成读后感。

## 写作中的禁止事项

- 不要把 Context Engineering 简化成 Prompt Engineering 升级版
- 不要把 Multi-Agent 写成组织学故事
- 不要把 Filesystem 写成“临时低配 memory”
- 不要把 Evaluation 写成“最后跑几个 benchmark”
- 不要把 BDI 章节写成无工程落点的纯哲学

