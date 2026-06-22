import { z } from "zod";

export const activityDetailSchema = z.object({
  id: z.string(),
  activity_type: z.string(),
  name: z.string().nullable(),
  start_time: z.string(),
  distance_m: z.number().nullable(),
  duration_s: z.number().nullable(),
  avg_hr: z.number().nullable(),
  max_hr: z.number().nullable(),
  elevation_gain_m: z.number().nullable(),
  avg_power_w: z.number().nullable(),
  tss: z.number().nullable(),
  streams: z.record(z.unknown()).nullable(),
});

export const analysisSchema = z.object({
  activity_id: z.string(),
  model: z.string(),
  facts: z.record(z.unknown()),
  narrative: z.string(),
  prompt_version: z.string(),
});

export type ActivityDetail = z.infer<typeof activityDetailSchema>;
export type ActivityAnalysis = z.infer<typeof analysisSchema>;
