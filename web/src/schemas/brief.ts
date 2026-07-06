import { z } from "zod";

export const briefSchema = z.object({
  day: z.string(),
  headline: z.string().nullable(),
  body: z.string(),
  prescription: z.unknown().nullable(),
  model: z.string().nullable(),
});

export type Brief = z.infer<typeof briefSchema>;
