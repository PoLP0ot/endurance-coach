import { z } from "zod";

export const exerciseSummarySchema = z.object({
  id: z.string(),
  name: z.string(),
  body_part: z.string(),
  target: z.string(),
  equipment: z.string(),
  image_url: z.string(),
  gif_url: z.string(),
});

export const exercisePageSchema = z.object({
  items: z.array(exerciseSummarySchema),
  next_cursor: z.string().nullable(),
});

export const exerciseDetailSchema = exerciseSummarySchema.extend({
  muscle_group: z.string().nullable(),
  secondary_muscles: z.array(z.string()),
  instructions: z.array(z.string()),
  attribution: z.string().nullable(),
});

export type ExerciseSummary = z.infer<typeof exerciseSummarySchema>;
export type ExercisePage = z.infer<typeof exercisePageSchema>;
export type ExerciseDetail = z.infer<typeof exerciseDetailSchema>;

// Fixed vocabularies of the seeded dataset (1,324 exercises).
export const BODY_PARTS = [
  "back",
  "cardio",
  "chest",
  "lower arms",
  "lower legs",
  "neck",
  "shoulders",
  "upper arms",
  "upper legs",
  "waist",
] as const;

export const EQUIPMENT_TYPES = [
  "assisted",
  "band",
  "barbell",
  "body weight",
  "bosu ball",
  "cable",
  "dumbbell",
  "elliptical machine",
  "ez barbell",
  "hammer",
  "kettlebell",
  "leverage machine",
  "medicine ball",
  "olympic barbell",
  "resistance band",
  "roller",
  "rope",
  "skierg machine",
  "sled machine",
  "smith machine",
  "stability ball",
  "stationary bike",
  "stepmill machine",
  "tire",
  "trap bar",
  "upper body ergometer",
  "weighted",
  "wheel roller",
] as const;
