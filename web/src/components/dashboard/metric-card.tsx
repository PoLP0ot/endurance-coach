import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  unit?: string;
  hint?: string;
  accentClassName?: string;
}

/** A single hero metric: big tabular number, unit, and a short hint (US2). */
export function MetricCard({
  label,
  value,
  unit,
  hint,
  accentClassName,
}: MetricCardProps) {
  return (
    <div className="rounded border border-line bg-card p-5">
      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </p>
      <p className="mt-3 flex items-baseline gap-1">
        <span
          className={cn(
            "font-display text-[40px] font-semibold leading-none tabular-nums",
            accentClassName,
          )}
        >
          {value}
        </span>
        {unit && (
          <span className="font-mono text-sm text-muted-foreground">{unit}</span>
        )}
      </p>
      {hint && (
        <p className="mt-2 font-mono text-[11px] text-muted-foreground">{hint}</p>
      )}
    </div>
  );
}
