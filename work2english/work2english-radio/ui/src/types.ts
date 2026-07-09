// Work2English OS — shared state contract with the backend (server.py /api/state).

export type VoiceStatus = "idle" | "loading" | "reading" | "paused" | "error";

/** daily = all of today's items; auto = only the latest batch (last time group). */
export type PlayerMode = "daily" | "auto";

export interface PlayerItem {
  audioUrl: string;
  message_id: string;
  text: string;
}

export interface PlayerControl {
  mode: string;
  loop: boolean;
  signature: string;
  updated_at: number;
  playlist: PlayerItem[];
}

export type ServiceState = "connected" | "processing" | "error" | "idle";

export interface ConnectionStatus {
  feishu: ServiceState;
  llm: ServiceState;
  tts: ServiceState;
  player: ServiceState;
}

/** One row of the study table — the core learning data the UI is built around. */
export interface ApiItem {
  time: string;
  source: string;
  original_zh: string;
  spoken_english: string;
  focus_phrase: string;
  note_zh: string;
  audioUrl: string;
}

export interface ServerState {
  day: string;
  level: string;
  voice: string;
  daily_briefing: string;
  items: ApiItem[];
  hasAudio: boolean;
  stale: boolean;
  generating: boolean;
  last_error: string | null;
  connectionStatus: ConnectionStatus;
  tts: TtsOptions;
  player_control: PlayerControl;
  diagnostics: { feishu: string; llm: string; tts: string; player: string };
}

export interface TtsProvider {
  id: string;
  name: string;
  free: boolean;
  configured: boolean;
  endpoint?: string;
}

export interface TtsVoice {
  id: string;
  name: string;
}

export interface TtsOptions {
  current: { provider: string; voice: string };
  providers: TtsProvider[];
  voices: Record<string, TtsVoice[]>;
}
