import type { GoalProgress } from "@/schemas/dashboard";
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

/** Goal headline + on-track band + projection vs target (2.1 generalized). */
export function GoalProgressBanner({ progress }: { progress: GoalProgress }) {
  const band = BAND[progress.on_track_band] ?? BAND.no_target;
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
      {(progress.projection || progress.target) && (
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 font-mono text-[11px] text-muted-foreground">
          {progress.projection != null && (
            <span>
              Projected <span className="text-ink">{progress.projection}</span>
            </span>
          )}
          {progress.target != null && (
            <span>
              Target <span className="text-ink">{progress.target}</span>
            </span>
          )}
          {progress.eta && (
            <span>
              ETA <span className="text-ink">{progress.eta}</span>
            </span>
          )}
        </div>
      )}
    </section>
  );
}
