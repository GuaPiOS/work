import { create } from "zustand";
import type {
  ApiItem,
  ConnectionStatus,
  PlayerMode,
  ServerState,
  ServiceState,
  TtsOptions,
  VoiceStatus,
} from "../types";
import { awaitGeneration, fetchState, postTtsSettings, requestGenerate } from "../data/api";
import { latestBatchStart, splitSentences } from "../lib";

// ─────────────────────────────────────────────────────────────────────────────
// Voice OS store — items-driven.
//
// The study table (items[]) is the source of truth for playback: the UI walks
// items in order, looping. New content is detected via player_control.signature;
// it does not auto-play while idle (the user presses Play), but if content
// arrives mid-playback it is queued and applied at the current item's boundary.
// ─────────────────────────────────────────────────────────────────────────────

const POLL_MS = 4000;

type Diagnostics = { feishu: string; llm: string; tts: string; player: string };

interface VoiceOSStore {
  status: VoiceStatus;
  connectionStatus: ConnectionStatus;
  diagnostics: Diagnostics;
  items: ApiItem[];
  dailyBriefing: string;
  currentIndex: number; // index into items[]
  mode: PlayerMode; // daily | auto(latest)
  tts: TtsOptions;
  day: string;
  level: string;
  voice: string;
  volume: number;
  progress: number; // 0..1 of current item
  currentSentence: string;
  remaining: number;
  total: number;
  ambientThought: string;
  stale: boolean;
  generating: boolean;
  backendError: string | null;
  ready: boolean;

  init: () => () => void;
  registerAudio: (el: HTMLAudioElement | null) => void;
  togglePlay: () => Promise<void>;
  pause: () => void;
  resume: () => Promise<void>;
  stop: () => void;
  next: () => void;
  prev: () => void;
  playItem: (index: number) => void;
  setMode: (mode: PlayerMode) => Promise<void>;
  setTts: (provider: string, voice: string) => Promise<void>;
  setVolume: (v: number) => void;
}

// The <audio> element is a DOM handle, not React state. Kept module-scoped.
let audioEl: HTMLAudioElement | null = null;
let lastSignature = "";
let pendingSwitch = false; // new content arrived mid-playback; apply at boundary

const EMPTY_CONNECTION: ConnectionStatus = { feishu: "idle", llm: "idle", tts: "idle", player: "idle" };
const EMPTY_DIAG: Diagnostics = { feishu: "", llm: "", tts: "", player: "" };
const EMPTY_TTS: TtsOptions = {
  current: { provider: "edge-tts", voice: "en-US-AriaNeural" },
  providers: [],
  voices: {},
};

function ambientFor(status: VoiceStatus, s: ServerState): string {
  if (s.generating) return "Synthesizing spoken English…";
  if (status === "reading") return "Reading your work briefing aloud.";
  if (status === "paused") return "Paused. Your place is held.";
  if (status === "loading") return "Preparing audio…";
  if (!s.items?.length) return "No audio yet — send a Feishu message or press Play.";
  if (s.stale) return "New content arrived. Press Play to refresh.";
  return "Ready.";
}

export const useVoiceOS = create<VoiceOSStore>((set, get) => {
  const applyVolume = () => {
    if (audioEl) audioEl.volume = get().volume;
  };

  const loadIndex = async (i: number, autoplay: boolean) => {
    const items = get().items;
    if (!items.length) return;
    const idx = ((i % items.length) + items.length) % items.length;
    const item = items[idx];
    set({
      currentIndex: idx,
      progress: 0,
      currentSentence: splitSentences(item.spoken_english)[0] || item.spoken_english,
      remaining: 0,
      total: 0,
    });
    if (audioEl && item.audioUrl) {
      audioEl.src = item.audioUrl;
      audioEl.load();
      applyVolume();
      if (autoplay) {
        try { await audioEl.play(); } catch { /* autoplay may need a gesture */ }
      }
    }
  };

  const beginPlaying = async (i = 0) => {
    set((s) => ({
      status: "reading",
      ambientThought: "Reading your work briefing aloud.",
      connectionStatus: { ...s.connectionStatus, player: "connected" as ServiceState },
    }));
    await loadIndex(i, true);
  };

  const hydrate = (s: ServerState) => {
    const sig = s.player_control?.signature ?? "";
    const playing = get().status === "reading" || get().status === "paused";
    const isNew = !!sig && sig !== lastSignature;
    if (sig) lastSignature = sig;

    const itemsChanged =
      !get().ready ||
      get().items.length !== (s.items?.length ?? 0) ||
      (s.items?.length && s.items[0]?.spoken_english !== get().items[0]?.spoken_english);

    if (isNew && s.items?.length) {
      const startIdx = get().mode === "auto" ? latestBatchStart(s.items) : 0;
      if (playing) {
        pendingSwitch = true;
        set({
          items: s.items,
          dailyBriefing: s.daily_briefing,
          day: s.day, level: s.level, voice: s.voice, stale: s.stale,
          generating: s.generating, backendError: s.last_error,
          connectionStatus: s.connectionStatus, diagnostics: s.diagnostics ?? EMPTY_DIAG,
          tts: s.tts ?? get().tts, ready: true,
          ambientThought: "New content ready — plays after the current item.",
        });
        return;
      }
      set({
        items: s.items,
        dailyBriefing: s.daily_briefing,
        currentIndex: itemsChanged ? startIdx : get().currentIndex,
        day: s.day, level: s.level, voice: s.voice, stale: s.stale,
        generating: s.generating, backendError: s.last_error,
        connectionStatus: s.connectionStatus, diagnostics: s.diagnostics ?? EMPTY_DIAG,
        tts: s.tts ?? get().tts, ready: true,
        ambientThought: "New content ready — press Play.",
      });
      return;
    }

    set({
      items: s.items ?? get().items,
      dailyBriefing: s.daily_briefing,
      day: s.day, level: s.level, voice: s.voice, stale: s.stale,
      generating: s.generating, backendError: s.last_error,
      connectionStatus: s.connectionStatus, diagnostics: s.diagnostics ?? EMPTY_DIAG,
      tts: s.tts ?? get().tts, ready: true,
      ambientThought: ambientFor(get().status, s),
    });
  };

  return {
    status: "idle",
    connectionStatus: EMPTY_CONNECTION,
    diagnostics: EMPTY_DIAG,
    items: [],
    dailyBriefing: "",
    currentIndex: 0,
    mode: "daily",
    tts: EMPTY_TTS,
    day: "", level: "A2", voice: "",
    volume: 1,
    progress: 0, currentSentence: "—", remaining: 0, total: 0,
    ambientThought: "Connecting to your work feed…",
    stale: false, generating: false, backendError: null, ready: false,

    init: () => {
      let cancelled = false;
      const load = async () => {
        try {
          const s = await fetchState();
          if (!cancelled) hydrate(s);
        } catch {
          if (!cancelled) {
            set({
              ready: true, status: "error",
              ambientThought: "Can't reach the local server. Is server.py running?",
              connectionStatus: EMPTY_CONNECTION,
              diagnostics: { ...EMPTY_DIAG, llm: "无法连接本地服务，请确认 server.py 正在运行。" },
            });
          }
        }
      };
      load();
      const interval = setInterval(load, POLL_MS);
      return () => { cancelled = true; clearInterval(interval); };
    },

    registerAudio: (el) => {
      audioEl = el;
      if (!el) return;
      applyVolume();
      el.ontimeupdate = () => {
        const { status, currentIndex, items } = get();
        if (status !== "reading" || !el.duration || !isFinite(el.duration)) return;
        const item = items[currentIndex];
        if (!item) return;
        const progress = Math.min(1, el.currentTime / el.duration);
        const sentences = splitSentences(item.spoken_english);
        const sentenceIdx = Math.min(Math.max(0, sentences.length - 1), Math.floor(progress * sentences.length));
        set({
          progress,
          currentSentence: sentences[sentenceIdx] || get().currentSentence,
          remaining: Math.max(0, el.duration - el.currentTime),
          total: el.duration,
        });
      };
      el.onloadedmetadata = () => {
        if (el.duration && isFinite(el.duration)) set({ total: el.duration, remaining: el.duration });
      };
      el.onended = () => {
        if (pendingSwitch) {
          pendingSwitch = false;
          const items = get().items;
          const start = get().mode === "auto" ? latestBatchStart(items) : 0;
          void loadIndex(start, true);
          return;
        }
        const next = get().currentIndex + 1 >= get().items.length ? 0 : get().currentIndex + 1;
        void loadIndex(next, true);
      };
      el.onerror = () => {
        set((s) => ({
          status: "error",
          ambientThought: "Audio playback failed.",
          connectionStatus: { ...s.connectionStatus, player: "error" as ServiceState },
        }));
      };
    },

    togglePlay: async () => {
      const state = get();
      if (state.status === "reading") { get().pause(); return; }
      if (state.status === "paused") { await get().resume(); return; }
      if (state.status === "loading") return;

      const needsGen = !state.items.length || state.stale || state.generating;
      if (needsGen) {
        set((s) => ({
          status: "loading",
          ambientThought: state.stale ? "New content detected. Regenerating…" : "Synthesizing spoken English…",
          connectionStatus: { ...s.connectionStatus, llm: "processing", tts: "processing", player: "processing" },
        }));
        try {
          await requestGenerate();
          const fresh = await awaitGeneration();
          hydrate(fresh);
          if (fresh.items?.length) await beginPlaying(get().mode === "auto" ? latestBatchStart(fresh.items) : 0);
        } catch (e) {
          set((s) => ({
            status: "error",
            ambientThought: "Generation failed. Check that Ollama is running.",
            backendError: e instanceof Error ? e.message : String(e),
            connectionStatus: { ...s.connectionStatus, llm: "error" },
          }));
        }
        return;
      }
      await beginPlaying(get().currentIndex || 0);
    },

    pause: () => {
      if (get().status !== "reading") return;
      audioEl?.pause();
      set((s) => ({
        status: "paused",
        ambientThought: "Paused. Your place is held.",
        connectionStatus: { ...s.connectionStatus, player: "idle" as ServiceState },
      }));
    },

    resume: async () => {
      if (get().status !== "paused") return;
      set((s) => ({
        status: "reading",
        ambientThought: "Resuming your briefing.",
        connectionStatus: { ...s.connectionStatus, player: "connected" as ServiceState },
      }));
      try { await audioEl?.play(); } catch { /* ignore */ }
    },

    stop: () => {
      if (audioEl) { audioEl.pause(); audioEl.currentTime = 0; }
      pendingSwitch = false;
      set((s) => ({
        status: "idle",
        currentIndex: 0,
        progress: 0,
        ambientThought: "Stopped. Awaiting signal.",
        connectionStatus: { ...s.connectionStatus, player: "idle" as ServiceState },
      }));
    },

    next: () => {
      const i = get().currentIndex + 1 >= get().items.length ? 0 : get().currentIndex + 1;
      void loadIndex(i, get().status === "reading" || get().status === "paused");
    },

    prev: () => {
      const i = get().currentIndex <= 0 ? get().items.length - 1 : get().currentIndex - 1;
      void loadIndex(i, get().status === "reading" || get().status === "paused");
    },

    playItem: (index) => {
      pendingSwitch = false;
      void beginPlaying(index);
    },

    setMode: async (mode) => {
      set({ mode, ambientThought: `Mode: ${mode === "daily" ? "today's set" : "latest only"}…` });
      try {
        const res = await fetch("/api/player-mode", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mode }),
        });
        if (!res.ok) throw new Error(`player-mode ${res.status}`);
        lastSignature = ""; // let next poll re-sync without double-trigger
      } catch (e) {
        set({ ambientThought: "Mode switch failed.", backendError: e instanceof Error ? e.message : String(e) });
      }
    },

    setTts: async (provider, voice) => {
      set((s) => ({
        tts: { ...s.tts, current: { provider, voice } },
        status: s.status === "idle" ? "loading" : s.status,
        ambientThought: "Switching voice — regenerating audio…",
      }));
      try {
        await postTtsSettings(provider, voice);
        await requestGenerate();
        const fresh = await awaitGeneration();
        hydrate(fresh);
      } catch (e) {
        set({
          status: "error",
          ambientThought: "Voice switch failed. Check key / voice id.",
          backendError: e instanceof Error ? e.message : String(e),
        });
      }
    },

    setVolume: (v) => {
      const vol = Math.max(0, Math.min(1, v));
      if (audioEl) audioEl.volume = vol;
      set({ volume: vol });
    },
  };
});
