import { z } from "zod";

export const signalSchema = z.object({
  key: z.string(),
  eyebrow: z.string(),
  question: z.string(),
  points: z.array(z.number()).nullable(),
  color: z.string().nullable(),
  interpretation: z.string(),
});

export const signalsResponseSchema = z.object({
  signals: z.array(signalSchema),
});

export type Signal = z.infer<typeof signalSchema>;
