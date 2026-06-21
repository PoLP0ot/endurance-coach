import type { Metadata } from "next";
import { AuthShell } from "@/components/auth/auth-shell";
import { SignupForm } from "@/components/auth/signup-form";

export const metadata: Metadata = {
  title: "Create your account — Endurance Coach",
};

export default function SignupPage() {
  return (
    <AuthShell
      title="Create your account"
      subtitle="Start your free trial. No credit card required."
    >
      <SignupForm />
    </AuthShell>
  );
}
