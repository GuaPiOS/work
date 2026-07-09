const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "FJD / Sveaverken";
pptx.subject = "TMR 无人化市场调研与立项建议";
pptx.title = "TMR 无人化市场调研与立项建议";
pptx.lang = "zh-CN";

const W = 13.333;
const H = 7.5;
const TOTAL_SLIDES = 11;

const C = {
  bg: "F6F8FB",
  panel: "FFFFFF",
  ink: "0F172A",
  sub: "475569",
  muted: "64748B",
  line: "D8E1EC",
  soft: "EAF2FB",
  accent: "0EA5E9",
  accent2: "14B8A6",
  accent3: "2563EB",
  accentSoft: "E0F2FE",
  warnSoft: "FFF1F2",
  warn: "E11D48",
  successSoft: "ECFDF5",
  success: "059669",
  dark: "0B1220",
};

const FONT = "Aptos";

function applyBase(slide, section, page) {
  slide.background = { color: C.bg };
  slide.addText(section, {
    x: 0.8,
    y: 0.42,
    w: 2.5,
    h: 0.2,
    fontFace: FONT,
    fontSize: 10,
    bold: true,
    color: C.accent,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.8,
    y: 7.03,
    w: 11.7,
    h: 0,
    line: { color: C.line, pt: 1 },
  });
  slide.addText("内部讨论稿 | 2026-03", {
    x: 0.8,
    y: 7.07,
    w: 2.2,
    h: 0.14,
    fontFace: FONT,
    fontSize: 8,
    color: C.muted,
    margin: 0,
  });
  slide.addText(`${page}/${TOTAL_SLIDES}`, {
    x: 12.1,
    y: 7.07,
    w: 0.4,
    h: 0.14,
    fontFace: FONT,
    fontSize: 8,
    color: C.muted,
    align: "right",
    margin: 0,
  });
}

function addTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.8,
    y: 0.95,
    w: 8.8,
    h: 0.7,
    fontFace: FONT,
    fontSize: 23,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.8,
      y: 1.63,
      w: 9.2,
      h: 0.36,
      fontFace: FONT,
      fontSize: 10.5,
      color: C.sub,
      margin: 0,
    });
  }
}

function addPanel(slide, x, y, w, h, fill = C.panel, line = C.line, radius = "roundRect") {
  slide.addShape(pptx.ShapeType[radius], {
    x,
    y,
    w,
    h,
    fill: { color: fill },
    line: { color: line, pt: 1 },
  });
}

function addPill(slide, text, x, y, w, color = C.ink, fill = C.soft) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.3,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: fill, pt: 1 },
  });
  slide.addText(text, {
    x: x + 0.1,
    y: y + 0.06,
    w: w - 0.2,
    h: 0.16,
    fontFace: FONT,
    fontSize: 9,
    bold: true,
    color,
    align: "center",
    margin: 0,
  });
}

function addKpiCard(slide, x, y, w, h, label, value, note, accent = C.accent) {
  addPanel(slide, x, y, w, h);
  slide.addShape(pptx.ShapeType.rect, {
    x: x + 0.16,
    y: y + 0.16,
    w: 0.08,
    h: h - 0.32,
    fill: { color: accent },
    line: { color: accent, pt: 0 },
  });
  slide.addText(label, {
    x: x + 0.35,
    y: y + 0.18,
    w: w - 0.5,
    h: 0.18,
    fontFace: FONT,
    fontSize: 9,
    bold: true,
    color: C.muted,
    margin: 0,
  });
  slide.addText(value, {
    x: x + 0.35,
    y: y + 0.44,
    w: w - 0.5,
    h: 0.34,
    fontFace: FONT,
    fontSize: 18,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText(note, {
    x: x + 0.35,
    y: y + h - 0.4,
    w: w - 0.5,
    h: 0.2,
    fontFace: FONT,
    fontSize: 8.5,
    color: C.sub,
    margin: 0,
  });
}

function addBulletList(slide, items, x, y, w, opts = {}) {
  const {
    fontSize = 12,
    color = C.ink,
    gap = 0.34,
    bulletColor = C.accent,
  } = opts;

  items.forEach((item, idx) => {
    const yy = y + idx * gap;
    slide.addShape(pptx.ShapeType.ellipse, {
      x,
      y: yy + 0.06,
      w: 0.08,
      h: 0.08,
      fill: { color: bulletColor },
      line: { color: bulletColor, pt: 0 },
    });
    slide.addText(item, {
      x: x + 0.16,
      y: yy,
      w,
      h: 0.22,
      fontFace: FONT,
      fontSize,
      color,
      margin: 0,
    });
  });
}

function addSmallSource(slide, text) {
  slide.addText(text, {
    x: 0.82,
    y: 6.72,
    w: 11.2,
    h: 0.16,
    fontFace: FONT,
    fontSize: 7.5,
    color: C.muted,
    margin: 0,
  });
}

function addSectionCard(slide, x, y, w, h, title, body, accent = C.accent) {
  addPanel(slide, x, y, w, h);
  slide.addShape(pptx.ShapeType.line, {
    x: x + 0.18,
    y: y + 0.26,
    w: 0.5,
    h: 0,
    line: { color: accent, pt: 2.2 },
  });
  slide.addText(title, {
    x: x + 0.18,
    y: y + 0.4,
    w: w - 0.36,
    h: 0.26,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.18,
    y: y + 0.76,
    w: w - 0.36,
    h: h - 0.92,
    fontFace: FONT,
    fontSize: 9.5,
    color: C.sub,
    margin: 0,
    valign: "top",
  });
}

function addNumberTag(slide, x, y, n, fill = C.accent) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x,
    y,
    w: 0.28,
    h: 0.28,
    fill: { color: fill },
    line: { color: fill, pt: 0 },
  });
  slide.addText(String(n), {
    x,
    y: y + 0.04,
    w: 0.28,
    h: 0.14,
    fontFace: FONT,
    fontSize: 9,
    bold: true,
    color: "FFFFFF",
    align: "center",
    margin: 0,
  });
}

// Slide 1: Cover
{
  const slide = pptx.addSlide();
  applyBase(slide, "TMR UNMANNED | MARKET & FEASIBILITY", 1);

  slide.addShape(pptx.ShapeType.line, {
    x: 0.8,
    y: 1.18,
    w: 0.9,
    h: 0,
    line: { color: C.accent, pt: 2.5 },
  });
  slide.addText("TMR 无人化市场调研与立项建议", {
    x: 0.8,
    y: 1.38,
    w: 7.6,
    h: 0.7,
    fontFace: FONT,
    fontSize: 26,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText("面向“自走式 TMR / 拖拉机 + 拖拽式 TMR”存量设备的无人化升级层", {
    x: 0.8,
    y: 2.14,
    w: 7.8,
    h: 0.34,
    fontFace: FONT,
    fontSize: 11,
    color: C.sub,
    margin: 0,
  });
  slide.addText("建议结论：先做自走式 retrofit，先做无人投喂，再做无人取料", {
    x: 0.8,
    y: 2.55,
    w: 7.2,
    h: 0.25,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.accent3,
    margin: 0,
  });

  addPanel(slide, 8.55, 1.25, 3.95, 3.2, C.panel, C.line);
  slide.addText("科技极简风 · 战略判断框架", {
    x: 8.85,
    y: 1.55,
    w: 3.2,
    h: 0.24,
    fontFace: FONT,
    fontSize: 10,
    bold: true,
    color: C.muted,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 9.15,
    y: 2.0,
    w: 2.7,
    h: 1.9,
    line: { color: C.accentSoft, pt: 1.2, transparency: 10 },
    fill: { color: C.bg, transparency: 100 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 9.55,
    y: 2.95,
    w: 1.8,
    h: 0,
    line: { color: C.accent, pt: 2 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 10.45,
    y: 2.2,
    w: 0,
    h: 1.5,
    line: { color: C.accent2, pt: 2 },
  });
  slide.addText("Route", {
    x: 8.95,
    y: 2.38,
    w: 0.7,
    h: 0.18,
    fontFace: FONT,
    fontSize: 9,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText("Safety", {
    x: 10.72,
    y: 2.38,
    w: 0.8,
    h: 0.18,
    fontFace: FONT,
    fontSize: 9,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText("Feed OS", {
    x: 10.62,
    y: 3.18,
    w: 0.9,
    h: 0.18,
    fontFace: FONT,
    fontSize: 9,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText("核心不是“能不能自动跑”，而是能否稳定嵌入 TMR 工艺、车辆控制与场内安全。", {
    x: 8.85,
    y: 4.0,
    w: 3.1,
    h: 0.42,
    fontFace: FONT,
    fontSize: 9.5,
    color: C.sub,
    margin: 0,
  });

  addKpiCard(slide, 0.8, 5.15, 3.8, 1.18, "Market Proof", "Lely 1000 套 / DeLaval 600+ 场", "自动饲喂需求已被验证", C.accent);
  addKpiCard(slide, 4.77, 5.15, 3.8, 1.18, "Deployable Pool", "45k - 70k 场址", "dairy-first 全球可部署场址池", C.accent2);
  addKpiCard(slide, 8.74, 5.15, 3.8, 1.18, "TAM", "US$0.4B - 1.0B", "按 US$20k/套渠道价口径", C.accent3);
}

// Slide 2: Executive summary
{
  const slide = pptx.addSlide();
  applyBase(slide, "EXECUTIVE SUMMARY", 2);
  addTitle(slide, "管理层结论", "先判断是否该做，再判断先做什么、卖给谁、如何控制风险。");

  addSectionCard(slide, 0.8, 2.15, 2.9, 1.55, "值得立项", "自动饲喂价值已经被验证，但“存量 TMR 设备无人化升级层”仍存在公开市场空白。", C.accent);
  addSectionCard(slide, 3.95, 2.15, 2.9, 1.55, "路线优先级", "P1 自走式 TMR retrofit；P2 有限车型的拖拉机+拖拽式；P3 无人取料/装料。", C.accent2);
  addSectionCard(slide, 7.1, 2.15, 2.9, 1.55, "规模足够大", "TAM US$0.4B-1.0B；SAM US$0.2B-0.5B；3-5 年 SOM 1,000-3,000 套。", C.accent3);
  addSectionCard(slide, 10.25, 2.15, 2.28, 1.55, "区域顺序", "西北欧 > 中国头部集团 > 北美大型奶场。", C.accent);

  addPanel(slide, 0.8, 4.05, 11.73, 2.2, C.panel, C.line);
  addTextBlock(slide, "为什么现在做", [
    "市场端：Lely、DeLaval、GEA、Trioliet 已把自动饲喂教育完成，客户已接受“高频新鲜投喂 + 降人工 + 闭环管理”的价值。",
    "供给端：主流方案偏完整系统或专用机器人，对存量 TMR 资产的 brownfield retrofit 仍稀缺。",
    "能力端：FeedLogger、Nimbo、ATX 已构成数字化、牛舍运行与无人化感知/控制三块底座。",
    "进入策略：v1 聚焦“人工/半自动装料 + 无人投喂 + 自动回库”，不要一上来承诺全链路无人取料。",
  ], 1.1, 4.42, 11.0);
}

// Slide 3: Why now
{
  const slide = pptx.addSlide();
  applyBase(slide, "WHY NOW", 3);
  addTitle(slide, "为什么现在是 TMR 无人化的合适窗口", "需求成熟、客户集中、内部能力可复用。");

  addSectionCard(slide, 0.8, 2.15, 3.75, 3.65, "01 市场验证已完成", "Lely Vector 在 2021 年交付第 1000 套；DeLaval 在 2023 年披露 Optimat 已装机 600+ 牧场；GEA、Trioliet、Wasserbauer、Pellon 说明自动饲喂不再是概念验证。", C.accent);
  addSectionCard(slide, 4.8, 2.15, 3.75, 3.65, "02 客户正在向大场集中", "美国 2017 年 >=1,000 头奶牛牧场已占全国奶牛 55.2%；中国 2023 年奶牛规模化率约 76%。这类客户更有动力为降人工、夜间投喂和运营稳定性付费。", C.accent2);
  addSectionCard(slide, 8.8, 2.15, 3.73, 3.65, "03 你们不是从零开始", "FeedLogger 已覆盖配方、任务与追溯；Nimbo 已覆盖牛舍运行与推料协同；ATX 已具备 RTK/IMU/LiDAR/远程接管/电子围栏/安全栈。新增难点集中在重载车辆控制、TMR 工艺执行和功能安全。", C.accent3);

  addSmallSource(slide, "Sources: Lely, DeLaval, GEA, USDA ERS, 农业农村部, Sveaverken / FJD internal product materials.");
}

// Slide 4: Whitespace
{
  const slide = pptx.addSlide();
  applyBase(slide, "COMPETITIVE WHITESPACE", 4);
  addTitle(slide, "竞争格局与市场空白", "完整系统很多，但对存量 TMR 资产友好的无人化升级层仍稀缺。");

  slide.addShape(pptx.ShapeType.line, {
    x: 1.3,
    y: 5.8,
    w: 9.2,
    h: 0,
    line: { color: C.line, pt: 1.4 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 1.3,
    y: 2.1,
    w: 0,
    h: 3.7,
    line: { color: C.line, pt: 1.4 },
  });
  slide.addText("系统闭环度 →", {
    x: 9.3,
    y: 5.92,
    w: 1.2,
    h: 0.18,
    fontFace: FONT,
    fontSize: 9,
    color: C.muted,
    margin: 0,
  });
  slide.addText("对存量设备友好度 ↑", {
    x: 0.76,
    y: 1.95,
    w: 0.4,
    h: 1.0,
    fontFace: FONT,
    fontSize: 9,
    color: C.muted,
    rotate: 270,
    margin: 0,
  });

  function point(x, y, text, fill, w = 1.55) {
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w,
      h: 0.42,
      fill: { color: fill },
      line: { color: fill, pt: 0 },
    });
    slide.addText(text, {
      x: x + 0.06,
      y: y + 0.11,
      w: w - 0.12,
      h: 0.16,
      fontFace: FONT,
      fontSize: 8.5,
      bold: true,
      color: fill === C.dark ? "FFFFFF" : C.ink,
      align: "center",
      margin: 0,
    });
  }

  point(7.55, 5.0, "Lely / DeLaval / Trioliet", C.accentSoft, 2.3);
  point(6.0, 4.1, "GEA / Wasserbauer / Pellon", "DBEAFE", 2.35);
  point(8.15, 3.55, "KUHN AURA", "DCFCE7", 1.45);
  point(5.0, 3.05, "Faresin / SILOKING", "F1F5F9", 1.95);
  point(7.2, 2.55, "FS200 机会点", C.dark, 1.65);

  addPanel(slide, 10.95, 2.1, 1.6, 3.9, C.panel, C.line);
  slide.addText("空白定义", {
    x: 11.18,
    y: 2.4,
    w: 1.15,
    h: 0.22,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  addBulletList(slide, [
    "低土建",
    "少改造",
    "兼容存量 TMR 资产",
    "可与 FeedLogger / Nimbo 协同",
    "比完整系统更低 CAPEX",
  ], 11.16, 2.82, 1.1, { fontSize: 9.3, gap: 0.42, bulletColor: C.accent });

  addSmallSource(slide, "Representative products: Lely Vector, DeLaval Optimat, GEA DairyFeed F4500, Trioliet, KUHN AURA, Faresin, SILOKING.");
}

// Slide 5: Route comparison
{
  const slide = pptx.addSlide();
  applyBase(slide, "FEASIBILITY ROUTES", 5);
  addTitle(slide, "三条路线的可行性判断", "关键不是“都能不能做”，而是“哪条路线最适合先商业化”。");

  const rows = [
    [
      { text: "评估维度", options: { bold: true, color: "FFFFFF", align: "center" } },
      { text: "自走式 TMR retrofit", options: { bold: true, color: "FFFFFF", align: "center" } },
      { text: "拖拉机 + 拖拽式 retrofit", options: { bold: true, color: "FFFFFF", align: "center" } },
      { text: "无人取料 / 装料", options: { bold: true, color: "FFFFFF", align: "center" } },
    ],
    ["控制边界清晰度", "高", "中", "低"],
    ["车辆/作业耦合复杂度", "中", "高", "极高"],
    ["场内导航与安全压力", "中高", "高", "极高"],
    ["平台化复制性", "中高", "中低", "低"],
    ["上市速度", "快", "中", "慢"],
    ["商业优先级", "P1", "P2", "P3"],
  ];

  slide.addTable(rows, {
    x: 0.8,
    y: 2.15,
    w: 11.7,
    h: 3.35,
    fontFace: FONT,
    fontSize: 10,
    border: { type: "solid", color: C.line, pt: 1 },
    fill: C.panel,
    color: C.ink,
    rowH: 0.45,
    colW: [2.7, 2.9, 3.1, 2.95],
    margin: 0.08,
    valign: "mid",
    autoFit: false,
    fillHead: C.dark,
  });

  addPanel(slide, 0.8, 5.82, 11.7, 0.7, C.successSoft, "CDEFE3");
  slide.addText("建议：v1 只做“人工/半自动装料 + 无人投喂 + 自动回库”，先把 feed-out 跑通，再碰 loading。", {
    x: 1.05,
    y: 6.03,
    w: 11.1,
    h: 0.2,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.success,
    margin: 0,
  });
}

// Slide 6: MVP architecture
{
  const slide = pptx.addSlide();
  applyBase(slide, "MVP SCOPE", 6);
  addTitle(slide, "推荐 MVP：Autonomous Feed-Out Kit", "把“已装料后无人投喂”做成稳定可交付产品，而不是演示级原型。");

  const steps = [
    ["1", "FeedLogger 调度", "任务下发、配方调用、栏位/组别切换"],
    ["2", "人工/半自动装料", "首版保留人工装料，降低技术和安全风险"],
    ["3", "自主路径与避障", "RTK / IMU / LiDAR / geofence / 远程接管"],
    ["4", "精准投喂", "定量卸料、路线跟随、组别切换、作业闭环"],
    ["5", "自动回库/补能", "回库、充电/补能、异常告警与报表"],
  ];

  let x = 0.82;
  steps.forEach((step, idx) => {
    addPanel(slide, x, 2.55, 2.3, 2.2);
    addNumberTag(slide, x + 0.18, 2.78, step[0], idx === 2 ? C.accent2 : C.accent);
    slide.addText(step[1], {
      x: x + 0.54,
      y: 2.78,
      w: 1.55,
      h: 0.2,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: C.ink,
      margin: 0,
    });
    slide.addText(step[2], {
      x: x + 0.18,
      y: 3.23,
      w: 1.92,
      h: 1.08,
      fontFace: FONT,
      fontSize: 9.4,
      color: C.sub,
      margin: 0,
      valign: "top",
    });
    if (idx < steps.length - 1) {
      slide.addShape(pptx.ShapeType.chevron, {
        x: x + 2.37,
        y: 3.25,
        w: 0.28,
        h: 0.38,
        fill: { color: C.line },
        line: { color: C.line, pt: 0 },
      });
    }
    x += 2.55;
  });

  addPanel(slide, 0.82, 5.2, 11.68, 0.9, C.warnSoft, "FFD5DC");
  slide.addText("暂不纳入 v1：青贮取料、复杂倒车、任意 OEM 通用化、跨场区超长路线。", {
    x: 1.05,
    y: 5.48,
    w: 11.0,
    h: 0.18,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.warn,
    margin: 0,
  });
}

// Slide 7: Market sizing
{
  const slide = pptx.addSlide();
  applyBase(slide, "MARKET SIZING", 7);
  addTitle(slide, "市场规模测算：从场址池到 TAM / SAM / SOM", "先看可部署场址池，再收敛成可变现的套件规模。");

  const layers = [
    ["可部署场址池", "45k - 70k 场", 8.0, C.soft, C.ink],
    ["理论 TAM", "20k - 50k 套", 6.7, C.accentSoft, C.ink],
    ["现实 SAM", "10k - 25k 套", 5.4, "DBEAFE", C.ink],
    ["3-5 年 SOM", "1k - 3k 套", 4.1, "DCFCE7", C.ink],
  ];
  layers.forEach((layer, idx) => {
    const w = layer[2];
    const x = 1.0 + (8.0 - w) / 2;
    const y = 2.15 + idx * 0.86;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w,
      h: 0.66,
      fill: { color: layer[3] },
      line: { color: layer[3], pt: 0 },
    });
    slide.addText(layer[0], {
      x: x + 0.25,
      y: y + 0.17,
      w: 2.2,
      h: 0.16,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: layer[4],
      margin: 0,
    });
    slide.addText(layer[1], {
      x: x + w - 1.7,
      y: y + 0.17,
      w: 1.45,
      h: 0.16,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: layer[4],
      align: "right",
      margin: 0,
    });
  });

  addPanel(slide, 9.35, 2.15, 3.15, 3.45);
  slide.addText("核心假设", {
    x: 9.62,
    y: 2.42,
    w: 1.8,
    h: 0.2,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  addBulletList(slide, [
    "dairy-first，不含全部 beef feedlot",
    "只计 brownfield retrofit 子场景",
    "先自走式，后有限车型拖拽式",
    "按 US$20k/套渠道价估算硬件 TAM",
    "软件/服务收入尚未完全计入",
  ], 9.6, 2.82, 2.55, { fontSize: 9.2, gap: 0.42, bulletColor: C.accent });

  addKpiCard(slide, 9.35, 5.85, 3.15, 0.82, "Value Pool", "US$0.4B - 1.0B", "TAM 对应硬件口径", C.accent3);
}

// Slide 8: Geography and ICP
{
  const slide = pptx.addSlide();
  applyBase(slide, "GO-TO-MARKET", 8);
  addTitle(slide, "区域优先级与目标客户", "区域选择决定试点效率，客户画像决定交付难度。");

  addPanel(slide, 0.8, 2.15, 6.1, 4.35);
  slide.addText("区域优先级（可部署场址池 midpoint，k sites）", {
    x: 1.05,
    y: 2.42,
    w: 3.7,
    h: 0.18,
    fontFace: FONT,
    fontSize: 10,
    bold: true,
    color: C.ink,
    margin: 0,
  });

  const bars = [
    ["西北欧及欧洲核心奶区", 37.5, C.accent],
    ["北美", 10, C.accent3],
    ["中国", 3.5, C.accent2],
    ["大洋洲/中东/拉美部分市场", 7.5, "94A3B8"],
  ];
  let y = 3.0;
  bars.forEach((bar) => {
    slide.addText(bar[0], {
      x: 1.05,
      y,
      w: 2.1,
      h: 0.16,
      fontFace: FONT,
      fontSize: 9.2,
      color: C.sub,
      margin: 0,
    });
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 3.1,
      y: y - 0.02,
      w: 3.05,
      h: 0.22,
      fill: { color: "EEF2F7" },
      line: { color: "EEF2F7", pt: 0 },
    });
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 3.1,
      y: y - 0.02,
      w: (bar[1] / 40) * 3.05,
      h: 0.22,
      fill: { color: bar[2] },
      line: { color: bar[2], pt: 0 },
    });
    slide.addText(String(bar[1]), {
      x: 6.28,
      y: y - 0.02,
      w: 0.32,
      h: 0.16,
      fontFace: FONT,
      fontSize: 9.2,
      bold: true,
      color: C.ink,
      align: "right",
      margin: 0,
    });
    y += 0.7;
  });

  slide.addText("推荐进入顺序：西北欧 > 中国头部集团 > 北美大型奶场", {
    x: 1.05,
    y: 5.98,
    w: 5.15,
    h: 0.2,
    fontFace: FONT,
    fontSize: 10.5,
    bold: true,
    color: C.accent3,
    margin: 0,
  });

  addPanel(slide, 7.15, 2.15, 5.35, 4.35);
  slide.addText("首批 ICP", {
    x: 7.42,
    y: 2.42,
    w: 1.3,
    h: 0.18,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  addBulletList(slide, [
    ">= 800 头奶牛，或多组别多圈舍牧场",
    "每天 2 次以上投喂，夜间/错峰投喂有价值",
    "已具备标准化投喂路线，愿意接受 geofence 和限速区",
    "已有自走式 TMR 或少量标准化拖拉机 family",
    "具备数字化管理基础，能接受远程运维与日志追踪",
  ], 7.42, 2.88, 4.45, { fontSize: 9.7, gap: 0.48, bulletColor: C.accent });

  addSmallSource(slide, "Regional sizing uses a bottom-up deployable site pool estimate informed by USDA ERS, Europe dairy structure references, 农业农村部, DairyNZ and Dairy Australia.");
}

// Slide 9: Roadmap
{
  const slide = pptx.addSlide();
  applyBase(slide, "ROADMAP", 9);
  addTitle(slide, "产品路线图", "先打穿闭环，再扩模型族，再向完整无人饲喂平台延展。");

  slide.addShape(pptx.ShapeType.line, {
    x: 1.0,
    y: 3.65,
    w: 11.2,
    h: 0,
    line: { color: C.line, pt: 2 },
  });

  const phases = [
    {
      x: 1.0,
      w: 3.45,
      title: "Phase 1 | 2026 H2 - 2027 H1",
      tag: "Self-Propelled MVP",
      bullets: [
        "2-4 个自走式 TMR 车型适配",
        "3 个灯塔牧场试点",
        "人工装料 + 无人投喂 + 自动回库",
      ],
      color: C.accent,
    },
    {
      x: 4.93,
      w: 3.45,
      title: "Phase 2 | 2027 H2 - 2028",
      tag: "Limited Tractor Family",
      bullets: [
        "有限拖拉机 / 拖车平台适配",
        "dealer 安装与部署工具包",
        "远程接管与运维体系标准化",
      ],
      color: C.accent2,
    },
    {
      x: 8.86,
      w: 3.34,
      title: "Phase 3 | 2028+",
      tag: "Full Closed Loop",
      bullets: [
        "无人取料 / 装料",
        "多车协同调度",
        "软件与服务收入放大",
      ],
      color: C.accent3,
    },
  ];

  phases.forEach((phase) => {
    addPanel(slide, phase.x, 2.15, phase.w, 2.45);
    slide.addShape(pptx.ShapeType.rect, {
      x: phase.x,
      y: 2.15,
      w: phase.w,
      h: 0.08,
      fill: { color: phase.color },
      line: { color: phase.color, pt: 0 },
    });
    slide.addText(phase.title, {
      x: phase.x + 0.18,
      y: 2.42,
      w: phase.w - 0.36,
      h: 0.18,
      fontFace: FONT,
      fontSize: 10.2,
      bold: true,
      color: C.ink,
      margin: 0,
    });
    addPill(slide, phase.tag, phase.x + 0.18, 2.76, 1.6, phase.color, phase.color === C.accent2 ? "DCFCE7" : C.soft);
    addBulletList(slide, phase.bullets, phase.x + 0.18, 3.26, phase.w - 0.45, {
      fontSize: 9.4,
      gap: 0.38,
      bulletColor: phase.color,
    });
  });

  addPanel(slide, 1.0, 5.15, 11.2, 1.05, C.panel, C.line);
  slide.addText("North-star metrics", {
    x: 1.26,
    y: 5.43,
    w: 1.8,
    h: 0.18,
    fontFace: FONT,
    fontSize: 10.5,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText(">99% 任务完成率    <=2% 投喂误差    >=1 个日常投喂岗位替代 / 显著减少夜班与周末人工", {
    x: 3.0,
    y: 5.41,
    w: 8.9,
    h: 0.2,
    fontFace: FONT,
    fontSize: 10.2,
    bold: true,
    color: C.accent3,
    margin: 0,
  });
}

// Slide 10: Risks and next actions
{
  const slide = pptx.addSlide();
  applyBase(slide, "RISKS & NEXT STEPS", 10);
  addTitle(slide, "关键风险与 90 天动作", "先把不确定性前置，而不是在量产时暴露。");

  addPanel(slide, 0.8, 2.15, 5.65, 4.35);
  slide.addText("关键风险", {
    x: 1.05,
    y: 2.42,
    w: 1.2,
    h: 0.18,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });

  const risks = [
    ["功能安全", "人牛混行、低速防撞、远程接管和责任边界必须按工业产品标准设计。", C.warn],
    ["多 OEM 适配", "品牌/年份/液压逻辑差异会迅速放大售后复杂度，必须限车型族。", C.accent3],
    ["loading 难度", "青贮面和料堆属于非结构化场景，不适合在 v1 承诺。", C.accent2],
    ["CAPEX 周期", "中国奶业短期盈利承压，首批项目必须用明确 ROI 说服客户。", C.accent],
  ];
  let ry = 2.86;
  risks.forEach((risk) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 1.05,
      y: ry,
      w: 4.95,
      h: 0.7,
      fill: { color: C.panel },
      line: { color: C.line, pt: 1 },
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: 1.05,
      y: ry,
      w: 0.08,
      h: 0.7,
      fill: { color: risk[2] },
      line: { color: risk[2], pt: 0 },
    });
    slide.addText(risk[0], {
      x: 1.23,
      y: ry + 0.14,
      w: 1.2,
      h: 0.18,
      fontFace: FONT,
      fontSize: 10,
      bold: true,
      color: C.ink,
      margin: 0,
    });
    slide.addText(risk[1], {
      x: 2.24,
      y: ry + 0.12,
      w: 3.45,
      h: 0.34,
      fontFace: FONT,
      fontSize: 8.9,
      color: C.sub,
      margin: 0,
    });
    ry += 0.9;
  });

  addPanel(slide, 6.7, 2.15, 5.82, 4.35);
  slide.addText("未来 90 天建议动作", {
    x: 6.98,
    y: 2.42,
    w: 1.8,
    h: 0.18,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });

  const actions = [
    "锁定 MVP 边界：明确只做 self-propelled feed-out，不做 loading。",
    "选定 2-4 个车型家族：完成控制接口、液压逻辑和安全冗余梳理。",
    "筛 3 个灯塔牧场：优先西北欧 1-2 个、中国头部集团 1 个。",
    "建立 ROI 模型：岗位替代、夜班减少、投喂一致性和饲料浪费下降要量化。",
    "形成 dealer/实施标准包：建图、培训、远程接管、维保和安全 SOP。",
  ];
  actions.forEach((action, idx) => {
    addNumberTag(slide, 7.02, 2.9 + idx * 0.63, idx + 1, idx < 2 ? C.accent3 : C.accent);
    slide.addText(action, {
      x: 7.42,
      y: 2.92 + idx * 0.63,
      w: 4.7,
      h: 0.22,
      fontFace: FONT,
      fontSize: 9.5,
      color: C.ink,
      margin: 0,
    });
  });

  addPanel(slide, 6.98, 5.86, 5.14, 0.43, C.successSoft, "CDEFE3");
  slide.addText("立项建议：批准 Phase 1 概念验证，目标是在 6-9 个月内完成首个“已装料后无人投喂”闭环。", {
    x: 7.18,
    y: 5.98,
    w: 4.8,
    h: 0.16,
    fontFace: FONT,
    fontSize: 9.6,
    bold: true,
    color: C.success,
    margin: 0,
  });
}

// Slide 11: Sources
{
  const slide = pptx.addSlide();
  applyBase(slide, "APPENDIX | SOURCES", 11);
  addTitle(slide, "关键公开来源", "用于支撑自动饲喂成熟度、行业结构与市场规模口径。");

  const left = [
    "Lely Vector official page / 1000th Vector news",
    "DeLaval Optimat / OptiWagon official launch",
    "GEA DairyFeed F4500 official page and launch release",
    "KUHN AURA official materials",
    "Trioliet automatic feeding materials",
    "USDA ERS dairy structure references",
  ];
  const right = [
    "农业农村部：中国奶业质量报告与稳定奶牛生产政策",
    "DairyNZ facts & figures",
    "Dairy Australia annual reports",
    "Sveaverken animal farming product page",
    "FJD ATX product page and internal input materials",
    "Project artifacts: framing / competitor matrix / feasibility memo",
  ];

  addPanel(slide, 0.8, 2.15, 5.6, 4.2);
  addPanel(slide, 6.93, 2.15, 5.6, 4.2);
  slide.addText("External sources", {
    x: 1.05,
    y: 2.42,
    w: 1.6,
    h: 0.18,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText("China + internal sources", {
    x: 7.18,
    y: 2.42,
    w: 2.0,
    h: 0.18,
    fontFace: FONT,
    fontSize: 11,
    bold: true,
    color: C.ink,
    margin: 0,
  });

  addBulletList(slide, left, 1.05, 2.9, 4.9, { fontSize: 9.5, gap: 0.56, bulletColor: C.accent });
  addBulletList(slide, right, 7.18, 2.9, 4.9, { fontSize: 9.5, gap: 0.56, bulletColor: C.accent2 });

  slide.addText("备注：全部数值为基于公开资料与内部假设的估算口径，适合作为立项与管理层讨论底稿，不应直接对外发布为第三方认证市场数据。", {
    x: 0.82,
    y: 6.56,
    w: 11.5,
    h: 0.2,
    fontFace: FONT,
    fontSize: 8.5,
    color: C.muted,
    margin: 0,
  });
}

function addTextBlock(slide, title, paragraphs, x, y, w) {
  slide.addText(title, {
    x,
    y,
    w,
    h: 0.2,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  paragraphs.forEach((p, idx) => {
    slide.addShape(pptx.ShapeType.ellipse, {
      x,
      y: y + 0.43 + idx * 0.38,
      w: 0.08,
      h: 0.08,
      fill: { color: idx === 3 ? C.accent2 : C.accent },
      line: { color: idx === 3 ? C.accent2 : C.accent, pt: 0 },
    });
    slide.addText(p, {
      x: x + 0.16,
      y: y + 0.38 + idx * 0.38,
      w: w - 0.18,
      h: 0.22,
      fontFace: FONT,
      fontSize: 10.2,
      color: C.sub,
      margin: 0,
    });
  });
}

const out = "second-brain-os/projects/active/ai-coding-agent-competitive-analysis/artifacts/current/20260319_delivery_tmr-unmanned-market-deck-tech-minimal-v1.pptx";

pptx.writeFile({ fileName: out });
