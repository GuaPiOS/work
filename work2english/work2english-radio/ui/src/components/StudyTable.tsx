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
      <div className="glass flex min-h-[520px] flex-col items-center justify-center gap-3 rounded-2xl p-10 text-center">
        <div className="text-xs font-semibold tracking-wide text-iris">学习记录</div>
        <h2 className="font-display text-2xl font-semibold text-mist">还没有学习内容</h2>
        <p className="max-w-md text-sm leading-relaxed text-haze">
          你可以从“今日训练”开始，或者直接给飞书机器人发送一句中文工作内容。生成后的英文会自动出现在这里。
        </p>
      </div>
    );
  }

  const isPlaying = (i: number) => i === currentIndex && (status === "reading" || status === "paused");

  return (
    <section className="glass flex min-h-[520px] flex-col rounded-2xl">
      <header className="shrink-0 border-b border-white/8 px-5 py-4 md:px-7 md:py-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
          <div className="text-xs font-semibold tracking-wide text-iris">学习记录</div>
          <h2 className="mt-1.5 font-display text-xl font-semibold tracking-tight text-mist md:text-2xl">
            你的英语内容
          </h2>
          <p className="mt-1 text-sm text-haze">{day || "今天"} · 共 {items.length} 条 · 难度 {level} → B1</p>
          </div>
          <span className="rounded-full bg-white/[0.05] px-3 py-1.5 text-xs text-haze">点击一行即可播放</span>
        </div>
        {dailyBriefing && (
          <details className="group mt-3 rounded-xl border border-white/8 bg-white/[0.025]">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-3 py-2.5 text-sm text-haze hover:text-mist">
              <span className="font-medium">今日摘要</span>
              <span className="text-xs text-haze/70 transition-transform group-open:rotate-180">⌄</span>
            </summary>
            <p className="border-t border-white/8 px-3 py-3 text-sm leading-relaxed text-haze">{dailyBriefing}</p>
          </details>
        )}
      </header>

      <div className="min-h-0 flex-1 px-3 py-3 md:px-5">
        <div className="scroll-os max-h-[calc(100dvh-285px)] min-h-[390px] overflow-auto rounded-xl border border-white/8 bg-white/[0.018]">
          <table className="w-full min-w-[880px] border-collapse">
          <thead className="sticky top-0 z-10">
            <tr className="bg-abyss/95 text-xs text-haze backdrop-blur">
              <th className="px-3 py-2 text-left font-medium">#</th>
              <th className="px-3 py-2 text-left font-medium">中文原文</th>
              <th className="px-3 py-2 text-left font-medium">口语英文</th>
              <th className="px-3 py-2 text-left font-medium">常用句型 · 简单提示</th>
              <th className="px-3 py-2 text-left font-medium">播放</th>
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
        <p className="mt-2 text-center text-xs text-haze/70 md:hidden">左右滑动查看完整内容</p>
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
