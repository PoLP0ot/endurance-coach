import { z } from "zod";

export const planWeekSchema = z.object({
  week: z.number(),
  start_date: z.string(),
  phase: z.enum(["base", "build", "peak", "taper"]),
  is_recovery: z.boolean(),
  target_tss: z.number(),
  focus: z.string(),
});

export const planSchema = z.object({
  id: z.string(),
  goal: z.string(),
  weeks: z.number(),
  start_date: z.string(),
  status: z.string(),
  structure: z.object({ goal: z.string(), weeks: z.array(planWeekSchema) }),
  narrative: z.string().nullable(),
  model: z.string().nullable(),
});

export const currentPlanSchema = z.object({ plan: planSchema.nullable() });

export type Plan = z.infer<typeof planSchema>;
export type PlanWeek = z.infer<typeof planWeekSchema>;

export const GOALS = [
  { value: "marathon", label: "Marathon" },
  { value: "weight_loss", label: "Weight loss" },
  { value: "hyrox", label: "Hyrox" },
  { value: "triathlon", label: "Triathlon" },
  { value: "health", label: "Health" },
] as const;
