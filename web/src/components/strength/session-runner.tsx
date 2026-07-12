"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Check, Loader2 } from "lucide-react";
import { ApiError, apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  sessionLogsSchema,
  sessionSummarySchema,
  strengthCurrentSchema,
  type SessionSummary,
  type StrengthItem,
  type StrengthSession,
  type Suggestion,
} from "@/schemas/strength";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Phase = "loading" | "error" | "premium" | "not-found" | "ready";

type SetEntry = {
  weight: string;
  reps: string;
  rpe: string;
  logged: boolean;
  saving: boolean;
};
type SetsState = Record<string, SetEntry>;

const setKey = (exerciseId: string, index: number) => `${exerciseId}:${index}`;

function initialSets(
  session: StrengthSession,
  logged: Map<string, { weight_kg: number | null; reps: number }>,
  suggestions: Record<string, Suggestion>,
): SetsState {
  const state: SetsState = {};
  for (const item of session.items) {
    const suggested = suggestions[item.exercise_id]?.weight_kg;
    for (let i = 1; i <= item.sets; i += 1) {
      const key = setKey(item.exercise_id, i);
      const existing = logged.get(key);
      const weight = existing?.weight_kg ?? suggested;
      state[key] = {
        weight: weight != null ? String(weight) : "",
        reps: String(existing?.reps ?? item.reps),
        rpe: "",
        logged: existing !== undefined,
        saving: false,
      };
    }
  }
  return state;
}

/** Guided session: log weight × reps per set, rest timer, completion (M4). */
export function SessionRunner({ week, day }: { week: number; day: number }) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [session, setSession] = useState<StrengthSession | null>(null);
  const [sets, setSets] = useState<SetsState>({});
  const [suggestions, setSuggestions] = useState<Record<string, Suggestion>>({});
  const [restLeft, setRestLeft] = useState<number | null>(null);
  const [finishing, setFinishing] = useState(false);
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const rawPlan = await apiFetch<unknown>("/strength/plans/current", { token });
      const plan = strengthCurrentSchema.parse(rawPlan).plan;
      const found = plan?.structure.weeks
        .find((w) => w.week === week)
        ?.sessions.find((s) => s.day === day);
      if (!found) {
        setPhase("not-found");
        return;
      }
      const rawLogs = await apiFetch<unknown>(
        `/strength/logs?week=${week}&day=${day}`,
        { token },
      );
      const logs = sessionLogsSchema.parse(rawLogs);
      const logged = new Map(
        logs.sets.map((s) => [setKey(s.exercise_id, s.set_index), s]),
      );
      setSession(found);
      setSuggestions(logs.suggestions);
      setSets(initialSets(found, logged, logs.suggestions));
      if (logs.summary.completed) setSummary(logs.summary);
      setPhase("ready");
    } catch (err) {
      setPhase(err instanceof ApiError && err.status === 402 ? "premium" : "error");
    }
  }, [week, day]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(
    () => () => {
      if (timerRef.current) clearInterval(timerRef.current);
    },
    [],
  );

  const startRest = (seconds: number) => {
    if (timerRef.current) clearInterval(timerRef.current);
    setRestLeft(seconds);
    timerRef.current = setInterval(() => {
      setRestLeft((left) => {
        if (left === null || left <= 1) {
          if (timerRef.current) clearInterval(timerRef.current);
          return null;
        }
        return left - 1;
      });
    }, 1000);
  };

  const patchSet = (key: string, patch: Partial<SetEntry>) =>
    setSets((prev) => ({ ...prev, [key]: { ...prev[key], ...patch } }));

  const logOne = async (item: StrengthItem, index: number) => {
    const key = setKey(item.exercise_id, index);
    const entry = sets[key];
    const reps = Number(entry.reps);
    if (!Number.isFinite(reps) || reps < 1) return;
    patchSet(key, { saving: true });
    try {
      const token = await getAccessToken();
      await apiFetch<unknown>("/strength/logs", {
        method: "POST",
        token,
        body: JSON.stringify({
          week,
          day,
          exercise_id: item.exercise_id,
          set_index: index,
          weight_kg: entry.weight === "" ? null : Number(entry.weight),
          reps,
          rpe: entry.rpe === "" ? null : Number(entry.rpe),
        }),
      });
      patchSet(key, { logged: true, saving: false });
      startRest(item.rest_sec);
    } catch {
      patchSet(key, { saving: false });
    }
  };

  const finish = async () => {
    setFinishing(true);
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/strength/sessions/complete", {
        method: "POST",
        token,
        body: JSON.stringify({ week, day }),
      });
      setSummary(sessionSummarySchema.parse(raw));
    } finally {
      setFinishing(false);
    }
  };

  if (phase === "loading") {
    return <LoadingState rows={6} label="Loading your session" />;
  }
  if (phase === "error") {
    return (
      <ErrorState
        message="We couldn't load this session."
        onRetry={() => void load()}
      />
    );
  }
  if (phase === "premium") {
    return (
      <div className="rounded border border-line bg-card p-6 text-center text-sm">
        <p className="mb-3">Strength sessions are premium.</p>
        <Button asChild>
          <Link href="/settings/subscription">See premium</Link>
        </Button>
      </div>
    );
  }
  if (phase === "not-found" || session === null) {
    return (
      <ErrorState message="This session isn't part of your current program." />
    );
  }

  if (summary !== null) {
    return (
      <div className="space-y-4 rounded border border-line bg-card p-6 text-center">
        <Check className="mx-auto h-8 w-8 text-accent" aria-hidden />
        <h2 className="font-display text-xl font-semibold">Session complete</h2>
        <p className="text-sm text-muted-foreground">
          {summary.sets_logged} / {summary.sets_prescribed} sets logged ·{" "}
          {summary.volume_kg} kg total volume
        </p>
        <Button asChild variant="outline">
          <Link href="/strength">Back to program</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Link
        href="/strength"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Program
      </Link>

      {restLeft !== null && (
        <div className="sticky top-2 z-10 rounded border border-primary bg-card px-4 py-2 text-center font-mono text-sm text-ink shadow-sm">
          Rest {restLeft}s
        </div>
      )}

      <div className="space-y-4">
        {session.items.map((item) => (
          <div key={item.exercise_id} className="rounded border border-line bg-card">
            <div className="flex items-center gap-3 border-b border-line p-3">
              {/* eslint-disable-next-line @next/next/no-img-element -- CDN gif */}
              <img
                src={item.gif_url}
                alt={item.name}
                className="h-16 w-16 shrink-0 rounded border border-line object-cover"
              />
              <div className="min-w-0">
                <Link
                  href={`/exercises/${item.exercise_id}`}
                  className="font-display text-sm font-semibold text-ink underline-offset-4 hover:underline"
                >
                  {item.name}
                </Link>
                <p className="text-xs text-muted-foreground">
                  {item.sets} × {item.reps} @ RPE {item.rpe} · rest {item.rest_sec}s
                </p>
                {suggestions[item.exercise_id]?.last && (
                  <p className="text-xs text-muted-foreground">
                    Last: {suggestions[item.exercise_id].last?.weight_kg ?? "—"} kg
                    × {suggestions[item.exercise_id].last?.reps}
                  </p>
                )}
              </div>
            </div>
            <ul className="divide-y divide-line">
              {Array.from({ length: item.sets }, (_, i) => i + 1).map((index) => {
                const key = setKey(item.exercise_id, index);
                const entry = sets[key];
                return (
                  <li key={index} className="flex items-center gap-2 px-3 py-2">
                    <span className="w-10 shrink-0 font-mono text-xs text-muted-foreground">
                      Set {index}
                    </span>
                    <Input
                      aria-label={`${item.name} set ${index} weight`}
                      type="number"
                      inputMode="decimal"
                      placeholder="kg"
                      className="h-9 w-20"
                      value={entry.weight}
                      onChange={(e) => patchSet(key, { weight: e.target.value })}
                    />
                    <Input
                      aria-label={`${item.name} set ${index} reps`}
                      type="number"
                      inputMode="numeric"
                      placeholder="reps"
                      className="h-9 w-20"
                      value={entry.reps}
                      onChange={(e) => patchSet(key, { reps: e.target.value })}
                    />
                    <Input
                      aria-label={`${item.name} set ${index} RPE`}
                      type="number"
                      inputMode="numeric"
                      min={1}
                      max={10}
                      placeholder="RPE"
                      className="h-9 w-16"
                      value={entry.rpe}
                      onChange={(e) => patchSet(key, { rpe: e.target.value })}
                    />
                    <Button
                      size="sm"
                      variant={entry.logged ? "outline" : "default"}
                      className="ml-auto"
                      disabled={entry.saving}
                      onClick={() => void logOne(item, index)}
                    >
                      {entry.saving ? (
                        <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                      ) : entry.logged ? (
                        <Check className="h-4 w-4" aria-hidden />
                      ) : (
                        "Log"
                      )}
                    </Button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>

      <Button onClick={finish} disabled={finishing} className="w-full">
        {finishing && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden />}
        Finish session
      </Button>
    </div>
  );
}
