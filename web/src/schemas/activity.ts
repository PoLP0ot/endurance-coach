import { z } from "zod";

export const activitySummarySchema = z.object({
  id: z.string(),
  activity_type: z.string(),
  name: z.string().nullable(),
  start_time: z.string(),
  distance_m: z.number().nullable(),
  duration_s: z.number().nullable(),
  avg_hr: z.number().nullable(),
  tss: z.number().nullable(),
});

export const activityPageSchema = z.object({
  items: z.array(activitySummarySchema),
  next_cursor: z.string().nullable(),
  windowed: z.boolean(),
});

export type ActivitySummary = z.infer<typeof activitySummarySchema>;
export type ActivityPage = z.infer<typeof activityPageSchema>;
