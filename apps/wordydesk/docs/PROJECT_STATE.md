# WordyDesk Project State

最后更新时间：2026-03-15

## 目标

`WordyDesk` 是一个 macOS 菜单栏词汇学习工具，核心流程是：

1. 用户在任意应用中选中英文单词
2. `WordyDesk` 读取选中文本
3. 生成简短英译英解释和简单例句
4. 朗读单词或例句
5. 保存到本地 Markdown
6. 进入本地复习计划，按遗忘曲线安排复习

## 当前已实现

- 菜单栏应用，支持单实例运行
- 可打开的独立可缩放主窗口
- 自动选词捕获
- 快捷键捕获：`Option-Command-G`
- 本地词典英译英解释
- 简单英文例句生成
- 系统语音朗读
- 可选云 TTS 提供器：
  - `System`
  - `ElevenLabs`
  - `OpenAI`
- 本地 Markdown 收藏
- 本地学习计划与复习状态
- 今日统计、到期复习、学习连续天数
- 提醒开关
- 菜单栏退出、重启
- 右上角问号引导入口
- 黑白极简 UI
- 浮窗支持拖动
- macOS Services 入口：
  - `Look Up in WordyDesk`

## 当前 Markdown 格式

```md
## word <sub>simple English meaning</sub>
- Example: simple sentence
```

文件位置：

- Markdown：`~/Library/Application Support/WordyDesk/collected-words.md`
- 学习记录：`~/Library/Application Support/WordyDesk/study-progress.json`

## 当前已知边界

- 右键入口走的是 macOS `Services`，通常出现在右键菜单的 `Services` 子菜单内，不保证出现在最外层。
- `Services` 菜单有系统缓存，更新后有时需要重新聚焦应用或等待系统刷新。
- 本地解释来自 `DictionaryServices`，质量受系统词典内容限制。
- 云 TTS 只有在设置里填入 key 后才生效，否则自动回退到系统语音。
- `NSSpeechSynthesizer` 仍用于 phoneme 辅助，因此编译有弃用警告，但当前不阻塞功能。

## 当前最值得继续做的方向

1. 把右键 `Services` 进一步升级成更稳定的系统文本服务体验
2. 引入真正高质量的词典/例句数据源，而不是仅靠本地词典和模板句
3. 改造复习体验，提升长期学习可用性
