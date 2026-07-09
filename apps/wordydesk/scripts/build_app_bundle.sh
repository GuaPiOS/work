#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_HOME="$ROOT_DIR/.codex-home"
MODULE_CACHE="$ROOT_DIR/.build/module-cache"
CLANG_CACHE="$ROOT_DIR/.build/clang-module-cache"
APP_DIR="$ROOT_DIR/dist/WordyDesk.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"

mkdir -p "$BUILD_HOME" "$MODULE_CACHE" "$CLANG_CACHE"

env \
  HOME="$BUILD_HOME" \
  SWIFTPM_MODULECACHE_OVERRIDE="$MODULE_CACHE" \
  CLANG_MODULE_CACHE_PATH="$CLANG_CACHE" \
  swift build --disable-sandbox

mkdir -p "$MACOS_DIR"

cp "$ROOT_DIR/.build/debug/WordyDesk" "$MACOS_DIR/WordyDesk"

cat > "$CONTENTS_DIR/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>WordyDesk</string>
  <key>CFBundleIdentifier</key>
  <string>com.guapi.wordydesk</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>WordyDesk</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>0.1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSApplicationCategoryType</key>
  <string>public.app-category.education</string>
  <key>LSMinimumSystemVersion</key>
  <string>14.0</string>
  <key>LSUIElement</key>
  <true/>
  <key>NSServices</key>
  <array>
    <dict>
      <key>NSMenuItem</key>
      <dict>
        <key>default</key>
        <string>Look Up in WordyDesk</string>
      </dict>
      <key>NSMessage</key>
      <string>lookupSelectedText</string>
      <key>NSPortName</key>
      <string>WordyDesk</string>
      <key>NSSendTypes</key>
      <array>
        <string>NSStringPboardType</string>
      </array>
    </dict>
  </array>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

printf 'APPL????' > "$CONTENTS_DIR/PkgInfo"

codesign --force --deep --sign - "$APP_DIR" >/dev/null 2>&1 || true

echo "Built app bundle at: $APP_DIR"
