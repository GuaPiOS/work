# Work2English Radio

本地工作英语播报器 —— 把飞书中文工作信息变成自然英文语音循环播放，并以学习表（中英对照 + 焦点短语 + 学习点）的形式呈现。

## 项目目标

从飞书复制中文工作内容 → AI 改写为自然英文播报稿 → TTS 生成英文音频 → 本地循环播放 + 学习对照。

## 架构

核心逻辑在 `w2e/` Python 包里，入口文件（`run.py` / `server.py` / `radio_service.py` / `feishu_collect.py`）是薄壳：

- `w2e/config.py` — 配置单一数据源（config.yaml ← runtime 覆盖 ← 环境变量）
- `w2e/runtime.py` — 进程/PID/日志/空闲看门狗基础（stdlib）
- `w2e/feishu.py` — 飞书事件解析、去重、收件箱、回执
- `w2e/llm.py` / `w2e/study.py` / `w2e/tts.py` — 改写、学习产物、TTS
- `w2e/generate.py` — 统一生成调度（debounce + 单飞，飞书与 UI 共用）
- `w2e/playback.py` — 可插拔播放子系统（浏览器优先、本地 afplay 兜底）
- `w2e/health.py` — UI 与 CLI 共用的健康检查

播放层是可扩展的：生成完成后由 `PlaybackCoordinator` 选一个 adapter 播放（浏览器在线→UI 播放；否则本地 afplay 兜底），并据实生成飞书回执（不会再出现"说开始播放但没播"）。未来新增移动端/远程客户端只需实现同一个 adapter 协议。

## 快速开始

### 1. 前置依赖

```bash
# 安装 Ollama
brew install ollama

# 启动 Ollama
ollama serve

# 拉取模型
ollama pull qwen3:8b
```

### 2. 安装 Python 依赖

> ⚠️ **重要：安装 edge-tts 前先关掉代理。** 如果你配置了公司代理（HTTP_PROXY / HTTPS_PROXY），pip 会走代理下载 edge-tts，大概率失败。需要先 unset 环境变量再安装。

```bash
cd work2english-radio
python3 -m venv .venv
source .venv/bin/activate

# 先检查是否有代理
echo $HTTP_PROXY

# 如果有输出，安装前必须关掉代理
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy

pip install -r requirements.txt

# 安装完可以恢复代理（Mac 上开新的终端窗口即可，不影响）
```

安装完成后验证：

```bash
# 检查 edge-tts 是否可用
edge-tts --help
```

如果提示 `edge-tts: command not found`，说明 pip 把 edge-tts 装到了 `~/.local/bin`，该目录不在 PATH 里。两个解决办法：

1. 不用管——`run.py` 已经自动搜索 `~/.local/bin`，直接跑就行。
2. 如果想在命令行里手动调 edge-tts，执行 `export PATH="$HOME/.local/bin:$PATH"`。

### 2.1 Fish Audio 免费 S2.1 Pro

当前项目已经切到 Fish Audio 免费模型：

```yaml
tts:
  provider: "fish-audio"

fish_audio:
  endpoint: "https://api.fish.audio/v1/tts"
  model: "s2.1-pro-free"
```

API key 存在本机 `config.yaml` 的 `fish_audio.api_key`，不要提交到公开仓库。也可以改用环境变量：

```bash
export FISH_AUDIO_API_KEY="你的 Fish Audio key"
```

Fish Audio 的英文声音用 `fish_audio.voices[].id` 配置。`tts.voice` 必须是 Fish 的 voice UUID；如果 UI 里残留了 Edge voice，程序会自动回退到 `fish_audio.voices` 里的第一个 Fish voice。

验证 Fish TTS：

```bash
./status.sh
```

看到类似下面输出表示配置已被识别：

```text
fish-audio: ready (model=s2.1-pro-free)
```

### 3. 复制到另一台电脑

整个项目文件夹可以直接复制到另一台 Mac 上使用，但有两点需要注意：

**.venv 不能随项目复制**

`.venv` 里的路径是硬编码到当前机器的，换机器后会失效。所以复制项目后要删掉旧的 `.venv`，在新机器上重建：

```bash
cd work2english-radio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.gitignore` 已经排除了 `.venv/`，如果用 git 同步项目，不会把虚拟环境带过去。

**新机器也需要装 Ollama 并拉模型**

```bash
brew install ollama
ollama pull qwen3:8b
```

**不需要带走的文件**

这些文件和文件夹是运行时生成的，复制项目时可以不带：

- `.venv/` — 虚拟环境，每台机器重建
- `output/` — 生成的英文稿和音频，新机器会重新生成
- `logs/` — 运行日志

**唯一需要持久化的文件就是项目源码本身**：`run.py`、`config.yaml`、`prompts/`、`requirements.txt`、`inbox/feishu_raw.md`。`requirements.txt` 只写了三行依赖（requests、pyyaml、edge-tts），任何机器上都能用同样的三条命令重建环境。

### 4. 使用

#### 本地文件模式

1. 打开飞书，复制中文工作内容
2. 粘贴到 `inbox/feishu_raw.md`
3. 运行 `python run.py --once`
4. 系统自动生成英文播报稿和音频，并启动本地播放

```bash
python run.py --once
```

停止播放：按 `Ctrl + C`。

#### 飞书机器人投喂模式

一键开启：

```bash
./start.sh
```

一键开启会启动轻量常驻收集器 `feishu_collect.py`。收到飞书新内容后，系统会按需启动 Ollama、生成英文和 MP3，并自动开始播放；空闲后会释放 Ollama 和播放器。

也可以在 Finder 中双击 `start.command`。

双击 `start.command` 后，Terminal 显示 `[进程已完成]` 是正常现象。`start.command` 会用 `nohup` 在后台执行 `./start.sh`，避免 Terminal 窗口结束时带走后台服务；真正的服务状态请过几秒用 `./status.sh` 查看。启动日志在 `logs/start.command.log`。

一键关闭：

```bash
./stop.sh
```

一键关闭会停止飞书收集器、内容监听器、当前播放器，以及本脚本启动的 Ollama 服务。

也可以在 Finder 中双击 `stop.command`。

`stop` 会写入 `runtime/stop.request`，用于打断尚未完成的后台启动流程。这样即使刚双击 `start.command` 后马上停止，也不会出现旧的后台启动流程继续执行、把服务又拉起来的情况。下一次正常启动会自动清除这个停止标记。

查看状态：

```bash
./status.sh
```

如果你给飞书机器人发消息后没有开始读，先执行：

```bash
./status.sh
```

空闲状态下正常应该看到：

```text
ollama: stopped
collector: running
player: stopped
```

收到新消息并生成/播放时，`ollama` 和 `player` 会临时变成 `running`；播放空闲一段时间后会自动停止重资源。

如果 `collector` 运行但没有收到消息，执行一次重启：

```bash
./stop.sh
./start.sh
```

后台收集器会自动定位 `lark-cli`。优先使用当前 PATH；如果双击 `.command` 时 PATH 不完整，会继续查找这些常见位置：

- `~/.npm-global/bin/lark-cli`
- `~/.local/bin/lark-cli`
- `/opt/homebrew/bin/lark-cli`
- `/usr/local/bin/lark-cli`

如果 `logs/collector.out.log` 里出现 `lark-cli not found`，先在终端执行：

```bash
command -v lark-cli
```

把输出路径加入 PATH，或安装到上面任一位置。

如果机器人已经回复“收到内容，正在生成英文播报”，说明飞书消息已经进入本地收集器。接着检查是否生成了新音频：

```bash
stat -f '%Sm %N' -t '%Y-%m-%d %H:%M:%S' output/today_audio.mp3 output/today_en.md
tail -n 40 logs/run.log
```

`logs/run.log` 末尾出现 `Generated successfully.`，并且 `logs/player.out.log` 出现 `player: loaded playlist` / `player: playing ...`，表示已经生成并开始播放。

如果你听到的仍然像旧内容，先看主播报稿开头是否已经包含最新消息：

```bash
sed -n '1,3p' output/today_en.md
```

如果 `output/today_en.md` 已经是最新内容但声音没切换，重启一次后台服务：

```bash
./stop.sh
./start.sh
```

播放器异常会写入：

```bash
tail -n 40 logs/player.out.log
```

所有后台进程都会把 stdin 接到 `/dev/null`，并忽略 Terminal 关闭时发出的 SIGHUP，避免双击 `.command` 后 Terminal 结束导致后台服务或播放器子进程退出。`./status.sh` 会识别已经退出的 zombie 播放器进程；如果看到 `player: stopped`，重新执行 `./start.sh` 即可用当前最新音频恢复循环播放。

打开当天学习对照表：

```bash
./open_study.sh
```

也可以在 Finder 中双击 `open_study.command`。

飞书机器人投喂会按天累积到 `inbox/feishu_raw.md`。`run.py --watch` 每次检测到当天内容变化后，会重新生成当天合集音频，并循环播放整天内容。跨天后，采集器会自动开始新的当天合集，同时把每日内容同步保存到 `inbox/daily/YYYY-MM-DD.md`。

#### 当天飞书信息自动汇总

除了主动发给机器人，也可以一次性读取当前用户当天可见的飞书消息、日历，以及当天新建或到期的任务。

这条入口和机器人直发是解耦的：系统会先把原始数据归档到 `inbox/sources/feishu-YYYY-MM-DD.json`，再生成一份中文学习摘要 `inbox/digest/YYYY-MM-DD.md`。只有当生成策略允许时，才把 digest 投喂到现有的英语转换、学习表和朗读流程。

系统会优先选择私聊、@你、你的发言及其上下文，并在多个聊天之间均衡选取。A2 → B1 默认每天只保留 3 个高价值学习点：

```bash
python daily_collect.py
```

只采集并查看摘要、不生成英语和音频：

```bash
python daily_collect.py --collect-only
```

立即生成，忽略电脑空闲策略：

```bash
python daily_collect.py --force-generate
```

补采指定日期：

```bash
python daily_collect.py --date 2026-07-13
```

这一功能使用飞书用户身份（`--as user`），因为机器人身份无法读取个人可见的聊天、日历和任务。首次使用时需要最小只读权限：

```bash
lark-cli auth login --scope "search:message calendar:calendar.event:read task:task:read"
```

消息搜索会自动读取全部分页结果，但不会把所有群消息都交给本地模型。内容筛选由本地代码完成，因此只需要一次模型调用来生成 A2 → B1 英语，响应更稳定，也避免活跃大群淹没真正与你相关的信息。重复运行当天汇总会替换旧的 daily digest section，但保留你主动发给机器人的内容；原始机器人事件仍保存在 `inbox/events/`。当前版本不会自动读取消息中的附件正文、妙记全文或浏览过但没有聊天记录的文档。

默认配置下，`daily_collect.py` 会先完成收集和 digest 写入，然后检查 `daily_digest.generation_policy`：

- `idle`：电脑空闲达到 `daily_digest.min_idle_seconds` 后才生成英语和音频。
- `always`：收集后立即生成。
- `never`：只写 digest，不自动生成。

每次生成后，系统也会创建学习对照表：`output/study/YYYY-MM-DD/index.html`。表格里包含原文、自然英文、学习点和逐条 MP3，可点击播放对照学习。

飞书事件流可能在重连后补发旧消息，或者给同一内容生成新的 `message_id`。收集器会在回执前先做过滤：启动前超过 `collector.ignore_events_older_than_start_seconds` 的历史事件会被忽略；同一聊天、同一发送者、同一文本在 `collector.duplicate_text_window_seconds` 内只处理一次。去重状态保存在 `runtime/event_dedupe_state.json`。

主音频 `output/today_audio.mp3` 会优先播报最新投喂的内容，再继续播报当天其他内容；学习对照表仍按当天内容完整保留，方便逐条对照。这样给机器人发新消息后，不需要等长文档播完，就能先听到最新那条消息。

播放层现在由 `runtime/player_control.json` 控制。每次新内容生成语音后，会立刻更新播放队列；如果此时正在读某一条 MP3，不会中断当前句子，而是在当前条读完后切到最新内容。

如果新消息在上一轮生成过程中到达，收集器会记录一次 pending 生成；当前轮结束后会立刻再生成一次，确保最新内容不会因为“生成中”而漏播。

`player.mode` 控制重复方式（前端学习中心提供两个选项，后端兼容旧值）：

- `auto`: 默认。优先播报最新一次投喂的内容。
- `daily`: 循环当天学习表里的全部条目。
- （`single` / `list` 仍向后兼容，由 `auto` 智能覆盖。）

当前生成链路的分工是：Ollama 只负责逐条把中文改写成自然英文和学习点；当天总播报由本地程序按“最新内容优先”稳定拼接。这样可以避免模型在长文档场景里忽略最新短消息，也能减少生成时间。

如果需要调试，可以手动分两个终端运行：

```bash
python run.py --watch
python feishu_collect.py
```

支持的飞书输入：

- 私聊机器人发送中文文本
- 私聊机器人发送飞书文档链接
- 群聊中 `@机器人 /read 中文文本`
- 群聊中 `@机器人 /doc 飞书文档链接`
- 群聊中 `@机器人 飞书文档链接`

不支持自动监听所有群消息、别人 @ 你本人的消息、历史消息、图片、语音、附件、表格卡片和 Web UI。

停止播放：`python run.py --watch` 中按 `Ctrl + C`，会同时停止当前音频播放。

## 配置

编辑 `config.yaml`：

- `level`: 英语难度等级，可选 `A2` / `B1` / `B2`
- `tts.provider`: TTS 服务，可选 `fish-audio` / `edge-tts`
- `tts.voice`: TTS 声音。Fish Audio 下填写 Fish voice UUID；Edge 下填写 `en-US-JennyNeural` / `en-US-AriaNeural`
- `tts.rate`: 语速，如 `-5%`、`-15%`
- `fish_audio.model`: Fish Audio 模型，免费 S2.1 Pro 使用 `s2.1-pro-free`
- `fish_audio.voices`: Fish Audio 可选声音列表，第一项会作为默认声音
- `llm.num_predict`: 模型最大输出长度，默认 `1200`；如果长文档条目很多但生成 JSON 不完整，可以临时调大
- `collector.ignore_events_older_than_start_seconds`: 忽略启动前太久的飞书补发事件，默认 `120`
- `collector.duplicate_text_window_seconds`: 同一聊天同一发送者同文本的去重窗口，默认 `600`
- `player.mode`: 播放重复模式，默认 `auto`；可选 `single` / `list` / `daily`
- `player.loop`: 是否循环播放
- `player.interval_seconds`: 两次播放间隔秒数

## 目录结构

```text
work2english-radio/
  README.md
  requirements.txt
  config.example.yaml     # 配置模板（提交到仓库；真实 config.yaml 被 gitignore）
  config.yaml             # 本机真实配置（含 key，不提交）
  run.py / server.py / radio_service.py / feishu_collect.py   # 薄入口
  w2e/                    # 核心包：config / runtime / feishu / llm / study / tts / generate / playback / health / cleanup
  templates/study_table.html   # 学习表 HTML 模板
  prompts/
  inbox/  output/  runtime/  logs/   # 运行时数据（gitignore）
  ui/                     # React 学习中心前端
  tests/                  # pytest 单元测试
```

## 技术栈

- Python 3.10+
- Ollama (qwen3:8b)
- Fish Audio S2.1 Pro Free / edge-tts
- macOS afplay
