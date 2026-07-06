"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { briefSchema, type Brief } from "@/schemas/brief";
import { CoachNote } from "./coach-note";

interface Fallback {
  headline: string;
  detail: string;
}

/** "Jul 6" from an ISO date for the brief badge. */
function shortDay(iso: string): string {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

/**
 * The proactive daily brief (premium, generated each morning) in the coach's
 * voice slot. Free users, errors and gated responses fall back to the weekly
 * Coach's Assessment so the dashboard always has exactly one coach narrative.
 */
export function BriefCard({ fallback }: { fallback: Fallback }) {
  const [brief, setBrief] = useState<Brief | null>(null);
  const [failed, setFailed] = useState(false);

  const load = useCallback(async () => {
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/coach/brief", { token });
      setBrief(briefSchema.parse(raw));
    } catch {
      setFailed(true);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (brief === null) {
    if (!failed) return null; // brief still loading — avoid a double narrative
    return <CoachNote headline={fallback.headline} detail={fallback.detail} />;
  }

  return (
    <section
      aria-label="Daily coach brief"
      className="rounded border border-line bg-card"
    >
      <div className="flex items-center gap-2.5 px-6 pt-4">
        <span className="h-2 w-2 flex-none rounded-full bg-primary" aria-hidden />
        <h2 className="font-display text-sm font-semibold text-ink">
          Coach&apos;s Brief
        </h2>
        <span className="ml-auto font-mono text-[9px] uppercase tracking-[0.14em] text-primary">
          {shortDay(brief.day)}
        </span>
      </div>
      <div className="px-6 pb-5 pt-3.5">
        <p className="text-[15px] leading-[1.72] text-ink-soft">
          {brief.headline && (
            <b className="font-semibold text-ink">{brief.headline} </b>
          )}
          {brief.body}
        </p>
      </div>
    </section>
  );
}
