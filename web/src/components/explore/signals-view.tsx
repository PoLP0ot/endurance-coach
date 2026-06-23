"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { signalsResponseSchema, type Signal } from "@/schemas/signals";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Activity } from "lucide-react";
import { Sparkline } from "./sparkline";

type Phase =
  | { kind: "loading" }
  | { kind: "error" }
  | { kind: "ready"; signals: Signal[] };

/** Signals / Explore: every metric framed as a question with a coach answer. */
export function SignalsView() {
  const [phase, setPhase] = useState<Phase>({ kind: "loading" });

  const load = useCallback(async () => {
    setPhase({ kind: "loading" });
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/signals", { token });
      const { signals } = signalsResponseSchema.parse(raw);
      setPhase({ kind: "ready", signals });
    } catch {
      setPhase({ kind: "error" });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (phase.kind === "loading") {
    return <LoadingState rows={3} label="Reading your signals" />;
  }
  if (phase.kind === "error") {
    return (
      <ErrorState message="We couldn't load your signals." onRetry={() => void load()} />
    );
  }
  if (phase.signals.length === 0) {
    return (
      <EmptyState
        icon={Activity}
        title="No signals yet"
        description="Connect your Garmin and we'll turn your data into clear answers."
      />
    );
  }

  const { signals } = phase;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">
          Your Signals
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Every metric, answered as a question — not a dump.
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {signals.map((s) => (
          <section key={s.question} className="rounded border border-line bg-card">
            <div className="px-6 pt-5">
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-primary">
                {s.eyebrow}
              </p>
              <h2 className="mt-1.5 font-display text-lg font-semibold tracking-tight text-ink">
                {s.question}
              </h2>
            </div>
            {s.points && (
              <div className={`px-6 pt-4 ${s.color ?? "text-primary"}`}>
                <Sparkline points={s.points} className="w-full" />
              </div>
            )}
            <div className="flex gap-3 px-6 pb-5 pt-4">
              <span
                className="mt-1.5 h-2 w-2 flex-none rounded-full bg-primary"
                aria-hidden
              />
              <p className="text-sm leading-relaxed text-ink-soft">
                <span className="font-semibold text-ink">Coach:</span>{" "}
                {s.interpretation}
              </p>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
