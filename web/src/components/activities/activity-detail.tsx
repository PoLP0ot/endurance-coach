"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Sparkles } from "lucide-react";
import { ApiError, apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  activityDetailSchema,
  analysisSchema,
  type ActivityAnalysis,
  type ActivityDetail,
} from "@/schemas/analysis";
import { formatDate, formatDistance, formatDuration } from "@/lib/format";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { MetricCard } from "@/components/dashboard/metric-card";
import { Button } from "@/components/ui/button";

type Phase = "loading" | "error" | "ready";
type AnalysisState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "premium" }
  | { kind: "error" }
  | { kind: "ready"; data: ActivityAnalysis };

/** Activity detail with the coach-first "What This Run Means" analysis (US3). */
export function ActivityDetail({ id }: { id: string }) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [activity, setActivity] = useState<ActivityDetail | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisState>({ kind: "idle" });

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>(`/activities/${id}`, { token });
      setActivity(activityDetailSchema.parse(raw));
      setPhase("ready");
    } catch {
      setPhase("error");
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  const analyze = async () => {
    setAnalysis({ kind: "loading" });
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>(`/activities/${id}/analysis`, { token });
      setAnalysis({ kind: "ready", data: analysisSchema.parse(raw) });
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        setAnalysis({ kind: "premium" });
      } else {
        setAnalysis({ kind: "error" });
      }
    }
  };

  if (phase === "loading") return <LoadingState rows={4} label="Loading activity" />;
  if (phase === "error" || !activity) {
    return (
      <ErrorState
        message="We couldn't load this activity."
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/activities"
          className="text-sm text-muted-foreground underline-offset-4 hover:underline"
        >
          ← Activity history
        </Link>
        <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight">
          {activity.name ?? activity.activity_type}
        </h1>
        <p className="text-sm text-muted-foreground">
          {formatDate(activity.start_time)}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard label="Distance" value={formatDistance(activity.distance_m)} />
        <MetricCard label="Duration" value={formatDuration(activity.duration_s)} />
        <MetricCard
          label="Avg HR"
          value={activity.avg_hr ? String(activity.avg_hr) : "—"}
          unit={activity.avg_hr ? "bpm" : undefined}
        />
        <MetricCard
          label="TSS"
          value={activity.tss !== null ? activity.tss.toFixed(0) : "—"}
        />
      </div>

      <section
        aria-label="What this run means"
        className="rounded-md border border-border p-5"
      >
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-accent" aria-hidden />
          <h2 className="font-display text-lg font-semibold tracking-tight">
            What this run means
          </h2>
        </div>

        {analysis.kind === "idle" && (
          <div className="mt-3">
            <p className="text-sm text-muted-foreground">
              Get your coach&apos;s read on this session.
            </p>
            <Button className="mt-3" onClick={analyze}>
              Analyze with coach
            </Button>
          </div>
        )}

        {analysis.kind === "loading" && (
          <p className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Your coach is reading the data…
          </p>
        )}

        {analysis.kind === "premium" && (
          <div className="mt-3 rounded-md bg-secondary/50 p-4">
            <p className="text-sm">
              AI activity analysis is a premium feature.
            </p>
            <Button asChild className="mt-3" variant="default">
              <Link href="/settings/subscription">Upgrade to Premium</Link>
            </Button>
          </div>
        )}

        {analysis.kind === "error" && (
          <p role="alert" className="mt-3 text-sm text-destructive">
            We couldn&apos;t generate an analysis. Please try again.
          </p>
        )}

        {analysis.kind === "ready" && (
          <div className="mt-3 space-y-3">
            <p className="whitespace-pre-line text-sm leading-relaxed">
              {analysis.data.narrative}
            </p>
            <details className="text-xs text-muted-foreground">
              <summary className="cursor-pointer">Evidence</summary>
              <pre className="mt-2 overflow-x-auto rounded-md bg-secondary/50 p-3 font-data">
                {JSON.stringify(analysis.data.facts, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </section>
    </div>
  );
}
