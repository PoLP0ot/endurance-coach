import Link from "next/link";
import { Activity } from "lucide-react";

interface AuthShellProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

/** Centered, full-height card layout shared by the auth screens. */
export function AuthShell({ title, subtitle, children }: AuthShellProps) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <Link
          href="/"
          className="flex items-center justify-center gap-2 font-display font-bold"
        >
          <Activity className="h-5 w-5 text-accent" aria-hidden />
          Endurance Coach
        </Link>
        <div className="space-y-1 text-center">
          <h1 className="font-display text-2xl font-bold tracking-tight">
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
