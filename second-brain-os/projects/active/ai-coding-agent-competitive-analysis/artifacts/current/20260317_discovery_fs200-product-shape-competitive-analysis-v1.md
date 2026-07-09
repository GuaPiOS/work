# FS200 产品形态竞品分析 v1

## Artifact Meta

- `artifact_id`: `art_003`
- `stage`: `discovery`
- `status`: `active`
- `updated_at`: `2026-03-17T14:23:23+08:00`
- `based_on`:
  - `context/research/20260317_fs200-product-shape-source-pack-v1.md`
  - `context/research/20260317_official-competitor-source-pack-v1.md`
  - `context/research/20260317_internal-inputs-summary-v1.md`
  - `artifacts/current/20260317_discovery_tmr-competitive-comparison-matrix-v1.md`

## Product Boundary

- `FS200` 当前产品定义：面向传统 `TMR` 设备用户的全无人导航套件 / 改造层
- 目标客户：存量 `TMR` 设备用户，希望在现有设备上做无人化升级
- 分析约束：主矩阵只纳入与 `FS200` 同产品形态的 autonomy kit / autonomy upgrade / retrofit layer
- 非主矩阵对象：完整自动饲喂系统、专用喂料机器人、无人自走式 `TMR` 整机、仅数字化 `TMR` 主机

## Three-Layer Market Structure

### Direct Competitors

- `Bluewhite Pathfinder GEN 4`
- `Sabanto Autonomy System`
- `John Deere Autonomy Precision Upgrade`
- `PTx Trimble OutRun`

### Adjacent Benchmarks

- `KUHN AURA`
- `Lely Vector`
- `GEA DairyFeed F4500`
- `Trioliet Triomatic`
- `Wasserbauer Shuttle Eco`
- `Pellon TMR Robot`

### Reference Products

- `Faresin`
- `SILOKING`

## Direct Competitor Matrix

| Product | Official Product Form | Officially Confirmed Scope | Why It Is Direct To FS200 | Main Scene Gap |
|---|---|---|---|---|
| `Bluewhite Pathfinder GEN 4` | 现有农业设备 autonomy platform / retrofit layer | 把现有车队升级为 autonomous operations，面向永久作物 / 果园场景 | 和 `FS200` 一样，卖点是把已有设备升级成无人作业设备，而不是重卖整机 | 当前公开场景偏果园，不是 `TMR` / 牛舍半室内作业 |
| `Sabanto Autonomy System` | 现有拖拉机 autonomy kit | 多品牌兼容，自主作业，摄像头、障碍物检测、`GNSS` 与远程监督 | 同样是存量设备升级逻辑，适合对标 kit 边界、兼容性策略和渠道打法 | 当前公开案例偏大田拖拉机场景 |
| `John Deere Autonomy Precision Upgrade` | `OEM` 式 autonomy upgrade | 对既有机型加装 autonomy upgrade，支持远程监督与作业计划导入 | 说明升级包路线可以成立，适合参考机型白名单、软件闭环和运维体验 | 更偏封闭 `OEM` 体系和大田工况 |
| `PTx Trimble OutRun` | self-contained retrofit kit | 先从 grain cart / tillage 等特定工况切入，强调远程监督和安全冗余 | 说明 `retrofit kit + 特定任务切入` 是可成立的上市路径 | 公开任务场景仍偏大田，不是饲喂院区与 `TMR` 设备 |

## Adjacent Benchmarks

| Product | What It Defines | Why It Is Not Direct |
|---|---|---|
| `KUHN AURA` | 自主 `TMR` 整机能力上限 | 它卖的是整机，不是改造层 |
| `Lely Vector` | 完整自动饲喂系统价值上限 | 它卖的是系统闭环，不是导航套件 |
| `GEA DairyFeed F4500` | 自动机器人 + 导航 + 饲喂闭环 | 它是专用机器人，不是 retrofit kit |
| `Trioliet Triomatic` | 成熟 `24/7` 自动饲喂系统 | 它是系统级自动化，而不是升级包 |
| `Wasserbauer Shuttle Eco` | 专用喂料机器人路线 | 它是专用 robot 范式，不是通用导航层 |
| `Pellon TMR Robot` | 定轨式 `TMR` 自动化路线 | 它依赖固定基础设施，不是自由导航套件 |

## Reference Products

| Product | Reference Value To FS200 | Why It Stays In Reference Layer |
|---|---|---|
| `Faresin` | 参考 `TMR` 主机数字化、远程监控、配方 / 库存和自动执行协同 | 不等于无人导航套件 |
| `SILOKING` | 参考自走式 `TMR` 主机与作业程序、循环管理和数据同步 | 不等于无人导航套件 |

## What This Reclassification Changes

1. 前一版 `art_002` 不是废弃，而是降级为“解决方案空间背景矩阵”。
2. 当前真正回答 `FS200` 产品形态问题的，是 direct competitor 这一层。
3. 推断：`FS200` 的第一批 direct competitors 更可能来自农业 autonomy retrofit 赛道，而不是现有自动饲喂品牌本身。
4. `KUHN AURA`、`Lely Vector`、`GEA` 等仍然要看，但它们回答的是“客户最终完整方案长什么样”，不是“`FS200` 套件长什么样”。

## First-Pass Conclusions

1. 在当前官方资料样本里，尚未发现一个公开命名且明确聚焦 `TMR` 存量设备 retrofit 的 exact twin。
   推断：`FS200` 的直接竞争不是“奶牛场里谁也卖 `FS200`”，而是“谁也在卖把现有设备升级为 autonomous machine 的 kit / upgrade”。
2. `FS200` 的 direct layer 需要优先对标四件事：
   - kit 边界
   - 兼容车型范围
   - 远程监督与安全冗余
   - 渠道 / 服务 / 运维模式
3. `FS200` 的 adjacent layer 需要对标三件事：
   - 客户为什么愿意为自动饲喂付费
   - 完整系统在效率、人工和新鲜投喂上的价值上限
   - 如果只卖导航套件，哪些系统价值仍需要合作方或宿主设备补齐
4. `FS200` 的 reference layer 需要对标三件事：
   - 配方与任务调度接口
   - 作业记录与报表闭环
   - 与 `TMR` 主机控制和数字化模块的协同方式

## Implications For FS200

推断：如果当前产品定位不变，`FS200` 更像以下组合，而不是单一完整自动饲喂系统：

- 一个 `ATX` 衍生出来的 autonomy / navigation layer
- 一个面向传统 `TMR` 设备的 retrofit kit
- 一个需要和 `FeedLogger / Nimbo X` 或未来 `TMR` 数字化层协同的执行模块

因此，后续可行性报告应优先验证：

- `TMR` 宿主设备的改造接口边界
- 牛舍 / 饲喂通道 / 半室外场景下的导航与安全稳定性
- 是否需要自建更完整的软件调度与作业闭环
- 商业化更适合卖套件、卖升级包，还是卖改造交付项目

## Evidence Gaps

- 4 个 direct competitors 的价格、交付模式、服务方式和真实落地案例
- 是否存在尚未纳入的 `dairy / feeding` 场景 autonomy retrofit 样本
- `FS200` 首版兼容哪些 `TMR` 设备类型
- `FS200` 的价格带、回本周期和商业模式约束
