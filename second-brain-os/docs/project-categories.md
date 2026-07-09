# Project Categories

项目不按行业分类，而按执行模式分类。

## `category`

| 分类 | 适用场景 | 主结果 |
|---|---|---|
| `delivery` | 有明确交付物和截止时间 | 报告、提案、汇报、方案 |
| `build` | 构建或改造系统、产品、流程 | 工具、原型、流程、系统 |
| `research` | 回答问题、形成判断 | 结论、评估、比较、调研 |
| `operations` | 周期性、重复性管理工作 | 机制、例行盘点、运营面板 |
| `writing` | 主结果是结构化文本内容 | Outline、Draft、Final copy |
| `learning` | 学习和能力沉淀 | 笔记、练习、方法总结 |

## `domain`

固定枚举：

- `work`
- `startup`
- `personal`
- `learning`
- `other`

## `automation_profile`

| 枚举 | 含义 |
|---|---|
| `manual` | 纯文档驱动 |
| `assisted` | 文档 + 通用脚本 |
| `delegated` | 允许更强委派或并行子代理 |

## 分类优先规则

如果一个项目看起来跨多个类别，按主结果判断。

例子：

- 目标是写结论报告：`research`
- 目标是做一个工作原型：`build`
- 目标是提交老板要的文档：`delivery`
- 目标是产出长文、文案或稿件：`writing`
