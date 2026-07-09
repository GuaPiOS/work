# 最终设计审查清单

## 一、Context 基础

- 当前任务的 context 由哪些部分组成？
- 哪些内容必须静态预载，哪些应该按需发现？
- 有没有显式 context budget？
- 关键约束是否放在 attention-favored positions？

## 二、退化与优化

- 系统在什么条件下会出现 lost-in-the-middle、poisoning、distraction、confusion、clash？
- 是否有 compaction 或 compression trigger？
- 大体量工具输出是否被 masking 或 offloading？
- 是否存在应该 partition 却仍强行塞进单上下文的任务？

## 三、工具、文件与记忆

- 工具边界是否清晰？是否存在重叠和歧义？
- 大量中间结果是否已迁移到 filesystem context？
- 计划、日志、子代理结果是否有稳定外置承载？
- memory system 是否与查询需求匹配？
- 是否处理了 temporal validity 与 retrieval correctness？

## 四、系统架构

- 单 agent 是否已经足够？
- 若使用 multi-agent，核心收益是否真来自 context isolation？
- 是否存在 telephone game 风险？
- 是否需要 hosted runtime 才能支撑并发、快照和连续性？

## 五、项目方法论

- 这个任务是否先通过了 task-model fit？
- 是否做过 manual prototype？
- 是否拆成了可缓存、可调试、可重跑的阶段？
- 是否清楚哪些阶段最贵、最不稳定？

## 六、评估

- 是否定义了多维 rubric？
- 是否覆盖 simple / medium / complex / very complex 样本？
- 是否区分 evaluation framework 与 judge pipeline？
- judge 是否处理了 direct vs pairwise 选择、bias mitigation 和 confidence calibration？
- 是否有人工复核触发条件？

## 七、解释性与未来升级

- 当前系统是否需要更强 explainability？
- belief / desire / intention 的区分是否能帮助当前系统更稳定地表达状态？
- 当前设计是否给未来模型升级留有空间，还是被过度脚手架锁死？
