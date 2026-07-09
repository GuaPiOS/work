import { useEffect, useRef } from "react";
import AmbientBackground from "./components/AmbientBackground";
import SystemStatus from "./components/SystemStatus";
import StudyTable from "./components/StudyTable";
import PlayerBar from "./components/PlayerBar";
import { useVoiceOS } from "./store/useVoiceOS";

/**
 * App — Work2English learning-centered shell.
 *
 *   ┌──────────── top: SystemStatus (real health) ────────────┐
 *   │                  StudyTable (centerpiece)                │
 *   ├──────── bottom: PlayerBar (transport + subtitle) ───────┤
 *
 * The study table is the focus: Chinese original, spoken English, focus phrase
 * and learning note for every item. A hidden <audio> is the real player,
 * driven by the store. Spacebar toggles play/pause.
 */
export default function App() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const init = useVoiceOS((s) => s.init);
  const registerAudio = useVoiceOS((s) => s.registerAudio);
  const togglePlay = useVoiceOS((s) => s.togglePlay);

  useEffect(() => {
    registerAudio(audioRef.current);
    return init();
  }, [init, registerAudio]);

  // Spacebar play/pause — ignored while typing in a form field.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
      if (e.code === "Space") {
        e.preventDefault();
        void togglePlay();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [togglePlay]);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <AmbientBackground />

      <div className="relative z-10 mx-auto flex h-full max-w-[1600px] flex-col gap-4 p-4 md:p-6">
        <SystemStatus />

        <main className="min-h-0 flex-1">
          <StudyTable />
        </main>

        <PlayerBar />
      </div>

      {/* The real player — hidden, controlled entirely by the store */}
      <audio ref={audioRef} preload="metadata" hidden />
    </div>
  );
}
