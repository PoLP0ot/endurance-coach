"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";
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
      <div className="rounded-md border border-border p-5">
        <h2 className="font-display text-lg font-semibold tracking-tight">
          {plan ? "Regenerate your plan" : "Build your plan"}
        </h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="goal">Goal</Label>
            <select
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
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
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
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
              className="rounded-md border-l-2 border-primary bg-secondary/40 p-5"
            >
              <p className="whitespace-pre-line text-sm leading-relaxed">
                {plan.narrative}
              </p>
            </section>
          )}
          <PlanTimeline weeks={plan.structure.weeks} />
        </div>
      )}
    </div>
  );
}
