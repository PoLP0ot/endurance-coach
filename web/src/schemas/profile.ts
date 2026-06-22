import { z } from "zod";

export const profileSchema = z.object({
  id: z.string(),
  email: z.string().nullable(),
  display_name: z.string().nullable(),
  primary_goal: z.string().nullable(),
  units: z.enum(["metric", "imperial"]),
  weekly_email_opt_in: z.boolean(),
  onboarding_complete: z.boolean(),
  subscription_status: z.string(),
});

export type Profile = z.infer<typeof profileSchema>;
