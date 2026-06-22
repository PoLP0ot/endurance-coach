import { z } from "zod";

export const subscriptionStatusSchema = z.object({
  status: z.string(),
  is_premium: z.boolean(),
  current_period_end: z.string().nullable(),
});

export const checkoutConfigSchema = z.object({
  client_token: z.string(),
  price_id: z.string(),
  environment: z.string(),
  customer_email: z.string().nullable(),
  custom_data: z.object({ user_id: z.string() }),
});

export type SubscriptionStatus = z.infer<typeof subscriptionStatusSchema>;
export type CheckoutConfig = z.infer<typeof checkoutConfigSchema>;
