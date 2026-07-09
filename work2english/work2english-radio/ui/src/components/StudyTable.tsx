import { useVoiceOS } from "../store/useVoiceOS";
import type { ApiItem } from "../types";

/**
 * StudyTable — the centerpiece of the learning-centered UI.
 *
 * Each row shows the Chinese original, the natural spoken English, the focus
 * phrase, and a learning note — exactly the data the old player-only UI threw
 * away. Click any row (or its play button) to play that item; the row currently
 * playing is highlighted.
 */
export default function StudyTable() {
  const items = useVoiceOS((s) => s.items);
  const currentIndex = useVoiceOS((s) => s.currentIndex);
  const status = useVoiceOS((s) => s.status);
  const playItem = useVoiceOS((s) => s.playItem);
  const day = useVoiceOS((s) => s.day);
  const level = useVoiceOS((s) => s.level);
  const dailyBriefing = useVoiceOS((s) => s.dailyBriefing);

  if (!items.length) {
    return (
      <div className="glass flex h-full min-h-[300px] flex-col items-center justify-center gap-3 rounded-os p-10 text-center">
        <div className="telemetry">No content yet</div>
        <p className="max-w-md text-haze">
          Send a Chinese work message to the Feishu bot, or paste content into
          <code className="mx-1 rounded bg-white/5 px-1.5 py-0.5 font-mono text-xs">inbox/feishu_raw.md</code>
          then press Play.
        </p>
      </div>
    );
  }

  const isPlaying = (i: number) => i === currentIndex && (status === "reading" || status === "paused");

  return (
    <section className="glass flex min-h-0 flex-col rounded-os">
      <header className="flex flex-wrap items-end justify-between gap-3 border-b border-white/8 px-6 py-4">
        <div>
          <h2 className="font-display text-lg font-semibold tracking-tight text-mist">
            Study Table <span className="text-haze font-light">· {day}</span>
          </h2>
          <p className="telemetry mt-1">{items.length} items · level {level}</p>
        </div>
        {dailyBriefing && (
          <p className="max-w-[55%] text-sm leading-relaxed text-haze">{dailyBriefing}</p>
        )}
      </header>

      <div className="scroll-os min-h-0 flex-1 overflow-y-auto px-2 py-2">
        <table className="w-full border-collapse">
          <thead className="sticky top-0 z-10">
            <tr className="telemetry text-haze">
              <th className="px-3 py-2 text-left font-medium">#</th>
              <th className="px-3 py-2 text-left font-medium">原文 · Chinese</th>
              <th className="px-3 py-2 text-left font-medium">Spoken English</th>
              <th className="px-3 py-2 text-left font-medium">Focus · Note</th>
              <th className="px-3 py-2 text-left font-medium">Play</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <Row
                key={`${i}-${item.time}-${item.spoken_english.slice(0, 16)}`}
                index={i}
                item={item}
                playing={isPlaying(i)}
                onPlay={() => playItem(i)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Row({
  index,
  item,
  playing,
  onPlay,
}: {
  index: number;
  item: ApiItem;
  playing: boolean;
  onPlay: () => void;
}) {
  return (
    <tr
      onClick={onPlay}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onPlay();
        }
      }}
      role="button"
      aria-label={`Play item ${index + 1}`}
      className={`cursor-pointer border-b border-white/5 align-top transition-colors hover:bg-white/[0.04] focus-visible:bg-white/[0.06] ${
        playing ? "bg-iris/[0.08]" : ""
      }`}
    >
      <td className="px-3 py-3">
        <div className="flex flex-col gap-1">
          <span className={`font-mono text-sm ${playing ? "text-plasma" : "text-haze"}`}>
            {String(index + 1).padStart(2, "0")}
          </span>
          <span className="font-mono text-[10px] text-haze/70">{item.time || "—"}</span>
        </div>
      </td>
      <td className="w-[28%] px-3 py-3 text-[13px] leading-relaxed text-mist/80 whitespace-pre-wrap">
        {item.original_zh || "—"}
      </td>
      <td className={`w-[30%] px-3 py-3 text-[14px] leading-relaxed ${playing ? "text-mist" : "text-mist/90"}`}>
        {item.spoken_english || "—"}
      </td>
      <td className="w-[24%] px-3 py-3">
        {item.focus_phrase && (
          <div className="mb-1 text-[13px] font-semibold text-azure">{item.focus_phrase}</div>
        )}
        {item.note_zh && <div className="text-[12px] leading-relaxed text-haze">{item.note_zh}</div>}
        {!item.focus_phrase && !item.note_zh && <span className="text-haze/50">—</span>}
      </td>
      <td className="px-3 py-3">
        <button
          onClick={(e) => { e.stopPropagation(); onPlay(); }}
          className={`grid h-9 w-9 place-items-center rounded-full transition-all ${
            playing
              ? "bg-iris text-white shadow-glow"
              : "bg-white/5 text-mist/80 hover:bg-white/12"
          }`}
          aria-label={playing ? "Playing" : "Play this item"}
        >
          {playing ? <NowIcon /> : <PlayIcon />}
        </button>
      </td>
    </tr>
  );
}

function PlayIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M8 5v14l11-7z" />
    </svg>
  );
}
function NowIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <rect x="6" y="5" width="4" height="14" rx="1" />
      <rect x="14" y="5" width="4" height="14" rx="1" />
    </svg>
  );
}
