# Compact State

> 机器优先的当前压缩状态。每轮实质进展后重写，不追加。

## Mission

- 项目：TMR 全无人套件竞品分析
- 当前阶段：discovery
- 当前目标：围绕 `FS200` 产品形态建立三层竞品结构，并把 direct competitors 和更广的 solution benchmarks 分开

## Active Facts

- 当前线程已绑定为仅服务 `ai-coding-agent-competitive-analysis` 项目
- 老板希望基于当前产品方案改造 `TMR 全无人套件`
- 服务对象为用户本人、产品团队和老板
- 时间范围以最近 `1` 年产品演进为主
- 用户已给出第一版核心竞品名单，共 `8` 个品牌 / 方案
- 当前 canonical artifact 为 `artifacts/current/20260317_discovery_fs200-product-shape-competitive-analysis-v1.md`
- 已读取首批内部输入，确认现有能力线索来自 `FeedLogger`、`Nimbo X`、`FS200` 和 `ATX` 无人套件
- 用户已明确：`ATX` 是农业场景下的果园全无人导航套件；`FS200` 是老板新定义在 TMR 上用的全无人导航套件；`FeedLogger/Nimbo X` 是畜牧场景现有产品；最终目标是依托 TMR 使用场景做出 `FS200`
- `ATX` 产品定义表显示已有多传感器融合、远程控制、安全冗余、ISOBUS 兼容和模块化硬件能力
- `TMR产品介绍.md` 显示已有 TMR 数字化管理与推料联动基础，但尚未证明已具备完整无人饲喂闭环
- `FS200系统部署潜力.md` 提供了“存量设备无人化升级层”的商业化假设和价格 / TAM 口径
- 已基于官方资料形成 `context/research/20260317_official-competitor-source-pack-v1.md`
- 已将 `FS200` 的竞品结构重构为三层：同产品形态 direct competitors、完整系统 adjacent benchmarks、`TMR` 主机 / 数字化 reference products
- 第一轮外部资料显示，`FS200` 的 direct competitor 目前主要来自跨场景农业 autonomy retrofit / upgrade 样本，而不是现有自动饲喂品牌本身
- 旧的 `art_002` broad matrix 仍保留，但已降级为 solution-space 背景，不再作为主产物
- 用户已明确目标客户是传统 `TMR` 设备用户，重点是存量改造

## Active Decisions

- 首个正式产物先做 research frame，而不是直接写最终可行性结论
- 外部原始资料和长输出统一进入 `context/tool_outputs/` 或 `context/research/`
- 第一版研究对象聚焦 `TMR 全无人套件` 相关竞品，并区分整机、系统和改造参考组
- 首批内部输入先沉淀为 `context/research/20260317_internal-inputs-summary-v1.md`，避免反复读取原始输入
- 当前产品逻辑按 `ATX 能力底座 -> FS200 TMR 导航套件 -> 与畜牧产品结合` 理解，后续比较应围绕导航套件而不是完整自动饲喂系统来判断改造路径
- 第一轮外部分析采用官方资料优先，不把渠道宣传或二手测评当作主要依据
- 当前主分析口径固定为三层：`direct competitors` 只看与 `FS200` 同产品形态的 autonomy kit / retrofit layer；完整自动饲喂系统和整机方案降级为 `adjacent benchmarks`；`Faresin` / `SILOKING` 留在 `reference products`

## Current Artifact

- `art_003` -> `artifacts/current/20260317_discovery_fs200-product-shape-competitive-analysis-v1.md`

## Next 3 Actions

1. 补齐 4 个 direct competitors 的价格、渠道、服务模式和落地案例信息
2. 基于三层结构写第一版 `FS200` 差异点 / 缺口 / 风险分析
3. 明确 `FS200` 的价格带和 MVP 边界

## Blocking Questions

- `FS200` 的价格带和商业模式偏好是什么？
- `FS200` 的 MVP 边界是什么？
