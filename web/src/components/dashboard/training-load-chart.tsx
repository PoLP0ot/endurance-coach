"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { type LoadPoint } from "@/schemas/dashboard";

/** "Jun 1" from an ISO date, for compact axis ticks. */
function shortDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

/** Fitness (CTL) / fatigue (ATL) / form (TSB) curve over the window (US2). */
export function TrainingLoadChart({ data }: { data: LoadPoint[] }) {
  // ~6 evenly-spaced date ticks so the X axis stays readable.
  const tickInterval = Math.max(0, Math.floor(data.length / 6) - 1);

  return (
    <div className="rounded-md border border-border p-4">
      <p className="mb-3 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Training load — 6 weeks{" "}
        <span className="normal-case text-[10px]">(TSS units)</span>
      </p>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis
              dataKey="date"
              tickFormatter={shortDate}
              interval={tickInterval}
              tick={{ fontSize: 10 }}
              tickMargin={6}
              minTickGap={8}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              width={40}
              label={{
                value: "TSS",
                angle: -90,
                position: "insideLeft",
                style: { fontSize: 10, fill: "hsl(var(--muted-foreground))" },
              }}
            />
            <Tooltip
              contentStyle={{ fontSize: 12 }}
              labelFormatter={(d) => shortDate(String(d))}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 4 }}
              iconType="plainline"
            />
            <Area
              type="monotone"
              dataKey="ctl"
              name="Fitness (CTL)"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary) / 0.15)"
            />
            <Line
              type="monotone"
              dataKey="atl"
              name="Fatigue (ATL)"
              stroke="hsl(var(--destructive))"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="tsb"
              name="Form (TSB)"
              stroke="hsl(var(--accent))"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
