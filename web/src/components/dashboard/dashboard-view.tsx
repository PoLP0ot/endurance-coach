"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Activity } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { dashboardSchema, type Dashboard } from "@/schemas/dashboard";
import { profileSchema } from "@/schemas/profile";
import { GOALS } from "@/schemas/plan";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { MetricCard } from "./metric-card";
import { CoachNote } from "./coach-note";
import { TrainingLoadChart } from "./training-load-chart";

type Phase =
  | { kind: "loading" }
  | { kind: "error" }
  | { kind: "ready"; data: Dashboard; goal: string | null };

/** Goal-aware framing for the dashboard "lens" (A13). */
const GOAL_LENS: Record<string, string> = {
  marathon: "Every metric read against your race readiness.",
  weight_loss: "Training framed around steady, sustainable fat loss.",
  hyrox: "Balancing run volume with strength endurance.",
  triathlon: "Your three sports as one combined load.",
  health: "Consistency, recovery and long-term health first.",
};

/** Coach-first dashboard: narrative first, then metrics and the load chart. */
export function DashboardView() {
  const [phase, setPhase] = useState<Phase>({ kind: "loading" });

  const load = useCallback(async () => {
    setPhase({ kind: "loading" });
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/dashboard", { token });
      const data = dashboardSchema.parse(raw);
      let goal: string | null = null;
      try {
        const profileRaw = await apiFetch<unknown>("/profile", { token });
        goal = profileSchema.parse(profileRaw).primary_goal;
      } catch {
        // profile is optional context — the dashboard renders without it
      }
      setPhase({ kind: "ready", data, goal });
    } catch {
      setPhase({ kind: "error" });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (phase.kind === "loading") {
    return <LoadingState rows={4} label="Loading your dashboard" />;
  }
  if (phase.kind === "error") {
    return (
      <ErrorState
        message="We couldn't load your dashboard."
        onRetry={() => void load()}
      />
    );
  }

  const { data, goal } = phase;
  const goalLabel = goal
    ? GOALS.find((g) => g.value === goal)?.label
    : undefined;
  const lens = goal ? GOAL_LENS[goal] : undefined;
  if (data.totals.activity_count === 0) {
    return (
      <EmptyState
        icon={Activity}
        title="No training data yet"
        description="Connect your Garmin to see your fitness, form and recovery."
        action={
          <Button asChild>
            <Link href="/onboarding">Connect Garmin</Link>
          </Button>
        }
      />
    );
  }

  const km = ((data.totals.total_distance_m ?? 0) / 1000).toFixed(1);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="font-display text-2xl font-semibold tracking-tight">
          Progress
        </h1>
        {goalLabel && (
          <span className="rounded-full border border-primary/40 bg-primary/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.12em] text-primary">
            {goalLabel} lens
          </span>
        )}
      </div>
      {lens && <p className="-mt-3 text-sm text-muted-foreground">{lens}</p>}
      <CoachNote headline={data.form.headline} detail={data.form.detail} />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard
          label="Fitness"
          value={data.fitness.ctl.toFixed(0)}
          hint="CTL · 42-day load"
          accentClassName="text-primary"
        />
        <MetricCard
          label="Fatigue"
          value={data.fitness.atl.toFixed(0)}
          hint="ATL · 7-day load"
          accentClassName="text-destructive"
        />
        <MetricCard
          label="Form"
          value={data.fitness.tsb.toFixed(0)}
          hint="TSB · balance"
        />
        <MetricCard
          label="Recovery"
          value={String(data.recovery)}
          unit="/100"
          accentClassName="text-accent"
        />
      </div>
      <TrainingLoadChart data={data.load_series} />
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {data.totals.activity_count} activities · {km} km in the last{" "}
          {data.totals.window_days} days
        </p>
        <Link
          href="/activities"
          className="text-sm text-primary underline-offset-4 hover:underline"
        >
          View history
        </Link>
      </div>
    </div>
  );
}
