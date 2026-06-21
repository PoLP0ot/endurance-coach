import Link from "next/link";
import { Activity } from "lucide-react";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
] as const;

/** Public marketing header with section anchors and a signup CTA. */
export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-display font-bold">
          <Activity className="h-5 w-5 text-accent" aria-hidden />
          Endurance Coach
        </Link>
        <nav aria-label="Main" className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {label}
            </Link>
          ))}
        </nav>
        <Button asChild size="sm">
          <Link href="/signup">Get Started — Free</Link>
        </Button>
      </div>
    </header>
  );
}
