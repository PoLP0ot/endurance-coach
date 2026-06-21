import type { Metadata } from "next";
import { AuthShell } from "@/components/auth/auth-shell";
import { LoginForm } from "@/components/auth/login-form";

export const metadata: Metadata = {
  title: "Welcome back — Endurance Coach",
};

export default function LoginPage() {
  return (
    <AuthShell title="Welcome back">
      <LoginForm />
    </AuthShell>
  );
}
