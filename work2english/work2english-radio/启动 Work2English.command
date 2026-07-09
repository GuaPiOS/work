#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  Work2English OS — double-click launcher
#
#  双击此文件即可：构建 UI（仅首次）→ 启动服务 → 打开浏览器。
#  关闭弹出的终端窗口（或 Ctrl+C）即停止。
#  可拖到 Dock 最左侧，以后点一下就开。
# ─────────────────────────────────────────────────────────────────────────────

# 1) 切到本文件所在目录（项目根），路径含空格也能正确处理
cd "$(dirname "$0")" || exit 1

# 1b) 确保 lark-cli（飞书采集器依赖）在 PATH 上
for CANDIDATE in "$HOME/.npm-global/bin" "$HOME/.local/bin" "/usr/local/bin" "/opt/homebrew/bin"; do
  if [ -d "$CANDIDATE" ]; then
    case ":$PATH:" in
      *":$CANDIDATE:"*) ;;
      *) PATH="$CANDIDATE:$PATH" ;;
    esac
  fi
done
export PATH

# 2) 选 Python：优先项目虚拟环境
PY=""
if [ -x ".venv/bin/python" ] && .venv/bin/python -c "import yaml, requests" 2>/dev/null; then
  PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import yaml, requests" 2>/dev/null; then
  PY="python3"
else
  echo "❌ 找不到带依赖的 Python。请在项目目录运行："
  echo "   python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  echo ""
  read -n 1 -s -r -p "按任意键关闭…"
  exit 1
fi

# 3) 每次启动都确保飞书采集器在跑（轻量、常驻）。Ollama + 翻译按需启动。
#    放在"服务已在跑"判断之前，这样即使 UI 已开着，点击启动器也会把采集器拉起来。
echo "▸ 确保飞书采集器运行（收到消息才唤醒 Ollama 做翻译）…"
"$PY" radio_service.py start 2>&1 | sed 's/^/   /' || echo "   (采集器启动遇到问题，详见 logs/)"

# 4) 如果 UI 服务已在跑，直接打开浏览器即可（重复点击的情况）
if curl -s --max-time 2 http://localhost:8000/api/health >/dev/null 2>&1; then
  echo "✓ UI 已在运行，打开浏览器…"
  open "http://localhost:8000"
  exit 0
fi

# 5) 首次运行或源码有更新：构建/重新构建 UI
NEEDS_BUILD=0
if [ ! -f "ui/dist/index.html" ]; then
  NEEDS_BUILD=1
else
  # 源码比构建产物新 → 需要重建（用最新修改的源文件对比 dist 时间）
  NEWEST_SRC=$(find ui/src -type f -newer ui/dist/index.html 2>/dev/null | head -1)
  NEWEST_CFG=""
  [ -f ui/vite.config.ts ] && [ ui/vite.config.ts -nt ui/dist/index.html ] && NEWEST_CFG="x"
  if [ -n "$NEWEST_SRC" ] || [ -n "$NEWEST_CFG" ]; then
    NEEDS_BUILD=1
  fi
fi

if [ "$NEEDS_BUILD" = "1" ]; then
  if [ ! -f "ui/dist/index.html" ]; then
    echo "▸ 首次运行，构建界面（约 30 秒）…"
  else
    echo "▸ 检测到界面有更新，重新构建…"
  fi
  if ! command -v npm >/dev/null 2>&1; then
    echo "❌ 未检测到 npm。请先安装 Node.js（https://nodejs.org）。"
    read -n 1 -s -r -p "按任意键关闭…"
    exit 1
  fi
  cd ui || exit 1
  unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy 2>/dev/null
  [ -d node_modules ] || npm install
  npm run build || npx vite build --emptyOutDir false
  cd ..
  echo "✓ 界面构建完成。"
fi

# 6) 启动 UI 服务（后台），退出时自动清理
echo "▸ 启动 Work2English OS 界面…"
"$PY" server.py &
SERVER_PID=$!
cleanup() {
  kill "$SERVER_PID" 2>/dev/null
  wait "$SERVER_PID" 2>/dev/null
}
trap cleanup EXIT INT TERM

# 7) 等服务就绪后打开浏览器
for i in $(seq 1 40); do
  if curl -s --max-time 1 http://localhost:8000/api/health >/dev/null 2>&1; then
    open "http://localhost:8000"
    break
  fi
  sleep 0.5
done

echo ""
echo "──────────────────────────────────────────────"
echo "  ▶  Work2English OS  →  http://localhost:8000"
echo "     飞书消息自动翻译；Ollama 用时才起，闲时释放内存。"
echo "     关闭此窗口只停 UI；要停采集器：python3 radio_service.py stop"
echo "──────────────────────────────────────────────"
echo ""

# 8) 前台等待，日志实时显示
wait "$SERVER_PID"
