# TMR 无人化可行性与市场规模分析 v1

## 一句话结论

TMR 无人化值得立项，但应按“封闭场景、分阶段无人化、先 后装改造 后整机”的逻辑推进。

更具体地说：

1. 先做自走式 TMR 后装改造，优先实现“已装料后无人行驶、无人投喂、自动回库/补能”。
2. 再做拖拉机 + 拖拽式 TMR 后装改造，但只选有限车型族，不做任意品牌任意拖车的通用版。
3. 最后做无人取料/装料，因为真正最难的不是导航，而是青贮面和料堆这种非结构化工况。

## 本文目的是回答：

1. 现有自走式 TMR 或拖拉机 + 拖拽式 TMR 无人化，技术上是否可行。
2. 当前市场是否已经验证“自动饲喂”需求，以及空白点在哪里。
3. 全无人套件如果定位成“存量 TMR 设备无人化升级层”，全球市场盘子大致有多大。
4. 应该优先打什么场景、什么区域、什么客户。

## 一、市场已经验证需求，但主流方案不是后装改造

### 1. 自动饲喂本身已经不是概念验证阶段

- Lely Vector作为完整自动饲喂系统，到 2021-03-08已交付第 1000 套，覆盖31个国家的奶牛和肉牛场。
- DeLaval Optimat 在2023-03-27 官方披露已装机 600+牧场，主要在欧洲，并推出了 OptiWagon自动送料机器人。
- GEA DairyFeed F4500官方明确为完全自主饲喂机器人，可通过激光扫描建图与自主导航，在 24/7 工况下完成称重、混料、投喂和推料，适配 300 头以内牛群、每小时约 2.2 m3 新鲜 TMR。
- Trioliet Triomatic、Pellon、Wasserbauer 等也说明欧洲市场已接受“高频新鲜投喂 + 降人工 + 系统闭环”的价值主张。

结论不是“有没有需求”，而是“客户已经接受自动饲喂，但现有主流供给多为完整系统，不是对存量 TMR 资产做无人化改造”。

### 2. 真正的产品空白在后装改造

从已调研竞品看，现有方案大体分三类：

1. 完整自动饲喂系统
   代表是 Lely Vector、DeLaval Optimat、Trioliet Triomatic。
   特点是整套工作流自动化，通常伴随饲料厨房、固定基础设施或专用机器人。
2. 自主饲喂机器人
   代表是 GEA DairyFeed F4500、Wasserbauer Shuttle Eco。
   特点是小型机器人、低速高频、多以专用机体为主。
3. 自主整机
   代表是 KUHN AURA。
   特点是从取料、称重、混料到投喂的完整自主整机，证明“全自主 TMR 车辆”技术上是可实现的。

这三类方案共同说明，市场已经接受自动化价值；但它们也共同暴露出一个空白：

对既有自走式 TMR 或拖拉机 + 拖拽式 TMR 做少改造、低土建、可复制的无人化升级层，公开市场上仍然稀缺。

这正是全无人套件的最佳切入点（暂时定义为 FS200）。

## 二、技术上可行性

### 1. 外部样本已经证明“自主 TMR 车辆”可跑通

KUHN AURA 是最直接的证明。

- KUHN 官方披露，AURA 能够自主完成 取料、称重、混料、分料、推料、报告。
- 导航上采用 RTK GPS + motion sensors + LiDAR 的室外/室内混合方案。
- 安全上采用 radar + laser + ultrasounds + sensitive edges。
- 官方案例里，AURA 在真实牧场上实现：
  - 日投喂频次 6 次
  - 日运行约 10 小时
  - 单周期约 46 分钟
  - 年均称重漂移 1.39%
  - 与之前的拖拽式方案相比，日饲喂作业时间从 1.5 小时降到约 0.5 小时准备工作

这说明“全链路自主”不是不可达，但它目前更多以整机方式出现，尚未形成成熟的开放 后装改造 平台。

### 2. 你们已有三块最关键的底座

根据内部资料，当前最可复用的不是一套完整 TMR 无人系统，而是三块能力的组合：

1. FeedLogger
   已覆盖配方设置、任务分配、进度追踪、异常告警、报表与追溯。
2. Nimbo X / TMR 优化套件
   已具备牛舍场景运行和推料协同能力。
3. ATX
   已具备多传感器融合、电子围栏、障碍物检测、急停、远程控制、路径规划、ISOBUS/implement sync 等能力。

这意味着你们不是从 0 到 1 做“自动饲喂”，而是从 0.6 到 1 做“重载 TMR 场景的无人化产品化”。

### 3. 真正新增的难点集中在 TMR 场景特有环节

需要新增或强化的能力，主要不是基础导航，而是以下四类：

1. 重载车辆 线控驱动
   包括转向、制动、档位/行走、液压执行机构与安全冗余。
2. TMR 工艺执行控制
   包括称重系统、卸料程序、绞龙/输送/铣刀头控制、不同配方组的定量投喂一致性。
3. 人牛混行的功能安全
   包括低速防撞、盲区感知、限速区、远程接管、双回路急停、共享空间规则。
4. 多 OEM 适配
   包括车型年份差异、CAN/ISOBUS/液压接口差异、售后与责任边界。

因此，这个项目的关键不在“导航能不能做”，而在“导航能否稳定嵌入 TMR 工艺、车辆控制与安全交付”。

## 三、两条路线怎么选

### 路线 A：现有自走式 TMR 无人化

这是优先路线。

优点：

- 单车一体，控制边界清晰。
- 目标客户通常是大牧场，自动化预算与 ROI 更容易成立。
- 不涉及拖车 articulation、PTO 同步和倒车稳定性等额外复杂度。
- 更适合作为 FS200 的首版 MVP，验证“重载车辆 + 牛舍场景 + TMR 工艺”的闭环。

难点：

- 各品牌自走式 TMR 的液压、控制逻辑差异依然存在。
- 如果首版就做“无人取料”，难度会显著上升。

建议 MVP 边界：

- 人工/半自动装料
- 无人行驶
- 无人投喂
- 自动回库
- 地理围栏 + 远程接管 + 安全限速

### 路线 B：拖拉机 + 拖拽式 TMR 无人化

这是第二路线，不建议作为首发。

优点：

- 存量设备基数更大。
- 如果主流动力换挡拖拉机型号较集中，平台化适配有机会成立。
- 对很多没有自走式 TMR 的客户，进入门槛更低。

难点：

- 牵引 articulation 与倒车是核心难点。
- 需要处理拖拉机与拖车之间的 PTO / 液压 / ISOBUS / braking 协同。
- 品牌、年份、地区差异会迅速拉高售后复杂度。
- 同样的无人化故障，在牵引系统里通常更难定位、更难解释责任。

建议打法：

- 只做 1-2 个拖拉机家族 + 1-2 个拖车平台。
- 优先做“已装料后无人投喂”，不把无人取料和复杂倒车一并纳入首版。

### 路线 C：无人取料/装料

这是第三路线，应作为后续 moat，而不是首发功能。

原因很简单：

- 青贮面、草捆、散料堆属于非结构化环境。
- 这里不仅要定位，还要做对象识别、几何估计、力控与安全处理。
- 真正高事故风险的环节往往也集中在取料区。

结论：

先做无人投喂，再做无人取料。

## 四、目标客户与优先场景

### 最优客户画像

1. ≥ 800 头奶牛，或多组别、多圈舍的规模化牧场
2. 每天 2 次以上投喂，且夜间/错峰投喂有明确价值
3. 使用 TMR 的舍饲或半舍饲模式，而不是完全草地放牧
4. 已有较标准化的投喂路线，愿意接受电子围栏与限速区
5. 对数据化管理已不陌生，或已安装 FeedLogger / Nimbo / 其他数字化系统

### 不建议优先打的客户

1. 小型牧场
2. 严重依赖放牧、TMR 占比低的区域
3. 设备品牌过杂、场地变化频繁、缺乏安全管理意识的客户

## 五、市场规模怎么估

## 1. 先看场址池，而不是先看报告总盘子

如果把 FS200 定义为“存量 TMR 设备无人化升级层”，比起直接套用“自动饲喂系统市场规模”，更合理的做法是先看目标场址池。

结合公开统计与行业结构，可以得到三个稳定结论：

1. 美国
   USDA NASS 2022 Census of Agriculture 显示，截至 2022 年底，美国拥有 ≥1,000 头奶牛的牧场共有 2,013 个，其中 1,000–2,499 头牧场 1,179 个、2,500 头及以上牧场 834 个；这类大规模牧场合计占全国奶牛存栏约 65%。
2. 欧洲
   自动化接受度高，是自动饲喂最成熟区域之一。Lely、DeLaval、GEA、Trioliet 等主力玩家均在这里形成安装基础。
3. 中国
   中国奶牛养殖规模化水平已较高。按《中国奶业质量报告（2024）》口径，2023 年全国“存栏百头以上规模养殖比例”达到 76%；同时，99%以上规模牧场已配备全混合日粮搅拌车（TMR 车）。

基于奶牛场的全球可部署场址做如下估算：

| 区域 | 可部署场址估算 |
|---|---:|
| 西北欧及欧洲核心奶区 | 30k - 45k |
| 北美 | 8k - 12k |
| 中国 | 2k - 5k |
| 大洋洲、中东及部分拉美 | 5k - 10k |
| 合计 | 45k - 70k |

说明：

- 这是“适合部署 TMR 无人化方案的场址池”，不是“所有奶牛场数量”。
- 它已经扣除了大量小场、放牧型、低自动化支付能力客户。

## 2. 再把场址池收敛成 FS200 可变现总市场规模

如果把上述场址池进一步扣除以下限制：

- 并非所有站点都有适配的存量设备
- 并非所有路线都适合地图化和无人化
- 并非所有区域都有经销与交付能力
- 并非所有客户都愿意先买 后装改造 而不是完整系统

则更现实的 FS200 理论总市场规模应收敛为：

- 20k - 50k 套
- 按内部假设 US$20k / 套 的渠道价，对应约 US$0.4B - 1.0B

这与内部材料里的判断是一致的：

- 理论总市场规模: US$0.4B - 1.0B
- 现实可服务市场规模: US$0.2B - 0.5B
- 3-5 年 实际服务规模: 1,000 - 3,000 套

这个口径的好处在于，它把“场景适配、交付能力、客户接受度”都考虑进去了，而不是直接拿大而化之的自动饲喂总市场去倒推。

## 3. 为什么这个盘子是够大的

从 FS200 的角度看，真正有价值的不是一个 US$20k 盒子，而是：

1. 硬件入口
   把已有 TMR 设备变成无人化设备。
2. 软件放大
   与 FeedLogger、任务调度、电子围栏、作业报表、异常告警结合。
3. 服务放大
   建图、适配、实施、培训、维保、升级。
4. 交叉销售
   与 Nimbo、推料联动、精准饲喂优化形成整套平台收入。

因此，FS200 的战略价值是“平台入口”，不是“单一改装件”。

## 六、区域优先级

### 第一优先：西北欧

理由：

- 自动饲喂接受度最高。
- 竞品教育已经完成。
- 人工成本高，自动化 ROI 更容易成立。
- Lely、DeLaval、GEA、Trioliet 等已验证客户教育成本可控。

### 第二优先：中国头部集团

理由：

- 规模化率高、TMR 渗透高、数字化基础好。
- 头部集团适合多场复制和集中采购。
- 你们本地交付与产品协同优势更强。

注意：

- 2024-09-26 农业农村部等七部门发文稳定肉牛奶牛生产，反映行业处于经营压力期。
- 因此中国市场首批项目更需要证明 1-2 个岗位节省、夜班替代、投喂一致性提升和饲料浪费下降，而不是仅讲“技术先进”。

### 第三优先：北美大型奶场

理由：

- 大牧场密度高。
- 规模化程度高。
- 舍饲、批量投喂、多栏舍场景明确。

难点：

- 场地跨度更大，工况更开放。
- 需要更强的渠道与本地服务能力。

## 七、产品路线建议

### Phase 1

Autonomous Feed-Out Kit for Self-Propelled TMR

范围：

- 已装料后无人投喂
- 室内外混合导航
- 低速防撞
- 远程接管
- 作业数据闭环

成功标准：

- 任务完成率 > 99%
- 投喂误差 <= 2%
- 至少替代 1 个日常投喂岗位，或显著减少夜班与周末人工

### Phase 2

Limited-Family Autonomous Tractor Feeding Kit

范围：

- 针对有限拖拉机/拖车平台
- 只做平台化可控的机型
- 保持 “已装料后无人投喂” 为主

### Phase 3

Autonomous Loading + Full Closed Loop

范围：

- 无人取料/装料
- 全链路饲喂闭环
- 多车协同与更高层级调度

## 八、最重要的风险提醒

1. 不要把 v1 做成“任意品牌、任意车型、任意场景通用”
   这会把适配和售后复杂度拉爆。
2. 不要一上来就承诺无人取料
   这是技术和安全风险最高的环节。
3. 不要把自己定义成 Lely/GEA 的同构替代
   你们更像“存量设备无人化升级层”，价值主张应该是 少改造、低 CAPEX、快部署、与现有数字化协同。
4. 安全要按工业产品标准做，而不是演示级原型
   KUHN 已在 AURA 上明确强调安全传感器和标准化要求，说明这个赛道的商业化前提就是功能安全。

## 九、最终判断

概括：

TMR 无人化这件事，市场需求已被验证，技术路径已被证明，但存量设备 后装改造 仍存在明显空白。

因此，FS200 有机会成为一个平台型入口产品。最优打法不是去复制完整自动饲喂系统，而是利用你们已具备的 FeedLogger + Nimbo + ATX 三块底座，先把 自走式 TMR 做成可商业化的无人投喂套件，再逐步扩展到 拖拉机 + 拖拽式 TMR 和 无人取料。

## Sources

- Lely Vector official page: https://www.lely.com/solutions/feeding/vector/
- Lely 1000th Vector official news: https://www.lely.com/ie/about-lely/news/1000th-vector/
- Lely Vector MFR Next official news: https://www.lely.com/about-lely/news/lely-introduces-the-vector-mfr-next/
- DeLaval Optimat official page: https://www.delaval.com/en-gb/farm-solutions/feeding/delaval-optimat/
- DeLaval OptiWagon launch: https://corporate.delaval.com/2023/03/delaval-launches-a-new-autonomous-feeding-robot/
- GEA DairyFeed F4500 official page: https://www.gea.com/en/products/milking-farming-barn/dairyfeed-feeding-systems/feeding-robot-dairyfeed-f4500/
- GEA F4500 launch release: https://www.gea.com/en/news/trade-press/2022/gea-introduces-feeding-robot-f4500/
- Trioliet battery feeding robot page: https://www.trioliet.com/news/news/new-triomatic-feeding-robot-on-battery-1
- KUHN AURA official news: https://www.kuhn.com/en/news/self-propelled-autonomous-aura-mixer-revealed
- KUHN history / AURA introduction: https://www.kuhn.com/en/about-kuhn/about-us/kuhn-group-history/history-2020-today
- USDA ERS large dairy structure: https://www.ers.usda.gov/index.php/amber-waves/2014/december/milk-production-continues-shifting-to-large-scale-farms
- Agriculture and Horticulture Development Board dairy structure summary: https://ahdb.org.uk/news/eu-dairy-farms-growing-in-size-and-specialisation
- DairyNZ facts and figures hub: https://www.dairynz.co.nz/resources/resource-list/facts-and-figures/
- Dairy Australia annual reports: https://www.dairyaustralia.com.au/about-us/annual-reports
- 农业农村部：促进奶业实现全面振兴: https://www.moa.gov.cn/ztzl/ymksn/jjrbbd/202408/t20240802_6460145.htm
- 农业农村部等七部门：稳定肉牛奶牛生产: https://www.moa.gov.cn/xw/zwdt/202409/t20240926_6463476.htm
- FJD ATX product page: https://agriculture.fjdynamics.com/product/fjd-atx-steer-system
- Sveaverken animal farming page: https://www.sveaverken.com/animal-farming
- https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1%2C_Chapter_1_US/st99_1_017_019.pdf
- https://hslcs.org.cn/index.php/info/19191.html?utm_source=chatgpt.com
