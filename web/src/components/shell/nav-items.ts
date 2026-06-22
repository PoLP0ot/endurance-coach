import {
  Activity,
  CalendarRange,
  MessageSquare,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

/** Primary navigation destinations for the authenticated app shell (US10). */
export const NAV_ITEMS: readonly NavItem[] = [
  { href: "/dashboard", label: "Progress", icon: Activity },
  { href: "/coach", label: "Coach", icon: MessageSquare },
  { href: "/plan", label: "Plan", icon: CalendarRange },
  { href: "/settings", label: "Settings", icon: Settings },
] as const;

/** A nav item is active when the path matches it or is nested beneath it. */
export function isActiveRoute(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}
