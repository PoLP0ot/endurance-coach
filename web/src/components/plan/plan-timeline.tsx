import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import { type PlanWeek } from "@/schemas/plan";

const PHASE_LABEL: Record<PlanWeek["phase"], string> = {
  base: "Base",
  build: "Build",
  peak: "Peak",
  taper: "Taper",
};

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

/** True when today falls inside the week starting at ``startDate``. */
function isCurrentWeek(startDate: string): boolean {
  const start = new Date(`${startDate}T00:00:00`).getTime();
  const now = Date.now();
  return now >= start && now < start + WEEK_MS;
}

/** Week-by-week periodized plan timeline (US5). */
export function PlanTimeline({ weeks }: { weeks: PlanWeek[] }) {
  return (
    <ol className="divide-y divide-line rounded border border-line bg-card">
      {weeks.map((w) => {
        const current = isCurrentWeek(w.start_date);
        return (
          <li
            key={w.week}
            className={cn(
              "flex items-center justify-between gap-4 border-l-2 border-l-transparent px-4 py-3",
              current && "border-l-primary bg-primary/[0.04]",
            )}
          >
            <div className="min-w-0">
              <p className="font-display text-sm font-semibold text-ink">
                Week {w.week}
                <span className="ml-2 font-mono text-[10px] uppercase tracking-wide text-muted-foreground">
                  {formatDate(w.start_date)}
                </span>
                {current && (
                  <span className="ml-2 rounded-full bg-primary/10 px-2.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-primary">
                    This week
                  </span>
                )}
              </p>
              <p className="truncate text-xs text-muted-foreground">{w.focus}</p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              {w.is_recovery && (
                <span className="rounded-full bg-olive/15 px-2.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-olive">
                  Recovery
                </span>
              )}
              <span
                className={cn(
                  "rounded-full px-2.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em]",
                  w.phase === "peak"
                    ? "bg-primary/10 text-primary"
                    : "bg-secondary text-muted-foreground",
                )}
              >
                {PHASE_LABEL[w.phase]}
              </span>
              <span className="font-display text-sm font-semibold tabular-nums text-ink">
                {w.target_tss.toFixed(0)}
                <span className="ml-1 font-mono text-[10px] text-muted-foreground">
                  TSS
                </span>
              </span>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
