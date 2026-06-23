import type { Goal } from "@/schemas/dashboard";
import { formatDate } from "@/lib/format";

/** North-star race banner: name, date, countdown and a progress bar (US2). */
export function GoalBanner({ goal }: { goal: Goal }) {
  const pct = Math.max(0, Math.min(100, goal.progress_pct));
  const countdown = goal.is_past
    ? "Race day passed"
    : goal.days_to_go === 0
      ? "Race day is today"
      : `${goal.weeks_to_go} ${goal.weeks_to_go === 1 ? "week" : "weeks"} to go · ${goal.days_to_go} days`;

  return (
    <div className="rounded border border-line bg-ink p-5 text-paper">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="flex items-center gap-2 font-display text-xl font-semibold tracking-tight">
          <span aria-hidden>🏁</span>
          {goal.race_name ?? "Your goal race"}
        </p>
        <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-paper/70">
          {formatDate(goal.race_date)}
        </p>
      </div>
      <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-paper/15">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] text-paper/70">
        <span>{countdown}</span>
        <span>{pct}% of the journey</span>
      </div>
    </div>
  );
}
