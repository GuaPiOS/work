import { useVoiceOS } from "../store/useVoiceOS";
import { mmss } from "../lib";
import type { PlayerMode } from "../types";

/**
 * PlayerBar — persistent bottom transport + the live English subtitle.
 *
 * Drives the single hidden <audio> via the store. Also hosts the voice
 * selector, the daily/latest mode toggle, and volume. This replaces the old
 * three-column ControlPanel/CurrentReading/ReadingQueue with one coherent bar,
 * freeing the main area for the StudyTable.
 */
export default function PlayerBar() {
  const status = useVoiceOS((s) => s.status);
  const items = useVoiceOS((s) => s.items);
  const currentIndex = useVoiceOS((s) => s.currentIndex);
  const currentSentence = useVoiceOS((s) => s.currentSentence);
  const progress = useVoiceOS((s) => s.progress);
  const total = useVoiceOS((s) => s.total);
  const remaining = useVoiceOS((s) => s.remaining);
  const ambient = useVoiceOS((s) => s.ambientThought);
  const mode = useVoiceOS((s) => s.mode);
  const volume = useVoiceOS((s) => s.volume);

  const togglePlay = useVoiceOS((s) => s.togglePlay);
  const stop = useVoiceOS((s) => s.stop);
  const next = useVoiceOS((s) => s.next);
  const prev = useVoiceOS((s) => s.prev);
  const setMode = useVoiceOS((s) => s.setMode);
  const setVolume = useVoiceOS((s) => s.setVolume);

  const item = items[currentIndex];
  const playing = status === "reading";

  return (
    <footer className="glass sticky bottom-4 z-20 rounded-2xl px-4 py-3 md:px-5">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
        {/* transport */}
        <div className="flex items-center gap-2">
          <IconBtn label="Previous" onClick={prev} disabled={!items.length}>
            <PrevIcon />
          </IconBtn>
          <button
            onClick={togglePlay}
            disabled={status === "loading"}
            className="grid h-12 w-12 place-items-center rounded-full bg-gradient-to-br from-plasma to-iris text-white shadow-glow transition-transform hover:scale-105 disabled:opacity-50"
            aria-label={playing ? "Pause" : "Play"}
          >
            {status === "loading" ? <Spinner /> : playing ? <PauseIcon /> : <PlayIcon />}
          </button>
          <IconBtn label="Stop" onClick={stop} disabled={!items.length || status === "idle"}>
            <StopIcon />
          </IconBtn>
          <IconBtn label="Next" onClick={next} disabled={!items.length}>
            <NextIcon />
          </IconBtn>
        </div>

        {/* now playing + subtitle */}
        <div className="min-w-[220px] flex-1">
          <div className="telemetry mb-1">
            {item ? `第 ${currentIndex + 1} 条 · ${item.time || "即时内容"}` : "还没有正在播放的内容"}
            {item && <span className="ml-2 text-haze/60">剩余 {mmss(remaining)}</span>}
          </div>
          <p className={`text-[15px] leading-snug ${item ? "text-mist" : "text-haze"}`}>
            {status === "reading" ? currentSentence : translateAmbient(ambient)}
          </p>
          {/* progress */}
          <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-white/8">
            <div
              className="h-full rounded-full bg-gradient-to-r from-plasma to-azure transition-[width] duration-200"
              style={{ width: `${Math.round(progress * 100)}%` }}
            />
          </div>
        </div>

        {/* mode + voice + volume */}
        <div className="flex items-center gap-4">
          <ModeToggle mode={mode} onChange={setMode} />
          <VoiceSelector />
          <Volume volume={volume} onChange={setVolume} />
        </div>
      </div>
      <div className="sr-only" aria-live="polite">{total ? `总时长 ${mmss(total)}` : ""}</div>
    </footer>
  );
}

function IconBtn({
  children, label, onClick, disabled,
}: { children: React.ReactNode; label: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      className="grid h-10 w-10 place-items-center rounded-full bg-white/5 text-mist/80 transition-colors hover:bg-white/12 disabled:opacity-30"
    >
      {children}
    </button>
  );
}

function ModeToggle({ mode, onChange }: { mode: PlayerMode; onChange: (m: PlayerMode) => void }) {
  return (
    <div className="flex items-center gap-1 rounded-full bg-white/5 p-1" role="group" aria-label="Playback mode">
      <ModeBtn active={mode === "daily"} onClick={() => onChange("daily")}>今天</ModeBtn>
      <ModeBtn active={mode === "auto"} onClick={() => onChange("auto")}>最新</ModeBtn>
    </div>
  );
}

function translateAmbient(text: string): string {
  const translations: Record<string, string> = {
    "Synthesizing spoken English…": "正在生成英文音频…",
    "Reading your work briefing aloud.": "正在朗读你的工作内容。",
    "Paused. Your place is held.": "已暂停，会从当前位置继续。",
    "Preparing audio…": "正在准备音频…",
    "No audio yet — send a Feishu message or press Play.": "还没有音频，可以发送飞书消息或开始今日训练。",
    "New content arrived. Press Play to refresh.": "有新的内容，点击播放即可更新。",
    "Ready.": "已经准备好。",
  };
  return translations[text] ?? text;
}
function ModeBtn({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
        active ? "bg-white/15 text-mist" : "text-haze hover:text-mist"
      }`}
    >
      {children}
    </button>
  );
}

function VoiceSelector() {
  const tts = useVoiceOS((s) => s.tts);
  const setTts = useVoiceOS((s) => s.setTts);
  const providerId = tts.current.provider;
  const voices = tts.voices[providerId] ?? [];
  const sel = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const [p, v] = e.target.value.split("|");
    if (v) void setTts(p, v);
  };
  return (
    <select
      aria-label="Voice"
      value={`${providerId}|${tts.current.voice}`}
      onChange={sel}
      className="max-w-[180px] truncate rounded-full bg-white/5 px-3 py-2 text-xs text-mist outline-none hover:bg-white/10"
    >
      {tts.providers.map((p) =>
        (tts.voices[p.id] ?? []).map((v) => (
          <option key={`${p.id}-${v.id}`} value={`${p.id}|${v.id}`} className="bg-abyss text-mist">
            {p.name} · {v.name}
          </option>
        )),
      )}
      {voices.length === 0 && <option>{providerId}</option>}
    </select>
  );
}

function Volume({ volume, onChange }: { volume: number; onChange: (v: number) => void }) {
  return (
    <div className="flex items-center gap-2" aria-label="Volume">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-haze" aria-hidden>
        <path d="M3 9v6h4l5 5V4L7 9H3z" />
      </svg>
      <input
        type="range" min={0} max={1} step={0.01} value={volume}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="h-1 w-20 cursor-pointer accent-iris"
        aria-label="Volume"
      />
    </div>
  );
}

function PlayIcon() { return <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden><path d="M8 5v14l11-7z" /></svg>; }
function PauseIcon() { return <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden><rect x="6" y="5" width="4" height="14" rx="1" /><rect x="14" y="5" width="4" height="14" rx="1" /></svg>; }
function StopIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden><rect x="6" y="6" width="12" height="12" rx="1.5" /></svg>; }
function PrevIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden><path d="M7 5v14h2V5H7zm3 7l9 7V5l-9 7z" /></svg>; }
function NextIcon() { return <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden><path d="M15 5v14h2V5h-2zM6 5v14l9-7-9-7z" /></svg>; }
function Spinner() { return <svg width="18" height="18" viewBox="0 0 24 24" className="animate-spin" aria-hidden><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="42" opacity="0.3" /><path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" fill="none" strokeLinecap="round" /></svg>; }
