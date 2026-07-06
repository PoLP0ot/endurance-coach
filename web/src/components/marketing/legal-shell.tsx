import Link from "next/link";
import { Activity } from "lucide-react";
import { SiteFooter } from "./site-footer";

/** Shared frame for legal/static pages: brand header, prose column, footer. */
export function LegalShell({
  title,
  updated,
  children,
}: {
  title: string;
  updated?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-line">
        <div className="container flex h-14 items-center">
          <Link href="/" className="flex items-center gap-2 font-display font-bold">
            <Activity className="h-5 w-5 text-accent" aria-hidden />
            Endurance Coach
          </Link>
        </div>
      </header>
      <main className="container max-w-3xl flex-1 py-12">
        <h1 className="font-display text-3xl font-semibold tracking-tight">
          {title}
        </h1>
        {updated && (
          <p className="mt-2 font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
            Last updated {updated}
          </p>
        )}
        <div className="mt-8 space-y-6 text-[15px] leading-relaxed text-ink-soft [&_h2]:font-display [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-ink [&_ul]:list-disc [&_ul]:space-y-1.5 [&_ul]:pl-5">
          {children}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
