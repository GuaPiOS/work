import { motion, AnimatePresence } from "framer-motion";
import { useVoiceOS } from "../store/useVoiceOS";
import type { ServiceState } from "../types";

/**
 * SystemStatus — top telemetry bar.
 *
 * Each service is a labelled channel with a colour-coded signal dot. When a
 * service isn't healthy, its diagnostic reason shows as a small caption so the
 * user knows exactly what to fix (e.g. "Ollama 未运行：ollama serve").
 */

type ServiceKey = "feishu" | "llm" | "tts" | "player";

const SERVICES: { key: ServiceKey; label: string }[] = [
  { key: "feishu", label: "Feishu" },
  { key: "llm", label: "LLM" },
  { key: "tts", label: "TTS" },
  { key: "player", label: "Player" },
];

const STATE_COLOR: Record<ServiceState, string> = {
  connected: "#34D399",
  processing: "#FBBF24",
  idle: "#6B7390",
  error: "#F87171",
};

const STATE_LABEL: Record<ServiceState, string> = {
  connected: "Connected",
  processing: "Working",
  idle: "Standby",
  error: "Error",
};

function ServiceDot({
  state,
  label,
  reason,
}: {
  state: ServiceState;
  label: string;
  reason: string;
}) {
  const color = STATE_COLOR[state];
  const healthy = state === "connected";
  const showReason = !healthy && reason;
  return (
    <div className="flex items-center gap-2">
      <span className="relative grid place-items-center" style={{ width: 10, height: 10 }}>
        <motion.span
          className="absolute rounded-full"
          style={{ background: color, width: 8, height: 8 }}
          animate={{ opacity: state === "processing" ? [1, 0.3, 1] : 1 }}
          transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
        />
        {healthy && (
          <motion.span
            className="absolute rounded-full"
            style={{ background: color, width: 8, height: 8 }}
            animate={{ scale: [1, 2.2], opacity: [0.5, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
          />
        )}
      </span>
      <div className="flex flex-col leading-none">
        <span className="telemetry">{label}</span>
        <span
          className="font-mono text-[11px] mt-1"
          style={{ color, letterSpacing: "0.02em" }}
        >
          {STATE_LABEL[state]}
        </span>
        <AnimatePresence>
          {showReason && (
            <motion.span
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-1 max-w-[150px] font-mono text-[10px] leading-snug text-status-err/90"
              title={reason}
            >
              {reason}
            </motion.span>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function SystemStatus() {
  const connection = useVoiceOS((s) => s.connectionStatus);
  const diagnostics = useVoiceOS((s) => s.diagnostics);

  return (
    <header className="glass rounded-os flex items-center justify-between gap-6 px-7 py-4">
      <div className="flex shrink-0 items-center gap-3">
        <div
          className="grid h-8 w-8 place-items-center rounded-xl"
          style={{
            background:
              "linear-gradient(135deg, rgba(123,97,255,0.25), rgba(56,189,248,0.18))",
            border: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          <span className="block h-3 w-3 rounded-full bg-gradient-to-br from-plasma to-azure shadow-glow" />
        </div>
        <div className="flex flex-col leading-none">
          <span className="font-display text-[15px] font-semibold tracking-tight text-mist">
            Work2English <span className="text-haze font-light">OS</span>
          </span>
          <span className="telemetry mt-1">Personal study companion · v0.2</span>
        </div>
      </div>

      <div className="flex items-center justify-end gap-6 md:gap-8">
        {SERVICES.map((s) => (
          <ServiceDot
            key={s.key}
            label={s.label}
            state={connection[s.key]}
            reason={diagnostics[s.key] ?? ""}
          />
        ))}
      </div>
    </header>
  );
}
