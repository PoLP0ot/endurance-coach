import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format";
import { type PlanWeek } from "@/schemas/plan";

const PHASE_LABEL: Record<PlanWeek["phase"], string> = {
  base: "Base",
  build: "Build",
  peak: "Peak",
  taper: "Taper",
};

/** Week-by-week periodized plan timeline (US5). */
export function PlanTimeline({ weeks }: { weeks: PlanWeek[] }) {
  return (
    <ol className="divide-y divide-border rounded-md border border-border">
      {weeks.map((w) => (
        <li key={w.week} className="flex items-center justify-between gap-4 px-4 py-3">
          <div className="min-w-0">
            <p className="text-sm font-medium">
              Week {w.week}
              <span className="ml-2 text-xs text-muted-foreground">
                {formatDate(w.start_date)}
              </span>
            </p>
            <p className="truncate text-xs text-muted-foreground">{w.focus}</p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            {w.is_recovery && (
              <span className="rounded-sm bg-secondary px-1.5 py-0.5 text-[10px] uppercase text-muted-foreground">
                Recovery
              </span>
            )}
            <span
              className={cn(
                "rounded-sm px-1.5 py-0.5 text-[10px] uppercase",
                w.phase === "peak"
                  ? "bg-accent/20 text-accent"
                  : "bg-secondary text-muted-foreground",
              )}
            >
              {PHASE_LABEL[w.phase]}
            </span>
            <span className="font-data text-sm tabular-nums">
              {w.target_tss.toFixed(0)}
              <span className="ml-1 text-xs text-muted-foreground">TSS</span>
            </span>
          </div>
        </li>
      ))}
    </ol>
  );
}
