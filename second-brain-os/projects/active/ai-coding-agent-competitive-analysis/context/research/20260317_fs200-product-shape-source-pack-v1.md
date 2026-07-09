# FS200 Product-Shape Source Pack v1

## Scope

本笔记按 `FS200` 的产品形态重构竞品资料，目标不是再做一版泛化的自动饲喂市场盘点，而是回答：

- `FS200` 这种“面向传统 `TMR` 设备用户的全无人导航套件 / 改造层”，直接对手是谁
- 哪些产品只能作为更高一层的系统 benchmark
- 哪些产品更适合当 `TMR` 主机与数字化能力参考

## Product Boundary

- `FS200` 当前定义：面向传统 `TMR` 设备用户的全无人导航套件 / 改造层
- 目标不是完整自动饲喂系统，也不是重新定义一台全新无人自走式 `TMR` 整机
- 目标客户优先看存量 `TMR` 设备用户，核心问题是“现有设备如何改造成可无人运行的 `TMR` 方案”

## Classification Rules

### Direct Competitors

满足以下条件才进入主矩阵：

- 公开资料里明确是 autonomy kit / autonomy upgrade / retrofit layer
- 面向现有农机或作业设备做无人化升级，而不是卖完整新系统
- 官方资料中能看到导航、自主作业、远程监督或安全冗余等能力

### Adjacent Benchmarks

满足以下条件：

- 解决的是相近客户价值问题，例如自动饲喂、无人作业、降人工
- 但产品形态高一层，属于完整自动饲喂系统、专用机器人或自主整机

### Reference Products

满足以下条件：

- 不属于同产品形态，也不是完整无人系统
- 但能给 `FS200` 提供 `TMR` 主机、数字化、作业协同和软件闭环参考

## Direct Competitor Candidates

### Bluewhite Pathfinder GEN 4

- 官方定位是面向现有农业设备的自主化平台，服务永久作物和果园场景
- 官方资料强调其可以把现有车队转成 autonomous operations，而不是要求客户重买整机
- 对 `FS200` 的意义：这是最接近“aftermarket autonomy layer” 的同形态样本之一
- 不匹配点：当前公开场景偏果园 / 永久作物，而不是牛舍与 `TMR` 作业
- 官方来源：
  - [Bluewhite GEN 4](https://bluewhite.ai/gen4/)
  - [Bluewhite Technology](https://bluewhite.ai/technology/)

### Sabanto Autonomy System

- 官方资料强调其通过 autonomous kits 改造现有拖拉机，而不是出售整机
- 官方口径包含多品牌兼容、摄像头、障碍物检测、`GNSS` 与远程监督
- 对 `FS200` 的意义：它和 `FS200` 一样，核心价值是“把已有设备升级为无人设备”
- 不匹配点：主要公开案例仍偏大田拖拉机场景，不是 `TMR` 饲喂场景
- 官方来源：
  - [Sabanto](https://www.sabantoag.com/)

### John Deere Autonomy Precision Upgrade

- 官方资料显示其是对既有 `8R` / `9R` 系列设备的 autonomy upgrade 路线，而不是单独一台全新 autonomous vehicle
- 官方口径强调通过 `John Deere Operations Center` 导入作业计划、远程监督和异常监控
- 对 `FS200` 的意义：这是 `OEM upgrade path` 的强参考样本，适合看兼容性分层、升级包边界和运维体验
- 不匹配点：当前公开适配机型和工况仍偏大田作业，不是 `TMR` 存量设备改造
- 官方来源：
  - [John Deere Precision Upgrade Kits](https://www.deere.com/en/technology-products/precision-upgrades/precision-upgrade-kits/)
  - [John Deere Autonomy Precision Upgrade](https://www.deere.com/en/news/all-news/jd-autonomy-precision-upgrade/)

### PTx Trimble OutRun

- 官方资料显示其是 self-contained retrofit kit 路线，先切 grain cart 与 tillage 等特定工况
- 官方口径强调远程监督、车载传感器、急停与通过渠道销售的商业模式
- 对 `FS200` 的意义：它说明“先拿 retrofit kit 进场，再逐步扩任务边界”的路线是成立的
- 不匹配点：公开产品仍偏大田工况，不是奶牛场 / `TMR` 半室内作业
- 官方来源：
  - [OutRun](https://www.outrun.ag/)

## Adjacent Benchmarks

以下产品不进入 `FS200` 的 direct matrix，但必须保留作为系统上限 benchmark：

- `KUHN AURA`
  - 无人自走式 `TMR` 整机 benchmark
- `Lely Vector`
  - 完整自动饲喂系统 benchmark
- `GEA DairyFeed F4500`
  - 自动饲喂机器人 benchmark
- `Trioliet Triomatic`
  - 成熟 `ASF` 系统 benchmark
- `Wasserbauer Shuttle Eco`
  - 专用喂料机器人 benchmark
- `Pellon TMR Robot`
  - 定轨 / 固定基础设施路线 benchmark

这些产品的官方事实已在 `context/research/20260317_official-competitor-source-pack-v1.md` 中整理。

## Reference Products

以下产品更适合作为 `TMR` 主机和数字化能力参考，而不是 direct competitor：

- `Faresin`
  - 强数字化、远程监控、配方 / 库存和自动执行协同
- `SILOKING`
  - 自走式 `TMR` 主机与配方、卸料程序、循环管理和数据同步结合

这些产品的官方事实已在 `context/research/20260317_official-competitor-source-pack-v1.md` 中整理。

## Interpretation

1. 推断：在当前官方资料样本里，还没有看到一个公开命名、且明确聚焦 `TMR` 存量设备 retrofit 的 exact twin。
2. 因此，`FS200` 的 direct competitor 集合需要按“同产品形态”来找，而不是只在奶牛饲喂赛道里找品牌。
3. `KUHN AURA`、`Lely Vector`、`GEA` 等产品仍然重要，但它们回答的是“客户最终能买到什么完整结果”，不是“`FS200` 这种套件本身的 direct market shape 是什么”。
4. `Faresin`、`SILOKING` 更适合回答“`FS200` 未来要怎么和 `TMR` 主机、配方、作业管理与数字化系统协同”。
