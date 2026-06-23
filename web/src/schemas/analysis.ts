import { z } from "zod";

export const streamSampleSchema = z.object({
  t: z.number().nullable(),
  hr: z.number().nullable(),
  pace_s_per_km: z.number().nullable(),
  elevation_m: z.number().nullable(),
  distance_m: z.number().nullable(),
});

export const streamSplitSchema = z.object({
  km: z.number(),
  duration_s: z.number(),
});

export const streamsSchema = z.object({
  samples: z.array(streamSampleSchema),
  route: z.array(z.array(z.number())),
  splits: z.array(streamSplitSchema),
  has_route: z.boolean(),
});

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
  streams: streamsSchema.nullable(),
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
export type ActivityStreams = z.infer<typeof streamsSchema>;
export type StreamSample = z.infer<typeof streamSampleSchema>;
