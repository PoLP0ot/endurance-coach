import type { ThisWeek } from "@/schemas/dashboard";
import { formatDistance, formatDuration } from "@/lib/format";

interface Row {
  metric: string;
  now: string;
  last: string;
  delta: number;
}

/** "This Week at a Glance" — current week vs last week across key metrics (US2). */
export function WeekGlance({ data }: { data: ThisWeek }) {
  const { this_week: now, last_week: last } = data;
  const rows: Row[] = [
    {
      metric: "Distance",
      now: formatDistance(now.distance_m),
      last: formatDistance(last.distance_m),
      delta: now.distance_m - last.distance_m,
    },
    {
      metric: "Load",
      now: `${now.tss.toFixed(0)} TSS`,
      last: `${last.tss.toFixed(0)} TSS`,
      delta: now.tss - last.tss,
    },
    {
      metric: "Sessions",
      now: String(now.activity_count),
      last: String(last.activity_count),
      delta: now.activity_count - last.activity_count,
    },
    {
      metric: "Time",
      now: formatDuration(now.duration_s),
      last: formatDuration(last.duration_s),
      delta: now.duration_s - last.duration_s,
    },
  ];

  return (
    <section className="rounded border border-line bg-card">
      <div className="flex items-center justify-between border-b border-line px-5 py-3">
        <h2 className="font-display text-base font-semibold tracking-tight">
          This Week at a Glance
        </h2>
        <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
          vs last week
        </span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
            <th className="px-5 py-2 font-normal" />
            <th className="px-5 py-2 font-normal">This week</th>
            <th className="px-5 py-2 font-normal">Last week</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.metric} className="border-t border-line/60">
              <td className="px-5 py-2.5 font-medium text-ink">{r.metric}</td>
              <td className="px-5 py-2.5 tabular-nums text-ink">
                {r.now}
                {r.delta !== 0 && (
                  <span
                    className={`ml-1.5 font-mono text-[10px] ${r.delta > 0 ? "text-olive" : "text-muted-foreground"}`}
                  >
                    {r.delta > 0 ? "▲" : "▼"}
                  </span>
                )}
              </td>
              <td className="px-5 py-2.5 tabular-nums text-muted-foreground">
                {r.last}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
