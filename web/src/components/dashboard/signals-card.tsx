"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { signalsResponseSchema, type Signal } from "@/schemas/signals";

/**
 * Every metric answered as a question, inline on the dashboard (formerly the
 * /explore page). Trends live in the load chart above; this card carries the
 * coach's reading of each one. Progressive: renders nothing until loaded and
 * stays silent on failure — the dashboard must not break over commentary.
 */
export function SignalsCard() {
  const [signals, setSignals] = useState<Signal[]>([]);

  const load = useCallback(async () => {
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/signals", { token });
      setSignals(signalsResponseSchema.parse(raw).signals);
    } catch {
      setSignals([]);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (signals.length === 0) return null;

  return (
    <section className="rounded border border-line bg-card">
      <div className="flex items-center justify-between border-b border-line px-5 py-3">
        <h2 className="font-display text-base font-semibold tracking-tight">
          Signals
        </h2>
        <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
          Coach&apos;s read
        </span>
      </div>
      <div className="divide-y divide-line/60">
        {signals.map((s) => (
          <div key={s.key} className="px-5 py-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
              {s.eyebrow}
            </p>
            <h3 className="mt-1 font-display text-sm font-semibold tracking-tight text-ink">
              {s.question}
            </h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-soft">
              {s.interpretation}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
