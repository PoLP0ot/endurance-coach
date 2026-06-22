import type { Metadata } from "next";
import { AuthShell } from "@/components/auth/auth-shell";
import { ConnectGarmin } from "@/components/onboarding/connect-garmin";

export const metadata: Metadata = {
  title: "Connect your Garmin — Endurance Coach",
};

export default function OnboardingPage() {
  return (
    <AuthShell
      title="Connect your Garmin account"
      subtitle="We'll import your activity history, health metrics, and training data. This takes about 30 seconds."
    >
      <ConnectGarmin />
    </AuthShell>
  );
}
