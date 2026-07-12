"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  exerciseDetailSchema,
  type ExerciseDetail as ExerciseDetailData,
} from "@/schemas/exercise";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";

type Phase = "loading" | "error" | "ready";

/** Full exercise sheet: animated demo, muscles and step-by-step form (M2). */
export function ExerciseDetail({ id }: { id: string }) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [exercise, setExercise] = useState<ExerciseDetailData | null>(null);

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>(`/exercises/${id}`, { token });
      setExercise(exerciseDetailSchema.parse(raw));
      setPhase("ready");
    } catch {
      setPhase("error");
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  if (phase === "loading") {
    return <LoadingState rows={5} label="Loading exercise" />;
  }
  if (phase === "error" || exercise === null) {
    return (
      <ErrorState
        message="We couldn't load this exercise."
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href="/exercises"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Library
      </Link>

      <div className="grid gap-6 md:grid-cols-[280px_1fr]">
        <div className="overflow-hidden rounded border border-line bg-card">
          {/* eslint-disable-next-line @next/next/no-img-element -- CDN gif, no Next loader */}
          <img
            src={exercise.gif_url}
            alt={exercise.name}
            className="aspect-square w-full object-cover"
          />
        </div>

        <div className="space-y-4">
          <div>
            <h1 className="font-display text-2xl font-semibold tracking-tight">
              {exercise.name}
            </h1>
            <p className="text-sm text-muted-foreground">
              {exercise.body_part} · {exercise.equipment}
            </p>
          </div>

          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded border border-line bg-card p-3">
              <dt className="text-xs text-muted-foreground">Target muscle</dt>
              <dd className="font-display font-semibold text-ink">
                {exercise.target}
              </dd>
            </div>
            <div className="rounded border border-line bg-card p-3">
              <dt className="text-xs text-muted-foreground">Also works</dt>
              <dd className="text-ink">
                {exercise.secondary_muscles.length > 0
                  ? exercise.secondary_muscles.join(", ")
                  : "—"}
              </dd>
            </div>
          </dl>

          <div className="rounded border border-line bg-card p-4">
            <h2 className="mb-2 font-display text-sm font-semibold text-ink">
              How to perform it
            </h2>
            <ol className="list-decimal space-y-1.5 pl-5 text-sm text-foreground">
              {exercise.instructions.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>

          {exercise.attribution && (
            <p className="text-xs text-muted-foreground">{exercise.attribution}</p>
          )}
        </div>
      </div>
    </div>
  );
}
