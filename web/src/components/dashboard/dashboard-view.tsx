"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Activity } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { dashboardSchema, type Dashboard } from "@/schemas/dashboard";
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
  | { kind: "ready"; data: Dashboard };

/** Coach-first dashboard: narrative first, then metrics and the load chart. */
export function DashboardView() {
  const [phase, setPhase] = useState<Phase>({ kind: "loading" });

  const load = useCallback(async () => {
    setPhase({ kind: "loading" });
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/dashboard", { token });
      setPhase({ kind: "ready", data: dashboardSchema.parse(raw) });
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

  const { data } = phase;
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
      <h1 className="font-display text-2xl font-semibold tracking-tight">Progress</h1>
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
      <p className="text-sm text-muted-foreground">
        {data.totals.activity_count} activities · {km} km in the last{" "}
        {data.totals.window_days} days
      </p>
    </div>
  );
}
