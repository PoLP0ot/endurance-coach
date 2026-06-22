"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { NAV_ITEMS, isActiveRoute } from "./nav-items";

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
      <aside className="hidden border-r border-border lg:flex lg:w-60 lg:flex-col lg:justify-between lg:p-4">
        <div>
          <Link
            href="/dashboard"
            className="block px-3 py-2 font-display text-lg font-semibold tracking-tight"
          >
            Endurance Coach
          </Link>
          <nav className="mt-6 flex flex-col gap-1">
            {NAV_ITEMS.map((item) => {
              const active = isActiveRoute(pathname, item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    active
                      ? "bg-secondary text-foreground"
                      : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground",
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
          className="justify-start text-muted-foreground"
          onClick={signOut}
        >
          <LogOut className="h-4 w-4" aria-hidden />
          Sign out
        </Button>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border px-4 py-3 lg:hidden">
          <span className="font-display text-base font-semibold tracking-tight">
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

        <nav className="fixed inset-x-0 bottom-0 z-10 grid grid-cols-4 border-t border-border bg-background lg:hidden">
          {NAV_ITEMS.map((item) => {
            const active = isActiveRoute(pathname, item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex min-h-[56px] flex-col items-center justify-center gap-1 py-2 text-xs",
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
