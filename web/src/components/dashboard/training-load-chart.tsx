"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { type LoadPoint } from "@/schemas/dashboard";

/** Fitness (CTL) / fatigue (ATL) / form (TSB) curve over the window (US2). */
export function TrainingLoadChart({ data }: { data: LoadPoint[] }) {
  return (
    <div className="rounded-md border border-border p-4">
      <p className="mb-3 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Training load — 6 weeks
      </p>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis dataKey="date" hide />
            <YAxis tick={{ fontSize: 11 }} width={32} />
            <Tooltip
              contentStyle={{ fontSize: 12 }}
              labelFormatter={(d) => String(d)}
            />
            <Area
              type="monotone"
              dataKey="ctl"
              name="Fitness"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary) / 0.15)"
            />
            <Line
              type="monotone"
              dataKey="atl"
              name="Fatigue"
              stroke="hsl(var(--destructive))"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="tsb"
              name="Form"
              stroke="hsl(var(--accent))"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
