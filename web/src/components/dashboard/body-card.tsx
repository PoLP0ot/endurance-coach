import type { Health } from "@/schemas/dashboard";
import { cn } from "@/lib/utils";

interface Tile {
  key: string;
  label: string;
  value: string;
  hint: string;
}

/** Goal-aware 7-day body snapshot from imported daily health (A13 / 2.6). */
export function BodyCard({ health }: { health: Health }) {
  const tiles: Tile[] = [
    health.hrv !== null && {
      key: "hrv",
      label: "HRV",
      value: `${health.hrv}`,
      hint: "ms · 7-day avg",
    },
    health.resting_hr !== null && {
      key: "resting_hr",
      label: "Resting HR",
      value: `${health.resting_hr}`,
      hint: "bpm · latest",
    },
    health.sleep_score !== null && {
      key: "sleep_score",
      label: "Sleep",
      value: `${health.sleep_score}`,
      hint: "score · 7-day avg",
    },
    health.steps !== null && {
      key: "steps",
      label: "Steps",
      value: health.steps.toLocaleString(),
      hint: "per day · avg",
    },
    health.body_battery !== null && {
      key: "body_battery",
      label: "Body Battery",
      value: `${health.body_battery}`,
      hint: "latest",
    },
    health.stress_avg !== null && {
      key: "stress_avg",
      label: "Stress",
      value: `${health.stress_avg}`,
      hint: "avg · 7-day",
    },
    health.weight_kg !== null && {
      key: "weight_kg",
      label: "Weight",
      value: `${health.weight_kg}`,
      hint: "kg · latest",
    },
  ].filter(Boolean) as Tile[];

  if (tiles.length === 0) return null;

  // Surface the goal's featured metric first.
  tiles.sort((a, b) =>
    a.key === health.feature ? -1 : b.key === health.feature ? 1 : 0,
  );

  return (
    <section className="rounded border border-line bg-card">
      <div className="flex items-center justify-between border-b border-line px-5 py-3">
        <h2 className="font-display text-base font-semibold tracking-tight">
          Your Body
        </h2>
        <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
          {health.days}-day · Garmin
        </span>
      </div>
      <div className="grid grid-cols-2 gap-px bg-line/60 sm:grid-cols-3">
        {tiles.map((t) => (
          <div
            key={t.key}
            className={cn(
              "bg-card p-4",
              t.key === health.feature && "ring-1 ring-inset ring-primary/40",
            )}
          >
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
              {t.label}
            </p>
            <p className="mt-1.5 font-display text-2xl font-semibold tabular-nums text-ink">
              {t.value}
            </p>
            <p className="mt-0.5 font-mono text-[10px] text-muted-foreground">
              {t.hint}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
