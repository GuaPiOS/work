# Work2English OS — UI

The interactive interface for Work2English Radio: a futuristic, ambient
**Personal Voice OS** dashboard. Built with React + TypeScript + Tailwind +
Framer Motion + Zustand.

**Phase 2 — wired to the real backend.** The UI plays the actual TTS audio that
`run.py` generates, shows the real study queue from `study.json`, reports real
connection status (Ollama / edge-tts), and triggers regeneration on Start when
the inbox has new content. `run.py` itself is unchanged — the CLI still works.

## Run it (production — one command)

```bash
# 1. Build the UI once (and after any UI code change)
cd ui
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy   # if npm hits a proxy wall
npm install
npm run build

# 2. Start the bridge server (serves UI + API + audio on one port)
cd ..
python3 server.py
```

Open **http://localhost:8000**. The server serves the built UI at `/`, the
generated audio/data under `/files/`, and the JSON API under `/api/`.

> If `npm run build` errors with `EPERM ... rmdir dist` on the iCloud folder,
> run `npx vite build --emptyOutDir false`. That is an iCloud-mount quirk.

## Run it (dev — hot reload)

Two terminals:

```bash
# T1: backend
python3 server.py                 # :8000

# T2: Vite dev server with API proxy
cd ui && npm run dev              # :5173  (proxies /api and /files to :8000)
```

Open **http://localhost:5173**.

## What it does

Click **Start**. If audio already exists and the inbox hasn't changed, it plays
immediately. If the inbox is new/changed, Start triggers a real generation
(Ollama rewrite → edge-tts MP3s) then plays. The Voice Core lights up, progress
tracks the real audio, the teleprompter sentence advances with playback, and the
queue auto-advances item by item. **Pause** holds your place. **Stop** resets.

## Backend API (`server.py`)

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Built UI (SPA) |
| `/files/...` | GET | Generated audio + `study.json` (byte-range supported) |
| `/api/state` | GET | Real `study.json` items + health + stale flag |
| `/api/generate` | POST | Triggers `run.generate_if_needed` in a background thread |

`server.py` is stdlib-only (no new Python deps) and imports `run` as a module,
so generation logic is shared, not duplicated.

## Architecture

```
src/
  types.ts              VoiceOSState + ServerState contracts
  data/api.ts           fetch helpers (state + generate + awaitGeneration)
  store/useVoiceOS.ts   Zustand store; drives a real <audio> element
  components/
    AmbientBackground / SystemStatus / ControlPanel
    VoiceCore (signature) / CurrentReading / ReadingQueue / AIStatusBar
  App.tsx               dashboard shell + hidden <audio> player
```

### Design tokens

| Token | Hex | Role |
|---|---|---|
| void | `#05060B` | page base |
| abyss | `#0A0D18` | lifted surface |
| iris | `#7B61FF` | primary violet (the AI's voice) |
| azure | `#38BDF8` | connected / active signal |
| plasma | `#C084FC` | halo / glow |
| mist | `#E6E8F0` | foreground text |
| haze | `#6B7390` | muted secondary |

Faces: **Space Grotesk** (display/UI) + **JetBrains Mono** (telemetry).

