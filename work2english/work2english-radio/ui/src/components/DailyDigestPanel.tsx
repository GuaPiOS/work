import { useEffect, useRef, useState, type ReactNode } from "react";
import { awaitGeneration, requestDailyCandidates, requestDailyGenerate, requestDailyPreview } from "../data/api";
import type { ApiItem, DailyCandidate, DailyPreviewResponse } from "../types";
import { useVoiceOS } from "../store/useVoiceOS";

type PanelStatus = "idle" | "fetching" | "ready" | "generating" | "error";
type ActiveTab = "candidates" | "preview";

export default function DailyDigestPanel() {
  const [status, setStatus] = useState<PanelStatus>("idle");
  const [activeTab, setActiveTab] = useState<ActiveTab>("candidates");
  const [preview, setPreview] = useState<DailyPreviewResponse | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [error, setError] = useState("");
  const didAutoLoad = useRef(false);
  const refresh = useVoiceOS((s) => s.refresh);
  const autoPreview = useVoiceOS((s) => s.dailyPreview);

  useEffect(() => {
    if (autoPreview && !preview) {
      setPreview(autoPreview);
      setSelectedIds(defaultSelectedIds(autoPreview.candidates ?? []));
      setStatus("ready");
    }
  }, [autoPreview, preview]);

  const runPreview = async () => {
    setStatus("fetching");
    setError("");
    try {
      const data = await requestDailyCandidates();
      setPreview(data);
      setSelectedIds(defaultSelectedIds(data.candidates ?? []));
      setActiveTab("candidates");
      setStatus("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("error");
    }
  };

  useEffect(() => {
    if (autoPreview || didAutoLoad.current) return;
    didAutoLoad.current = true;
    void runPreview();
  }, [autoPreview]);

  const rerunSelectedPreview = async () => {
    const selectedTexts = selectedCandidateTexts(preview?.candidates ?? [], selectedIds);
    if (!selectedTexts.length) {
      setError("请至少选择一条候选内容。");
      return;
    }
    setStatus("fetching");
    setError("");
    try {
      const data = await requestDailyPreview({ selectedTexts });
      setPreview({ ...preview, ...data, candidates: preview?.candidates ?? [] });
      setActiveTab("preview");
      setStatus("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("error");
    }
  };

  const generateAudio = async () => {
    setStatus("generating");
    setError("");
    try {
      await requestDailyGenerate();
      await awaitGeneration();
      await refresh();
      setStatus("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("error");
    }
  };

  const busy = status === "fetching" || status === "generating";
  const counts = preview?.counts ?? {};
  const items = preview?.items ?? [];
  const candidates = preview?.candidates ?? [];
  const selectedCount = selectedIds.length;

  return (
    <section className="glass flex min-h-[520px] flex-col rounded-2xl">
      <div className="shrink-0 border-b border-white/8 px-5 py-4 md:px-7 md:py-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs font-semibold tracking-wide text-iris">TODAY · {new Date().toLocaleDateString("zh-CN", { month: "long", day: "numeric" })}</div>
            <h2 className="mt-2 font-display text-2xl font-semibold tracking-tight text-mist">
              今天练什么？
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-haze">
              系统已经从今天的飞书内容里筛选工作信息。确认推荐内容后，就可以生成英文并开始播放。
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {preview?.updated_at && <InfoPill>更新于 {preview.updated_at.slice(11, 16)}</InfoPill>}
            {!!candidates.length && <InfoPill>已选 {selectedCount}/{candidates.length}</InfoPill>}
            {Object.entries(counts).map(([key, value]) => (
              <InfoPill key={key}>{sourceLabel(key)} {value}</InfoPill>
            ))}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex rounded-xl bg-white/[0.04] p-1">
            <TabButton
              active={activeTab === "candidates"}
              onClick={() => setActiveTab("candidates")}
              label="选择内容"
              meta={candidates.length ? `${candidates.length} 条` : "未拉取"}
            />
            <TabButton
              active={activeTab === "preview"}
              onClick={() => setActiveTab("preview")}
              label="英文稿"
              meta={items.length ? `${items.length} 条` : "待生成"}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {activeTab === "candidates" ? (
              <>
                <button
                  onClick={runPreview}
                  disabled={busy}
                  className="rounded-lg bg-white/10 px-4 py-2 text-sm font-semibold text-mist transition hover:bg-white/15 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    {status === "fetching" ? "正在准备…" : candidates.length ? "重新同步" : "准备今天内容"}
                </button>
                <button
                  onClick={rerunSelectedPreview}
                  disabled={busy || !candidates.length || !selectedCount}
                  className="rounded-lg bg-iris px-4 py-2 text-sm font-semibold text-white shadow-glow transition hover:bg-iris/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  生成英文稿
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setActiveTab("candidates")}
                  disabled={busy}
                  className="rounded-lg bg-white/10 px-4 py-2 text-sm font-semibold text-mist transition hover:bg-white/15 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  返回选择
                </button>
                <button
                  onClick={generateAudio}
                  disabled={busy || !items.length}
                  className="rounded-lg bg-iris px-4 py-2 text-sm font-semibold text-white shadow-glow transition hover:bg-iris/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {status === "generating" ? "正在生成…" : "开始播放"}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {(error || preview?.preview_error) && (
        <div className="mx-6 mt-4 shrink-0 rounded-lg border border-status-err/30 bg-status-err/10 px-4 py-3 text-sm text-status-err">
          {error || preview?.preview_error}
        </div>
      )}

      {!!preview?.issues?.length && (
        <div className="mx-6 mt-4 shrink-0 rounded-lg border border-status-warn/30 bg-status-warn/10 px-4 py-3 text-sm text-status-warn">
          {preview.issues.map((issue) => `${issue.source}: ${issue.error}`).join(" · ")}
        </div>
      )}

      <div className="min-h-0 flex-1 px-6 py-4">
        {activeTab === "candidates" ? (
          <div className="flex h-full min-h-0 flex-col gap-3">
            <div className="flex shrink-0 items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-mist">选择今天要练的内容</div>
                <p className="mt-1 text-xs text-haze">系统默认选中最适合练习的 3 条，你也可以取消或换成其他内容。</p>
              </div>
              {candidates.length > 0 && <span className="text-xs text-haze">最多选择 3 条</span>}
            </div>

            <div className="scroll-os min-h-0 flex-1 overflow-y-auto pr-1">
              {candidates.length ? (
                <div className="grid gap-2 lg:grid-cols-2 2xl:grid-cols-3">
                  {candidates.map((candidate) => (
                    <CandidateRow
                      key={candidate.id}
                      candidate={candidate}
                      selected={selectedIds.includes(candidate.id)}
                      onToggle={() => {
                        setSelectedIds((prev) => (
                          prev.includes(candidate.id)
                            ? prev.filter((id) => id !== candidate.id)
                            : [...prev, candidate.id].slice(0, 3)
                        ));
                      }}
                    />
                  ))}
                </div>
              ) : (
                <EmptyTab
                  title="今天的内容还没准备好"
                  body="点击“准备今天内容”，系统会自动从飞书里筛选适合练习的工作内容。"
                />
              )}
            </div>
          </div>
        ) : (
          <div className="flex h-full min-h-0 flex-col gap-3">
            <div className="flex shrink-0 items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-mist">英文稿</div>
                <p className="mt-1 text-xs text-haze">每条内容包含中文原文、口语英文、常用句型和简单提示。</p>
              </div>
              {items.length > 0 && <span className="text-xs text-haze">难度 A2 → B1</span>}
            </div>

            <div className="scroll-os min-h-0 flex-1 overflow-y-auto pr-1">
              {items.length ? (
                <div className="grid gap-3 xl:grid-cols-3">
                  {items.map((item, index) => (
                    <PreviewCard key={`${index}-${item.spoken_english.slice(0, 16)}`} item={item} index={index} />
                  ))}
                </div>
              ) : (
                <EmptyTab
                  title="还没有英文稿"
                  body="先在“选择内容”里确认 1～3 条，再点击“生成英文稿”。本地模型失败时，我们会明确告诉你。"
                />
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function TabButton({
  active,
  onClick,
  label,
  meta,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  meta: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg px-4 py-2 text-left transition ${
        active ? "bg-white/[0.12] text-mist shadow-sm" : "text-haze hover:bg-white/[0.06] hover:text-mist"
      }`}
    >
      <div className="text-sm font-semibold">{label}</div>
      <div className="mt-0.5 font-mono text-[10px] opacity-70">{meta}</div>
    </button>
  );
}

function InfoPill({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-md bg-white/5 px-2.5 py-1 font-mono text-xs text-haze">
      {children}
    </span>
  );
}

function sourceLabel(key: string): string {
  const labels: Record<string, string> = {
    messages: "消息",
    calendar: "日程",
    tasks: "任务",
  };
  return labels[key] ?? key;
}

function EmptyTab({ title, body }: { title: string; body: string }) {
  return (
    <div className="grid h-full min-h-[180px] place-items-center rounded-xl border border-dashed border-white/10 bg-white/[0.025] p-8 text-center">
      <div>
        <div className="font-display text-base font-semibold text-mist">{title}</div>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-haze">{body}</p>
      </div>
    </div>
  );
}

function defaultSelectedIds(candidates: DailyCandidate[]): string[] {
  const recommended = candidates.filter((candidate) => candidate.recommended).map((candidate) => candidate.id);
  return recommended.length ? recommended.slice(0, 3) : candidates.slice(0, 3).map((candidate) => candidate.id);
}

function selectedCandidateTexts(candidates: DailyCandidate[], selectedIds: string[]): string[] {
  const selected = new Set(selectedIds);
  return candidates
    .filter((candidate) => selected.has(candidate.id))
    .map((candidate) => candidate.text)
    .filter(Boolean)
    .slice(0, 3);
}

function CandidateRow({
  candidate,
  selected,
  onToggle,
}: {
  candidate: DailyCandidate;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={`rounded-lg border px-3 py-3 text-left transition ${
        selected
          ? "border-iris/70 bg-iris/12"
          : "border-white/8 bg-white/[0.035] hover:border-white/18 hover:bg-white/[0.06]"
      }`}
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <div className="flex flex-wrap gap-1.5">
          {candidate.tags.map((tag) => (
            <span key={tag} className="rounded-md bg-white/8 px-2 py-0.5 text-[11px] text-haze">
              {tag}
            </span>
          ))}
        </div>
        <div className={`rounded-full px-2 py-0.5 text-[11px] ${selected ? "bg-iris text-white" : "bg-white/8 text-haze"}`}>
          {selected ? "已选" : candidate.recommended ? "推荐" : "可选"}
        </div>
      </div>
      <p className="line-clamp-3 text-sm leading-relaxed text-mist/90">{candidate.text}</p>
      <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-haze">
        {candidate.reasons.join(" · ")}
      </p>
    </button>
  );
}

function PreviewCard({ item, index }: { item: ApiItem; index: number }) {
  return (
    <article className="glass-soft rounded-lg p-4">
      <div className="mb-2 font-mono text-xs text-haze">#{String(index + 1).padStart(2, "0")}</div>
      <p className="text-sm leading-relaxed text-mist/85">{item.original_zh}</p>
      <p className="mt-3 text-[15px] leading-relaxed text-mist">{item.spoken_english}</p>
      {(item.focus_phrase || item.note_zh) && (
        <div className="mt-3 border-t border-white/8 pt-3">
          {item.focus_phrase && <div className="text-sm font-semibold text-azure">{item.focus_phrase}</div>}
          {item.note_zh && <div className="mt-1 text-xs leading-relaxed text-haze">{item.note_zh}</div>}
        </div>
      )}
    </article>
  );
}
