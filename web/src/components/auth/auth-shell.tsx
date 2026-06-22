import Link from "next/link";
import { Activity } from "lucide-react";

interface AuthShellProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

/** Centered, full-height card layout shared by the auth screens (prototype: paper card). */
export function AuthShell({ title, subtitle, children }: AuthShellProps) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 py-12">
      <Link
        href="/"
        className="flex items-center justify-center gap-2 font-display font-semibold tracking-tight text-ink"
      >
        <Activity className="h-5 w-5 text-accent" aria-hidden />
        Endurance Coach
      </Link>
      <div className="w-full max-w-[420px] rounded border border-line bg-card px-[34px] py-9 shadow-sm">
        <div className="mb-6 space-y-1 text-center">
          <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-muted-foreground">{subtitle}</p>
          )}
        </div>
        {children}
      </div>
    </main>
  );
}
