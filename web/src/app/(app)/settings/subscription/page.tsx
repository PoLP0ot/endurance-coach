import Link from "next/link";
import { SubscriptionView } from "@/components/subscription/subscription-view";

export default function SubscriptionPage() {
  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/settings"
          className="text-sm text-muted-foreground underline-offset-4 hover:underline"
        >
          ← Settings
        </Link>
        <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight">
          Subscription
        </h1>
      </div>
      <SubscriptionView />
    </div>
  );
}
