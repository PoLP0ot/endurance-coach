"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Dumbbell, Loader2 } from "lucide-react";
import { ApiError, apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  STRENGTH_EQUIPMENT_OPTIONS,
  STRENGTH_FREQUENCY_OPTIONS,
  STRENGTH_LEVELS,
  STRENGTH_WEEK_OPTIONS,
  exerciseHistorySchema,
  strengthCurrentSchema,
  strengthPlanSchema,
  type ExerciseHistory,
  type StrengthPlan,
  type StrengthWeek,
} from "@/schemas/strength";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

type Phase = "loading" | "error" | "premium" | "ready";

const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const SELECT_CLASS =
  "w-full rounded border border-input bg-card px-3 py-2.5 text-sm text-foreground focus-visible:border-primary focus-visible:outline-none";

/** The week containing today, else the first upcoming week. */
function currentWeek(weeks: StrengthWeek[]): StrengthWeek | null {
  const today = new Date().toISOString().slice(0, 10);
  for (const week of weeks) {
    const start = week.start_date;
    const end = new Date(new Date(start).getTime() + 7 * 86400000)
      .toISOString()
      .slice(0, 10);
    if (today >= start && today < end) return week;
  }
  return weeks[0] ?? null;
}

function SetupForm({
  onCreated,
}: {
  onCreated: (plan: StrengthPlan) => void;
}) {
  const [frequency, setFrequency] = useState(3);
  const [weeks, setWeeks] = useState(12);
  const [level, setLevel] = useState("beginner");
  const [equipment, setEquipment] = useState<string[]>(["body weight"]);
  const [submitting, setSubmitting] = useState(false);
  const [failed, setFailed] = useState(false);

  const toggle = (item: string) =>
    setEquipment((prev) =>
      prev.includes(item) ? prev.filter((e) => e !== item) : [...prev, item],
    );

  const submit = async () => {
    setSubmitting(true);
    setFailed(false);
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/strength/plans", {
        method: "POST",
        token,
        body: JSON.stringify({ frequency, weeks, level, equipment }),
      });
      onCreated(strengthPlanSchema.parse(raw));
    } catch {
      setFailed(true);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4 rounded border border-line bg-card p-6">
      <div>
        <h2 className="font-display text-lg font-semibold">Build your program</h2>
        <p className="text-sm text-muted-foreground">
          A periodized strength block — or ask your coach in chat and it will
          set one up with you.
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="space-y-1.5">
          <Label htmlFor="strength-frequency">Sessions / week</Label>
          <select
            id="strength-frequency"
            value={frequency}
            onChange={(e) => setFrequency(Number(e.target.value))}
            className={SELECT_CLASS}
          >
            {STRENGTH_FREQUENCY_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="strength-weeks">Length (weeks)</Label>
          <select
            id="strength-weeks"
            value={weeks}
            onChange={(e) => setWeeks(Number(e.target.value))}
            className={SELECT_CLASS}
          >
            {STRENGTH_WEEK_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="strength-level">Level</Label>
          <select
            id="strength-level"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className={SELECT_CLASS}
          >
            {STRENGTH_LEVELS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <fieldset className="space-y-1.5">
        <legend className="text-sm font-medium">Available equipment</legend>
        <div className="flex flex-wrap gap-2">
          {STRENGTH_EQUIPMENT_OPTIONS.map((item) => {
            const active = equipment.includes(item);
            return (
              <button
                key={item}
                type="button"
                onClick={() => toggle(item)}
                aria-pressed={active}
                className={`rounded border px-3 py-1.5 text-sm transition-colors ${
                  active
                    ? "border-primary bg-primary/10 text-ink"
                    : "border-line bg-card text-muted-foreground hover:border-primary"
                }`}
              >
                {item}
              </button>
            );
          })}
        </div>
      </fieldset>
      {failed && (
        <p role="alert" className="text-sm text-destructive">
          We couldn&apos;t generate the program. Try again.
        </p>
      )}
      <Button onClick={submit} disabled={submitting || equipment.length === 0}>
        {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden />}
        Generate my program
      </Button>
    </div>
  );
}

function WeekDetail({ week }: { week: StrengthWeek }) {
  return (
    <div className="space-y-3">
      {week.sessions.map((session) => (
        <div key={session.day} className="rounded border border-line bg-card">
          <div className="flex items-baseline justify-between gap-3 border-b border-line px-4 py-2.5">
            <p className="font-display text-sm font-semibold text-ink">
              {session.title}
            </p>
            <p className="ml-auto text-xs text-muted-foreground">
              {DAY_NAMES[session.day]}
            </p>
            <Link
              href={`/strength/session?week=${week.week}&day=${session.day}`}
              className="text-xs font-medium text-primary underline-offset-4 hover:underline"
            >
              Start →
            </Link>
          </div>
          <ul className="divide-y divide-line">
            {session.items.map((item) => (
              <li key={item.exercise_id} className="flex items-center gap-3 px-4 py-2.5">
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/exercises/${item.exercise_id}`}
                    className="truncate font-display text-sm font-medium text-ink underline-offset-4 hover:underline"
                  >
                    {item.name}
                  </Link>
                  <p className="text-xs text-muted-foreground">
                    {item.slot} · {item.equipment}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <p className="font-display text-sm font-semibold tabular-nums text-ink">
                    {item.sets} × {item.reps}
                  </p>
                  <p className="font-mono text-[10px] text-muted-foreground">
                    RPE {item.rpe} · rest {item.rest_sec}s
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

/** Long-term strength program: setup, block overview, current week (M3). */
export function StrengthView() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [plan, setPlan] = useState<StrengthPlan | null>(null);
  const [history, setHistory] = useState<ExerciseHistory["exercises"]>([]);

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/strength/plans/current", { token });
      const current = strengthCurrentSchema.parse(raw).plan;
      setPlan(current);
      setPhase("ready");
      if (current !== null) {
        try {
          const rawHistory = await apiFetch<unknown>("/strength/history", { token });
          setHistory(exerciseHistorySchema.parse(rawHistory).exercises);
        } catch {
          setHistory([]);
        }
      }
    } catch (err) {
      setPhase(err instanceof ApiError && err.status === 402 ? "premium" : "error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (phase === "loading") {
    return <LoadingState rows={6} label="Loading your program" />;
  }
  if (phase === "error") {
    return (
      <ErrorState
        message="We couldn't load your strength program."
        onRetry={() => void load()}
      />
    );
  }
  if (phase === "premium") {
    return (
      <div className="space-y-3 rounded border border-line bg-card p-6 text-center">
        <Dumbbell className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden />
        <h2 className="font-display text-lg font-semibold">
          Strength programs are premium
        </h2>
        <p className="text-sm text-muted-foreground">
          Upgrade to get a periodized program built from your equipment and level.
        </p>
        <Button asChild>
          <Link href="/settings/subscription">See premium</Link>
        </Button>
      </div>
    );
  }

  if (plan === null) {
    return <SetupForm onCreated={setPlan} />;
  }

  const week = currentWeek(plan.structure.weeks);
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {[
          `${plan.weeks} weeks`,
          `${plan.frequency}×/week`,
          plan.level,
          plan.equipment.join(", "),
        ].map((chip) => (
          <span
            key={chip}
            className="rounded-full border border-line bg-card px-2.5 py-1 text-muted-foreground"
          >
            {chip}
          </span>
        ))}
      </div>

      <div className="flex overflow-hidden rounded border border-line">
        {plan.structure.blocks.map((block) => (
          <div
            key={block.block}
            style={{ flexGrow: block.weeks }}
            className="border-r border-line bg-card px-3 py-2 last:border-r-0"
          >
            <p className="font-display text-xs font-semibold capitalize text-ink">
              {block.block}
            </p>
            <p className="text-[10px] text-muted-foreground">{block.weeks} wk</p>
          </div>
        ))}
      </div>

      {week && (
        <section className="space-y-3">
          <div>
            <h2 className="font-display text-lg font-semibold">
              Week {week.week}
              {week.is_deload && (
                <span className="ml-2 rounded-full border border-line bg-secondary px-2 py-0.5 text-xs font-normal text-muted-foreground">
                  deload
                </span>
              )}
            </h2>
            <p className="text-sm text-muted-foreground">{week.focus}</p>
          </div>
          <WeekDetail week={week} />
        </section>
      )}

      {history.length > 0 && (
        <section className="space-y-2">
          <h3 className="font-display text-sm font-semibold text-ink">Progress</h3>
          <ul className="divide-y divide-line rounded border border-line bg-card">
            {history.map((entry) => (
              <li
                key={entry.exercise_id}
                className="flex items-center justify-between gap-3 px-4 py-2 text-sm"
              >
                <Link
                  href={`/exercises/${entry.exercise_id}`}
                  className="truncate text-ink underline-offset-4 hover:underline"
                >
                  {entry.name}
                </Link>
                <span className="shrink-0 font-mono text-xs text-muted-foreground">
                  {entry.pr_weight_kg !== null && `PR ${entry.pr_weight_kg} kg · `}
                  last {entry.last_weight_kg ?? "—"} kg × {entry.last_reps}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="space-y-2">
        <h3 className="font-display text-sm font-semibold text-ink">All weeks</h3>
        <ul className="divide-y divide-line rounded border border-line bg-card">
          {plan.structure.weeks.map((w) => (
            <li
              key={w.week}
              className="flex items-center justify-between px-4 py-2 text-sm"
            >
              <span className="text-ink">Week {w.week}</span>
              <span className="text-xs capitalize text-muted-foreground">
                {w.block}
                {w.is_deload && " · deload"}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
