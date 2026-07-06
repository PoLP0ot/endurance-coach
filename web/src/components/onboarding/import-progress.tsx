import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

/** The import pipeline's stages, matched against backend progress labels. */
const STEPS = [
  { key: "activities", label: "Fetching activities" },
  { key: "health", label: "Syncing health data" },
  { key: "analyzing", label: "Analyzing metrics" },
  { key: "building", label: "Building your dashboard" },
] as const;

const MATCHERS: Record<(typeof STEPS)[number]["key"], RegExp> = {
  activities: /activit/i,
  health: /health/i,
  analyzing: /analyz|metric/i,
  building: /build|dashboard/i,
};

function activeIndex(label: string): number {
  const idx = STEPS.findIndex((s) => MATCHERS[s.key].test(label));
  return idx === -1 ? -1 : idx;
}

/**
 * The first minute with the product: the athlete just handed over their
 * Garmin credentials and waits ~30–60 s. Show the pipeline as a living
 * checklist driven by the real backend progress labels — never fake steps.
 */
export function ImportProgress({ label }: { label: string }) {
  const current = activeIndex(label);
  const known = current !== -1;

  return (
    <div role="status" aria-live="polite" className="mx-auto max-w-xs">
      <ol className="space-y-3">
        {STEPS.map((step, i) => {
          const state = !known
            ? i === 0
              ? "active"
              : "upcoming"
            : i < current
              ? "done"
              : i === current
                ? "active"
                : "upcoming";
          return (
            <li
              key={step.key}
              data-state={state}
              aria-current={state === "active" ? "step" : undefined}
              className={cn(
                "flex items-center gap-3 text-sm transition-colors",
                state === "done" && "text-olive",
                state === "active" && "font-semibold text-ink",
                state === "upcoming" && "text-muted-foreground/60",
              )}
            >
              <span
                className={cn(
                  "grid h-6 w-6 shrink-0 place-items-center rounded-full border",
                  state === "done" && "border-olive/40 bg-olive/10",
                  state === "active" && "border-primary/50",
                  state === "upcoming" && "border-line",
                )}
              >
                {state === "done" ? (
                  <Check className="h-3.5 w-3.5" aria-hidden />
                ) : state === "active" ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" aria-hidden />
                ) : (
                  <span className="h-1 w-1 rounded-full bg-line" aria-hidden />
                )}
              </span>
              {step.label}
            </li>
          );
        })}
      </ol>
      {!known && (
        <p className="mt-4 text-center font-mono text-[11px] text-muted-foreground">
          {label}
        </p>
      )}
    </div>
  );
}
