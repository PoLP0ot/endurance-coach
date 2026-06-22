"use client";

import { useCallback, useEffect, useState } from "react";
import { Check } from "lucide-react";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  checkoutConfigSchema,
  subscriptionStatusSchema,
  type SubscriptionStatus,
} from "@/schemas/subscription";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";

const PREMIUM_FEATURES = [
  "Full training history",
  "Unlimited AI coach chat",
  "AI activity analysis",
  "Adaptive training plans",
  "Weekly coaching email",
];

type Phase = "loading" | "error" | "ready";

interface PaddleCheckout {
  open: (opts: Record<string, unknown>) => void;
}
declare global {
  interface Window {
    Paddle?: { Checkout: PaddleCheckout };
  }
}

/** Subscription management + upgrade via Paddle checkout (US8). */
export function SubscriptionView() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [status, setStatus] = useState<SubscriptionStatus | null>(null);
  const [upgrading, setUpgrading] = useState(false);

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/subscription/status", { token });
      setStatus(subscriptionStatusSchema.parse(raw));
      setPhase("ready");
    } catch {
      setPhase("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const upgrade = async () => {
    setUpgrading(true);
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/subscription/checkout", {
        method: "POST",
        token,
      });
      const config = checkoutConfigSchema.parse(raw);
      if (typeof window !== "undefined" && window.Paddle) {
        window.Paddle.Checkout.open({
          items: [{ priceId: config.price_id, quantity: 1 }],
          customer: config.customer_email
            ? { email: config.customer_email }
            : undefined,
          customData: config.custom_data,
        });
      } else {
        toast.info("Checkout is opening — complete your upgrade in the popup.");
      }
    } catch {
      toast.error("We couldn't start checkout. Please try again.");
    } finally {
      setUpgrading(false);
    }
  };

  if (phase === "loading") {
    return <LoadingState rows={3} label="Loading your subscription" />;
  }
  if (phase === "error" || !status) {
    return (
      <ErrorState
        message="We couldn't load your subscription."
        onRetry={() => void load()}
      />
    );
  }

  if (status.is_premium) {
    return (
      <div className="rounded-md border border-border p-6">
        <p className="font-display text-lg font-semibold">You&apos;re on Premium</p>
        <p className="mt-1 text-sm text-muted-foreground">
          {status.current_period_end
            ? `Renews ${new Date(status.current_period_end).toLocaleDateString()}.`
            : "Thanks for supporting your training."}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border p-6">
      <p className="font-display text-lg font-semibold">Upgrade to Premium</p>
      <p className="mt-1 text-sm text-muted-foreground">$8/month · cancel anytime</p>
      <ul className="mt-4 space-y-2">
        {PREMIUM_FEATURES.map((f) => (
          <li key={f} className="flex items-center gap-2 text-sm">
            <Check className="h-4 w-4 text-accent" aria-hidden />
            {f}
          </li>
        ))}
      </ul>
      <Button className="mt-6" onClick={upgrade} disabled={upgrading}>
        {upgrading ? "Starting checkout…" : "Upgrade to Premium"}
      </Button>
    </div>
  );
}
