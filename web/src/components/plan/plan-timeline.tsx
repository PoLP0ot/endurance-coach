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
const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

/** True when today falls inside the week starting at ``startDate``. */
function isCurrentWeek(startDate: string): boolean {
  const start = new Date(`${startDate}T00:00:00`).getTime();
  const now = Date.now();
  return now >= start && now < start + WEEK_MS;
}

/** Today's position in a Monday-first week (0 = Monday). */
function todayIndex(): number {
  return (new Date().getDay() + 6) % 7;
}

/** The current week's prescribed days, Monday-first; gaps are rest days. */
function WeekDays({ week }: { week: PlanWeek }) {
  const byDay = new Map(week.sessions.map((s) => [s.day_index, s]));
  const today = todayIndex();
  return (
    <ol className="mt-3 divide-y divide-line/60 border-t border-line/60">
      {DAY_NAMES.map((name, i) => {
        const session = byDay.get(i);
        const isToday = i === today;
        return (
          <li
            key={name}
            className={cn(
              "flex items-center gap-3 py-2 text-sm",
              isToday && "-mx-2 rounded bg-primary/[0.06] px-2",
            )}
          >
            <span
              className={cn(
                "w-9 shrink-0 font-mono text-[10px] uppercase tracking-[0.12em]",
                isToday ? "font-semibold text-primary" : "text-muted-foreground",
              )}
            >
              {name}
            </span>
            {session ? (
              <>
                <span className="min-w-0 flex-1 truncate text-ink-soft">
                  {session.prescription}
                </span>
                <span className="shrink-0 rounded-full bg-secondary px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-muted-foreground">
                  {session.kind}
                </span>
                {session.target_tss !== null && (
                  <span className="w-14 shrink-0 text-right font-display text-xs font-semibold tabular-nums text-ink">
                    {session.target_tss.toFixed(0)}
                    <span className="ml-1 font-mono text-[9px] font-normal text-muted-foreground">
                      TSS
                    </span>
                  </span>
                )}
              </>
            ) : (
              <span className="flex-1 text-xs text-muted-foreground">Rest</span>
            )}
          </li>
        );
      })}
    </ol>
  );
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
              "border-l-2 border-l-transparent px-4 py-3",
              current && "border-l-primary bg-primary/[0.04]",
            )}
          >
            <div className="flex items-center justify-between gap-4">
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
            </div>
            {current && w.sessions.length > 0 && <WeekDays week={w} />}
          </li>
        );
      })}
    </ol>
  );
}
