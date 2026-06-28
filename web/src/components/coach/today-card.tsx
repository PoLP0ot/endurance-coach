"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { CalendarCheck } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { todaySchema, type Today } from "@/schemas/today";

/** "What do I do today" — the daily entry to the closed loop (C4). */
export function TodayCard() {
  const [today, setToday] = useState<Today | null>(null);

  const load = useCallback(async () => {
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/coach/today", { token });
      setToday(todaySchema.parse(raw));
    } catch {
      setToday(null);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (!today) return null;

  const adherence = today.adherence;
  const headline =
    today.status === "no_plan"
      ? "No active plan yet — generate one to get daily sessions."
      : today.is_rest
        ? "Rest day — let today's recovery bank your training."
        : today.session?.prescription;

  return (
    <section className="rounded border border-line border-l-2 border-l-primary bg-card p-5">
      <div className="flex items-center gap-2.5">
        <CalendarCheck className="h-4 w-4 text-primary" aria-hidden />
        <h2 className="font-display text-base font-semibold tracking-tight text-ink">
          Today
        </h2>
        {today.phase && (
          <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
            {today.phase} · week {today.week}
          </span>
        )}
      </div>
      <p className="mt-2 text-[15px] leading-relaxed text-ink-soft">{headline}</p>
      {today.status === "no_plan" ? (
        <Link
          href="/plan"
          className="mt-3 inline-block text-sm text-primary underline-offset-4 hover:underline"
        >
          Build your plan →
        </Link>
      ) : (
        adherence?.adherence_pct != null && (
          <p className="mt-3 font-mono text-[11px] text-muted-foreground">
            This week: {adherence.adherence_pct}% adherence · {adherence.completed}{" "}
            done · {adherence.missed} missed
          </p>
        )
      )}
    </section>
  );
}
