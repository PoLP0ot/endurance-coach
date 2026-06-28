import type { GoalVariant } from "@/schemas/dashboard";
import { MetricCard } from "./metric-card";

const TITLE: Record<string, string> = {
  marathon: "Race readiness",
  triathlon: "Three-sport balance",
  hyrox: "Run / strength balance",
  weight_loss: "Fat-loss signals",
  health: "Health signals",
};

/** Goal-specific metric tiles from the backend goal definition (Phase D). */
export function GoalVariantPanels({ variant }: { variant: GoalVariant }) {
  if (variant.panels.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
        {TITLE[variant.kind] ?? "Your metrics"}
      </h2>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        {variant.panels.map((p) => (
          <MetricCard
            key={p.label}
            label={p.label}
            value={String(p.value)}
            unit={p.unit || undefined}
            hint={p.hint || undefined}
          />
        ))}
      </div>
    </section>
  );
}
