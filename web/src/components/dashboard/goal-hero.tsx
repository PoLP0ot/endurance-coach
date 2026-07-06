import { Flag } from "lucide-react";
import type { Goal, GoalProgress } from "@/schemas/dashboard";
import { formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";

const BAND: Record<string, { label: string; chip: string }> = {
  ahead: { label: "Ahead", chip: "border-olive/40 bg-olive/10 text-olive" },
  on_track: { label: "On track", chip: "border-primary/40 bg-primary/10 text-primary" },
  at_risk: { label: "At risk", chip: "border-rust/40 bg-rust/10 text-rust" },
  off_track: {
    label: "Off track",
    chip: "border-destructive/40 bg-destructive/10 text-destructive",
  },
  no_target: { label: "No target set", chip: "border-line bg-secondary text-muted-foreground" },
};

/** Projection stats shared by both hero variants. */
function ProgressStats({
  progress,
  className,
}: {
  progress: GoalProgress;
  className?: string;
}) {
  if (progress.projection == null && progress.target == null) return null;
  return (
    <div className={cn("flex flex-wrap gap-x-6 gap-y-1 font-mono text-[11px]", className)}>
      {progress.projection != null && (
        <span>
          Projected <span className="font-semibold">{progress.projection}</span>
        </span>
      )}
      {progress.target != null && (
        <span>
          Target <span className="font-semibold">{progress.target}</span>
        </span>
      )}
    </div>
  );
}

/**
 * The single north-star card: race, countdown, journey progress and the
 * deterministic projection with its on-track band (US2 + 2.1, merged).
 */
export function GoalHero({
  goal,
  progress,
}: {
  goal: Goal | null;
  progress: GoalProgress;
}) {
  const band = BAND[progress.on_track_band] ?? BAND.no_target;

  if (!goal) {
    return (
      <section className="rounded border border-line bg-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="font-display text-base font-semibold tracking-tight text-ink">
            {progress.label ?? "Your goal"}
          </p>
          <span
            className={cn(
              "rounded-full border px-3 py-1 font-mono text-[10px] uppercase tracking-[0.12em]",
              band.chip,
            )}
          >
            {band.label}
          </span>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-ink-soft">{progress.headline}</p>
        <ProgressStats progress={progress} className="mt-3 text-muted-foreground [&_span_span]:text-ink" />
      </section>
    );
  }

  const pct = Math.max(0, Math.min(100, goal.progress_pct));
  const countdown = goal.is_past
    ? "Race day passed"
    : goal.days_to_go === 0
      ? "Race day is today"
      : `${goal.weeks_to_go} ${goal.weeks_to_go === 1 ? "week" : "weeks"} to go · ${goal.days_to_go} days`;

  return (
    <section className="rounded border border-line bg-ink p-5 text-paper">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="flex items-center gap-2 font-display text-xl font-semibold tracking-tight">
          <Flag className="h-4 w-4 text-primary" aria-hidden />
          {goal.race_name ?? "Your goal race"}
        </p>
        <span
          className={cn(
            "rounded-full border px-3 py-1 font-mono text-[10px] uppercase tracking-[0.12em]",
            band.chip,
          )}
        >
          {band.label}
        </span>
      </div>
      <p className="mt-1 font-mono text-[11px] uppercase tracking-[0.12em] text-paper/70">
        {formatDate(goal.race_date)} · {countdown}
      </p>
      {progress.headline && (
        <p className="mt-3 text-sm leading-relaxed text-paper/90">{progress.headline}</p>
      )}
      <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-paper/15">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] text-paper/70">
        <ProgressStats progress={progress} className="[&_span_span]:text-paper" />
        <span className="ml-auto">{pct}% of the journey</span>
      </div>
    </section>
  );
}
