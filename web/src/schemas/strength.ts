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

export const loggedSetSchema = z.object({
  exercise_id: z.string(),
  set_index: z.number(),
  weight_kg: z.number().nullable(),
  reps: z.number(),
  rpe: z.number().nullable(),
});

export const sessionSummarySchema = z.object({
  week: z.number(),
  day: z.number(),
  title: z.string(),
  sets_prescribed: z.number(),
  sets_logged: z.number(),
  volume_kg: z.number(),
  completed: z.boolean(),
});

export const suggestionSchema = z.object({
  weight_kg: z.number().nullable(),
  last: z
    .object({ weight_kg: z.number().nullable(), reps: z.number() })
    .nullable(),
});

export const sessionLogsSchema = z.object({
  sets: z.array(loggedSetSchema),
  summary: sessionSummarySchema,
  suggestions: z.record(z.string(), suggestionSchema).default({}),
});

export const exerciseHistorySchema = z.object({
  exercises: z.array(
    z.object({
      exercise_id: z.string(),
      name: z.string(),
      pr_weight_kg: z.number().nullable(),
      last_weight_kg: z.number().nullable(),
      last_reps: z.number(),
      sets_logged: z.number(),
    }),
  ),
});

export type Suggestion = z.infer<typeof suggestionSchema>;
export type ExerciseHistory = z.infer<typeof exerciseHistorySchema>;

export type SessionSummary = z.infer<typeof sessionSummarySchema>;
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
