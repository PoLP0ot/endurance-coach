import { z } from "zod";

export const strengthItemSchema = z.object({
  slot: z.string(),
  exercise_id: z.string(),
  name: z.string(),
  equipment: z.string(),
  gif_url: z.string(),
  target_weight_kg: z.number().nullable(),
  sets: z.number(),
  reps: z.number(),
  rpe: z.number(),
  rest_sec: z.number(),
});

export const strengthSessionSchema = z.object({
  day: z.number(),
  focus: z.string(),
  title: z.string(),
  items: z.array(strengthItemSchema),
});

export const strengthWeekSchema = z.object({
  week: z.number(),
  start_date: z.string(),
  block: z.string(),
  is_deload: z.boolean(),
  focus: z.string(),
  sessions: z.array(strengthSessionSchema),
});

export const strengthStructureSchema = z.object({
  frequency: z.number(),
  level: z.string(),
  equipment: z.array(z.string()),
  blocks: z.array(z.object({ block: z.string(), weeks: z.number() })),
  weeks: z.array(strengthWeekSchema),
});

export const strengthPlanSchema = z.object({
  id: z.string(),
  goal_kind: z.string().nullable(),
  weeks: z.number(),
  frequency: z.number(),
  level: z.string(),
  equipment: z.array(z.string()),
  start_date: z.string(),
  status: z.string(),
  structure: strengthStructureSchema,
  narrative: z.string().nullable(),
});

export const strengthCurrentSchema = z.object({
  plan: strengthPlanSchema.nullable(),
});

export type StrengthItem = z.infer<typeof strengthItemSchema>;
export type StrengthSession = z.infer<typeof strengthSessionSchema>;
export type StrengthWeek = z.infer<typeof strengthWeekSchema>;
export type StrengthPlan = z.infer<typeof strengthPlanSchema>;

export const STRENGTH_LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
] as const;

export const STRENGTH_WEEK_OPTIONS = [8, 10, 12, 16] as const;
export const STRENGTH_FREQUENCY_OPTIONS = [2, 3, 4] as const;

/** Curated equipment choices for the setup form (dataset vocabulary). */
export const STRENGTH_EQUIPMENT_OPTIONS = [
  "body weight",
  "dumbbell",
  "barbell",
  "kettlebell",
  "cable",
  "resistance band",
  "smith machine",
  "leverage machine",
] as const;
