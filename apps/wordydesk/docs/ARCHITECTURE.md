# WordyDesk Architecture

## 目录边界

- 应用入口：`apps/wordydesk/Package.swift`
- 应用源码：`apps/wordydesk/Sources/`
- 打包脚本：`apps/wordydesk/scripts/build_app_bundle.sh`
- 项目上下文：`apps/wordydesk/docs/`

不要把 `WordyDesk` 的持续开发状态继续塞进仓库根 `README.md` 里。根 README 属于整个仓库，不是 app 专属上下文层。

## 主要模块

### 入口与单实例

- [WordyDeskApp.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/WordyDeskApp.swift)
- [AppInstanceManager.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/AppInstanceManager.swift)

职责：

- 启动 app
- 维护单实例
- 菜单栏 scene
- 独立窗口 scene

### 应用状态中心

- [AppModel.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/AppModel.swift)

职责：

- 捕获选中文本
- 构造 `WordEntry`
- 驱动朗读
- 驱动保存
- 驱动复习与统计
- 驱动引导、状态消息、窗口交互

这是当前最高上下文密度文件。后续重构优先从这里拆责任。

### 文本捕获

- [SelectionCaptureService.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/SelectionCaptureService.swift)
- [WordyDeskService.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/WordyDeskService.swift)

职责：

- 快捷键/自动选词读取
- macOS `Services` 入口读取

### 词条与数据模型

- [Models.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/Models.swift)

职责：

- `WordEntry`
- `StudyRecord`
- 复习评级
- 统计模型

### 解释、例句、朗读

- [DictionaryLookupService.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/DictionaryLookupService.swift)
- [ExampleSentenceGenerator.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/ExampleSentenceGenerator.swift)
- [SpeechService.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/SpeechService.swift)
- [SpeechProvider.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/SpeechProvider.swift)

职责：

- 本地词典英译英
- 简单例句模板
- 系统/云 TTS

### 持久化

- [FavoritesStore.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/FavoritesStore.swift)
- [StudyStore.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/StudyStore.swift)
- [AppPreferences.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/AppPreferences.swift)
- [ReminderScheduler.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/ReminderScheduler.swift)

职责：

- Markdown 收藏
- 学习进度 JSON
- 用户偏好
- 每日提醒

### UI

- [ContentView.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/ContentView.swift)
- [QuickPopupController.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/QuickPopupController.swift)
- [SettingsView.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/SettingsView.swift)
- [OnboardingView.swift](/Users/guapi/Documents/New project/apps/wordydesk/Sources/OnboardingView.swift)

职责：

- 主窗口与菜单栏面板
- 黑白极简风格
- 浮窗交互
- 设置与引导

## 后续重构建议

如果继续加功能，优先做这两个拆分：

1. 从 `AppModel.swift` 拆出 `CaptureCoordinator`、`StudyCoordinator`
2. 从 `ContentView.swift` 拆出 `NowView`、`ReviewView`、`PlanView`

原因：

- 这两个文件正在成为新的上下文热点
- 再继续叠功能会明显拖慢理解速度
