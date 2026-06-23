"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Watch } from "lucide-react";
import { ApiError, apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  currentPlanSchema,
  planSchema,
  GOALS,
  type Plan,
} from "@/schemas/plan";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { PlanTimeline } from "./plan-timeline";

type Phase = "loading" | "error" | "premium" | "ready";

/** Training plan screen: generate a periodized plan or view the active one (US5). */
export function PlanView() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [plan, setPlan] = useState<Plan | null>(null);
  const [goal, setGoal] = useState<string>(GOALS[0].value);
  const [weeks, setWeeks] = useState(12);
  const [generating, setGenerating] = useState(false);
  // Push-to-watch (A14): POST /plans/push uploads this week's structured workout.
  const [watch, setWatch] = useState<
    "idle" | "confirm" | "sending" | "synced" | "error"
  >("idle");

  const sendToWatch = async () => {
    setWatch("sending");
    try {
      const token = await getAccessToken();
      await apiFetch("/plans/push", { method: "POST", token });
      setWatch("synced");
    } catch {
      setWatch("error");
    }
  };

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/plans/current", { token });
      setPlan(currentPlanSchema.parse(raw).plan);
      setPhase("ready");
    } catch (err) {
      setPhase(err instanceof ApiError && err.status === 402 ? "premium" : "error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const generate = async () => {
    setGenerating(true);
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/plans", {
        method: "POST",
        token,
        body: JSON.stringify({ goal, weeks }),
      });
      setPlan(planSchema.parse(raw));
    } catch {
      setPhase("error");
    } finally {
      setGenerating(false);
    }
  };

  if (phase === "loading") return <LoadingState rows={4} label="Loading your plan" />;
  if (phase === "error") {
    return <ErrorState message="We couldn't load your plan." onRetry={() => void load()} />;
  }
  if (phase === "premium") {
    return (
      <div className="rounded-md border border-border p-6 text-center">
        <h2 className="font-display text-lg font-semibold">Training plans are premium</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Upgrade to get an adaptive, periodized plan for your goal.
        </p>
        <Button asChild className="mt-4">
          <Link href="/settings/subscription">Upgrade to Premium</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded border border-line bg-card p-5">
        <h2 className="font-display text-lg font-semibold tracking-tight text-ink">
          {plan ? "Regenerate your plan" : "Build your plan"}
        </h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="goal">Goal</Label>
            <select
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="w-full rounded border border-input bg-card px-3 py-2.5 text-sm text-foreground focus-visible:border-primary focus-visible:outline-none"
            >
              {GOALS.map((g) => (
                <option key={g.value} value={g.value}>
                  {g.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="weeks">Weeks</Label>
            <input
              id="weeks"
              type="number"
              min={4}
              max={24}
              value={weeks}
              onChange={(e) => setWeeks(Number(e.target.value))}
              className="w-full rounded border border-input bg-card px-3 py-2.5 text-sm text-foreground focus-visible:border-primary focus-visible:outline-none"
            />
          </div>
        </div>
        <Button className="mt-4" onClick={generate} disabled={generating}>
          {generating && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
          {generating ? "Generating…" : "Generate plan"}
        </Button>
      </div>

      {plan && (
        <div className="space-y-4">
          {plan.narrative && (
            <section
              aria-label="Plan rationale"
              className="rounded border border-line border-l-2 border-l-primary bg-card p-5"
            >
              <p className="whitespace-pre-line text-[15px] leading-relaxed text-ink-soft">
                {plan.narrative}
              </p>
            </section>
          )}
          <PlanTimeline weeks={plan.structure.weeks} />

          <section className="rounded border border-line bg-card p-5">
            {watch === "synced" ? (
              <p className="flex items-center gap-2 text-sm font-medium text-olive">
                <Watch className="h-4 w-4" aria-hidden />
                This week&apos;s workouts are on your Garmin watch.
              </p>
            ) : watch === "confirm" || watch === "sending" ? (
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-ink-soft">
                  Send this week&apos;s structured workouts to your watch?
                </p>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={sendToWatch}
                    disabled={watch === "sending"}
                  >
                    {watch === "sending" && (
                      <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                    )}
                    {watch === "sending" ? "Sending…" : "Confirm"}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setWatch("idle")}
                    disabled={watch === "sending"}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : watch === "error" ? (
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p role="alert" className="text-sm text-destructive">
                  We couldn&apos;t reach your watch. Connect Garmin and try again.
                </p>
                <Button size="sm" variant="ghost" onClick={() => setWatch("idle")}>
                  Dismiss
                </Button>
              </div>
            ) : (
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <Watch className="h-5 w-5 text-primary" aria-hidden />
                  <div>
                    <h3 className="font-display text-sm font-semibold text-ink">
                      Push to watch
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      Sync this week&apos;s sessions to your Garmin.
                    </p>
                  </div>
                </div>
                <Button size="sm" onClick={() => setWatch("confirm")}>
                  Send to watch
                </Button>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
