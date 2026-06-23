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

export const goalSchema = z.object({
  race_name: z.string().nullable(),
  race_date: z.string(),
  days_to_go: z.number(),
  weeks_to_go: z.number(),
  progress_pct: z.number(),
  is_past: z.boolean(),
});

export const weekSummarySchema = z.object({
  activity_count: z.number(),
  distance_m: z.number(),
  tss: z.number(),
  duration_s: z.number(),
});

export const thisWeekSchema = z.object({
  this_week: weekSummarySchema,
  last_week: weekSummarySchema,
  week_start: z.string(),
});

export const dashboardSchema = z.object({
  goal: goalSchema.nullable(),
  this_week: thisWeekSchema,
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
export type Goal = z.infer<typeof goalSchema>;
export type ThisWeek = z.infer<typeof thisWeekSchema>;
