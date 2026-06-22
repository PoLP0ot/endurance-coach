import { z } from "zod";

export const loadPointSchema = z.object({
  date: z.string(),
  ctl: z.number(),
  atl: z.number(),
  tsb: z.number(),
});

export const latestActivitySchema = z.object({
  id: z.string(),
  activity_type: z.string(),
  name: z.string().nullable(),
  start_time: z.string(),
  distance_m: z.number().nullable(),
  duration_s: z.number().nullable(),
  avg_hr: z.number().nullable(),
});

export const dashboardSchema = z.object({
  fitness: z.object({ ctl: z.number(), atl: z.number(), tsb: z.number() }),
  form: z.object({ band: z.string(), headline: z.string(), detail: z.string() }),
  recovery: z.number(),
  load_series: z.array(loadPointSchema),
  totals: z.object({
    activity_count: z.number(),
    total_distance_m: z.number(),
    window_days: z.number(),
  }),
  latest_activity: latestActivitySchema.nullable(),
});

export type Dashboard = z.infer<typeof dashboardSchema>;
export type LoadPoint = z.infer<typeof loadPointSchema>;
