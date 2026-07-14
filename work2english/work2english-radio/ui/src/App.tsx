import { useEffect, useRef, useState, type ReactNode } from "react";
import AmbientBackground from "./components/AmbientBackground";
import SystemStatus from "./components/SystemStatus";
import DailyDigestPanel from "./components/DailyDigestPanel";
import StudyTable from "./components/StudyTable";
import PlayerBar from "./components/PlayerBar";
import { useVoiceOS } from "./store/useVoiceOS";

type AppView = "today" | "history";

/**
 * The shell has two user-facing jobs, not two implementation panels:
 * 今日训练 is the guided daily workflow; 学习记录 is the searchable archive.
 */
export default function App() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const init = useVoiceOS((s) => s.init);
  const registerAudio = useVoiceOS((s) => s.registerAudio);
  const togglePlay = useVoiceOS((s) => s.togglePlay);
  const [view, setView] = useState<AppView>("today");

  useEffect(() => {
    registerAudio(audioRef.current);
    return init();
  }, [init, registerAudio]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return;
      if (e.code === "Space") {
        e.preventDefault();
        void togglePlay();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [togglePlay]);

  return (
    <div className="relative min-h-dvh w-full overflow-x-hidden">
      <AmbientBackground />

      <div className="relative z-10 mx-auto flex min-h-dvh w-full max-w-[1520px] flex-col gap-4 px-4 py-4 md:px-6 md:py-6">
        <SystemStatus />

        <div className="flex min-h-0 flex-1 flex-col gap-4">
          <nav
            className="glass-soft flex shrink-0 flex-wrap items-center justify-between gap-3 rounded-2xl px-3 py-2"
            aria-label="主导航"
          >
            <div className="flex items-center gap-1">
              <NavButton active={view === "today"} onClick={() => setView("today")}>
                今日训练
              </NavButton>
              <NavButton active={view === "history"} onClick={() => setView("history")}>
                学习记录
              </NavButton>
            </div>
            <div className="hidden items-center gap-2 text-xs text-haze md:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-status-ok" />
              <span>直接发给飞书机器人也会自动进入学习记录</span>
            </div>
          </nav>

          <main className="min-h-0 flex-1">
            {view === "today" ? <DailyDigestPanel /> : <StudyTable />}
          </main>
        </div>

        <PlayerBar />
      </div>

      <audio ref={audioRef} preload="metadata" hidden />
    </div>
  );
}

function NavButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-4 py-2 text-sm font-semibold transition-colors ${
        active ? "bg-mist text-abyss shadow-sm" : "text-haze hover:bg-white/[0.06] hover:text-mist"
      }`}
    >
      {children}
    </button>
  );
}
