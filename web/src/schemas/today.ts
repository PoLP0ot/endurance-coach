import { z } from "zod";

export const sessionSchema = z.object({
  day_index: z.number(),
  kind: z.string(),
  prescription: z.string(),
  target_tss: z.number(),
});

export const adherenceSchema = z.object({
  adherence_pct: z.number().nullable(),
  completed: z.number(),
  partial: z.number(),
  missed: z.number(),
  extras: z.number(),
});

export const todaySchema = z.object({
  status: z.string(),
  date: z.string(),
  week: z.number().optional(),
  phase: z.string().optional(),
  session: sessionSchema.nullable().optional(),
  is_rest: z.boolean().optional(),
  adherence: adherenceSchema.optional(),
  goal_band: z.string().nullable().optional(),
  headline: z.string().nullable().optional(),
});

export type Today = z.infer<typeof todaySchema>;
