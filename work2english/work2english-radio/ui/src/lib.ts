import type { ApiItem } from "./types";

/** Split a spoken-English script into sentences for the live subtitle view. */
export function splitSentences(text: string): string[] {
  const clean = text.replace(/\s+/g, " ").trim();
  if (!clean) return [];
  const parts = clean.match(/[^.!?]+[.!?]*/g) || [clean];
  return parts.map((s) => s.trim()).filter(Boolean);
}

/** Index of the first item in the latest time-group (same HH:MM as the last). */
export function latestBatchStart(items: ApiItem[]): number {
  if (!items.length) return 0;
  const lastTime = items[items.length - 1].time;
  if (!lastTime) return 0;
  for (let i = items.length - 1; i >= 0; i--) {
    if (items[i].time !== lastTime) return Math.min(i + 1, items.length - 1);
  }
  return 0;
}

export function mmss(total: number): string {
  if (!total || !isFinite(total)) return "0:00";
  const m = Math.floor(total / 60);
  const s = Math.round(total % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
