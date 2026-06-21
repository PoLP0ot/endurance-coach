import Link from "next/link";
import { Activity } from "lucide-react";

const SECTION_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
] as const;

const PAGE_LINKS = [
  { href: "/privacy", label: "Privacy Policy" },
  { href: "/terms", label: "Terms of Service" },
  { href: "/contact", label: "Contact" },
] as const;

/** Marketing footer with section + legal links and copyright (1.9). */
export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="container flex flex-col gap-8 py-12 md:flex-row md:items-start md:justify-between">
        <Link href="/" className="flex items-center gap-2 font-display font-bold">
          <Activity className="h-5 w-5 text-accent" aria-hidden />
          Endurance Coach
        </Link>
        <nav
          aria-label="Footer"
          className="flex flex-col gap-8 sm:flex-row sm:gap-16"
        >
          <ul className="space-y-2 text-sm text-muted-foreground">
            {SECTION_LINKS.map(({ href, label }) => (
              <li key={href}>
                <Link href={href} className="hover:text-foreground">
                  {label}
                </Link>
              </li>
            ))}
          </ul>
          <ul className="space-y-2 text-sm text-muted-foreground">
            {PAGE_LINKS.map(({ href, label }) => (
              <li key={href}>
                <Link href={href} className="hover:text-foreground">
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
      <div className="container pb-8 text-sm text-muted-foreground">
        © 2026 Endurance Coach. All rights reserved.
      </div>
    </footer>
  );
}
