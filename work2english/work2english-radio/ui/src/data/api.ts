import type { DailyPreviewResponse, ServerState } from "../types";

// Thin fetch helpers around the backend (server.py). All same-origin when the
// UI is served by server.py at :8000. In Vite dev mode, vite.config.ts proxies
// /api and /files to :8000 so the same paths work.

const STATE_URL = "/api/state";
const GENERATE_URL = "/api/generate";

export async function fetchState(signal?: AbortSignal): Promise<ServerState> {
  const res = await fetch(STATE_URL, { signal, cache: "no-store" });
  if (!res.ok) throw new Error(`state ${res.status}`);
  return (await res.json()) as ServerState;
}

export async function requestGenerate(): Promise<boolean> {
  const res = await fetch(GENERATE_URL, { method: "POST" });
  if (res.status === 409) return false; // already running
  if (!res.ok) throw new Error(`generate ${res.status}`);
  const data = (await res.json()) as { ok: boolean };
  return data.ok;
}

export async function postTtsSettings(provider: string, voice: string): Promise<boolean> {
  const res = await fetch("/api/tts-settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, voice }),
  });
  if (!res.ok) throw new Error(`tts-settings ${res.status}`);
  const data = (await res.json()) as { ok: boolean };
  return data.ok;
}

export async function requestDailyPreview(options: { date?: string; selectedTexts?: string[] } = {}): Promise<DailyPreviewResponse> {
  const res = await fetch("/api/daily-preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...(options.date ? { date: options.date } : {}),
      ...(options.selectedTexts ? { selected_texts: options.selectedTexts } : {}),
    }),
  });
  const data = (await res.json()) as DailyPreviewResponse;
  if (!res.ok || !data.ok) throw new Error(data.error || `daily-preview ${res.status}`);
  return data;
}

export async function requestDailyCandidates(date?: string): Promise<DailyPreviewResponse> {
  const res = await fetch("/api/daily-candidates", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(date ? { date } : {}),
  });
  const data = (await res.json()) as DailyPreviewResponse;
  if (!res.ok || !data.ok) throw new Error(data.error || `daily-candidates ${res.status}`);
  return data;
}

export async function requestDailyGenerate(): Promise<boolean> {
  const res = await fetch("/api/daily-generate", { method: "POST" });
  if (res.status === 409) return false;
  const data = (await res.json()) as { ok: boolean; error?: string };
  if (!res.ok || !data.ok) throw new Error(data.error || `daily-generate ${res.status}`);
  return data.ok;
}

/** Poll until generation finishes, with a timeout. Returns final state. */
export async function awaitGeneration(
  timeoutMs = 180_000,
): Promise<ServerState> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 1500));
    const s = await fetchState();
    if (!s.generating) return s;
  }
  throw new Error("generation timed out");
}
