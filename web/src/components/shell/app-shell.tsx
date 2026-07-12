"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { MOBILE_NAV_ITEMS, NAV_ITEMS, isActiveRoute } from "./nav-items";

/**
 * Authenticated app shell (US10): a desktop sidebar (≥1024px) and a mobile
 * bottom nav share one nav config. Highlights the active route and signs out.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() ?? "";
  const router = useRouter();

  const signOut = async () => {
    await createClient().auth.signOut();
    router.push("/login");
  };

  return (
    <div className="min-h-screen lg:flex">
      <aside className="hidden border-r border-line lg:flex lg:w-60 lg:flex-col lg:justify-between lg:py-5">
        <div>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-5 pb-6 font-display text-lg font-semibold tracking-tight text-ink"
          >
            <span className="grid h-6 w-6 place-items-center rounded-full border border-ink">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
            </span>
            Endurance Coach
          </Link>
          <nav className="flex flex-col">
            {NAV_ITEMS.map((item) => {
              const active = isActiveRoute(pathname, item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 border-l-2 px-5 py-2.5 font-display text-sm font-semibold transition-colors",
                    active
                      ? "border-primary bg-primary/[0.07] text-ink"
                      : "border-transparent text-muted-foreground hover:bg-secondary hover:text-ink",
                  )}
                >
                  <Icon className="h-4 w-4" aria-hidden />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="mx-3 justify-start text-muted-foreground hover:text-ink"
          onClick={signOut}
        >
          <LogOut className="h-4 w-4" aria-hidden />
          Sign out
        </Button>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-line px-4 py-3 lg:hidden">
          <span className="flex items-center gap-2 font-display text-base font-semibold tracking-tight text-ink">
            <span className="grid h-5 w-5 place-items-center rounded-full border border-ink">
              <span className="h-1 w-1 rounded-full bg-primary" />
            </span>
            Endurance Coach
          </span>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Sign out"
            onClick={signOut}
          >
            <LogOut className="h-4 w-4" aria-hidden />
          </Button>
        </header>

        <main className="flex-1 px-4 py-6 pb-24 lg:px-8 lg:pb-8">{children}</main>

        <nav className="fixed inset-x-0 bottom-0 z-10 grid h-[62px] grid-cols-5 border-t border-line bg-card/95 backdrop-blur lg:hidden">
          {MOBILE_NAV_ITEMS.map((item) => {
            const active = isActiveRoute(pathname, item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex flex-col items-center justify-center gap-1 font-display text-[10.5px] font-semibold transition-colors",
                  active ? "text-primary" : "text-muted-foreground",
                )}
              >
                <Icon className="h-5 w-5" aria-hidden />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
