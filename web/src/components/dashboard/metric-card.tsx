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
    <div className="rounded-md border border-border p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p className="mt-2 flex items-baseline gap-1">
        <span className={cn("font-data text-3xl font-semibold", accentClassName)}>
          {value}
        </span>
        {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
      </p>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}
