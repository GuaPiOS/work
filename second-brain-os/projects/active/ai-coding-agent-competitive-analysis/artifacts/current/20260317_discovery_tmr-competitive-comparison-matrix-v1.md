# TMR 全无人套件竞品比较矩阵 v1

## Artifact Meta

- `artifact_id`: `art_002`
- `stage`: `discovery`
- `status`: `active`
- `updated_at`: `2026-03-17T13:50:12+08:00`
- `based_on`:
  - `context/research/20260317_official-competitor-source-pack-v1.md`
  - `context/research/20260317_internal-inputs-summary-v1.md`
  - `artifacts/current/20260317_framing_tmr-unmanned-suite-competitive-analysis_research-frame-v1.md`

## Matrix v1

| Competitor | Archetype | Officially Confirmed Scope | Navigation / Motion Pattern | Digital Layer | Relevance to FS200 |
|---|---|---|---|---|---|
| `KUHN AURA` | 无人自走式 TMR 整机 | 装载、称重、混料、分料、推料、报告 | `GPS + RTK` 驱动的自主整机 | 有作业与报告能力 | 最接近“自主 TMR 车辆”路线，但不是 retrofit 套件 |
| `Lely Vector` | 完整自动饲喂系统 | 饲料厨房 + 混料 / 饲喂机器人 + 料槽监测 | 系统内机器人导航 | 完整系统级管理 | 定义完整自动饲喂价值上限，和导航套件不在同一层 |
| `GEA DairyFeed F4500` | 自动饲喂机器人 | 自动饲喂、推料、建图、定时循环 | 激光扫描建图 + 自主机器人 | 与牧场管理系统联动 | 强 robot benchmark，适合看导航 + 饲喂闭环 |
| `Trioliet Triomatic` | 自动饲喂系统 | `24/7` 投喂、小批次精确混料、低人工 | 系统化自动路线 | 自动饲喂系统级 | 体现成熟 ASF 路线，适合作为系统终局参考 |
| `Wasserbauer Shuttle Eco` | 自动喂料机器人 | 电池驱动、全天候喂料、多圈舍运行 | 更偏专用路径 / 机器人范式 | 机器人控制逻辑 | 与 `ATX/FS200` 的通用导航底座路线形成对照 |
| `Pellon TMR Robot` | 轨道式 TMR 机器人 | 小批次混料、轨道投喂 | 定轨 / 室内固定基础设施 | 控制器为主 | 说明自动化也可走轨道式，不等于自由导航 |
| `Faresin` | TMR 主机 + 数字化 | 远程监控、配方 / 库存、自动执行、智能辅助 | 公开资料中未见自由导航定位 | 数字化能力强 | 是 `FS200` 的高相关参考组，尤其适合看软件和自动化协同 |
| `SILOKING` | 自走式 TMR + 数字化 | 配方、卸料程序、循环管理、数据同步、自走式主机数据化 | 公开资料中未见自由导航定位 | 数字化能力强 | 是 `FS200` 的高相关参考组，尤其适合看自走式主机数据化路线 |

## First-Pass Conclusions

1. `FS200` 不应该直接把自己定义成 `Lely Vector` 或 `GEA DairyFeed F4500` 这类完整自动饲喂系统的同构替代品。
   推断：从当前内部资料看，`FS200` 更像“以 `ATX` 为导航底座、面向 `TMR` 场景的全无人导航套件”。
2. 当前最 relevant 的对标逻辑不是单点找一个完全同类，而是三线并看：
   - 看 `KUHN AURA` 的自主整机能力上限
   - 看 `Faresin` / `SILOKING` 的 TMR 主机数字化能力
   - 看 `Lely` / `GEA` / `Trioliet` / `Wasserbauer` / `Pellon` 的完整自动饲喂价值上限
3. `FS200` 的战略位置更像“存量 TMR 设备无人化改造层”。
   推断：如果这个定位成立，后续比较矩阵必须把 `retrofit 难度`、`适配车型范围`、`导航在牛舍 / 半室外场景的稳定性`、`与现有数字化产品协同` 放到前排维度。

## What Still Needs Evidence

- 8 个竞品的价格、渠道和真实落地案例
- `FS200` 的目标客户、优先牧场规模和区域
- `FS200` 的 MVP 边界：只做导航套件，还是覆盖更多自动饲喂闭环能力
- `ATX` 英文 brochure 的完整可读版本
