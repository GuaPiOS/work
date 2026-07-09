# WordyDesk Runbook

## 本地恢复开发

### 1. 读上下文

先读：

1. [PROJECT_STATE.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/PROJECT_STATE.md)
2. [BACKLOG.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/BACKLOG.md)

### 2. 编译

```bash
env HOME=/Users/guapi/Documents/New\ project/apps/wordydesk/.codex-home \
SWIFTPM_MODULECACHE_OVERRIDE=/Users/guapi/Documents/New\ project/apps/wordydesk/.build/module-cache \
CLANG_MODULE_CACHE_PATH=/Users/guapi/Documents/New\ project/apps/wordydesk/.build/clang-module-cache \
swift build --disable-sandbox
```

### 3. 打包

```bash
apps/wordydesk/scripts/build_app_bundle.sh
```

### 4. 安装

```bash
ditto '/Users/guapi/Documents/New project/apps/wordydesk/dist/WordyDesk.app' '/Applications/WordyDesk.app'
```

### 5. 重启

```bash
killall WordyDesk || true
open '/Applications/WordyDesk.app'
```

### 6. 检查实例数

```bash
osascript -e 'tell application "System Events" to count (every process whose name is "WordyDesk")'
```

期望结果：

- 输出 `1`

## 右键 Services 刷新

如果更新后右键菜单里没看到 `Look Up in WordyDesk`：

```bash
/System/Library/CoreServices/pbs -flush
```

然后：

- 重新打开目标应用的右键菜单
- 检查 `Services` 子菜单

## 修改后必须同步更新的文件

如果功能发生变化，至少更新下面其中一项：

- [PROJECT_STATE.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/PROJECT_STATE.md)
- [BACKLOG.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/BACKLOG.md)
- [ARCHITECTURE.md](/Users/guapi/Documents/New project/apps/wordydesk/docs/ARCHITECTURE.md)
