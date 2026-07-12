import {
  Activity,
  CalendarRange,
  Dumbbell,
  History,
  MessageSquare,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Shown in the 4-slot mobile bottom nav; all items appear in the sidebar. */
  mobile: boolean;
}

/** Primary navigation destinations for the authenticated app shell (US10). */
export const NAV_ITEMS: readonly NavItem[] = [
  { href: "/dashboard", label: "Progress", icon: Activity, mobile: true },
  { href: "/coach", label: "Coach", icon: MessageSquare, mobile: true },
  { href: "/plan", label: "Plan", icon: CalendarRange, mobile: true },
  { href: "/activities", label: "Activities", icon: History, mobile: false },
  { href: "/exercises", label: "Exercises", icon: Dumbbell, mobile: false },
  { href: "/settings", label: "Settings", icon: Settings, mobile: true },
] as const;

/** The compact set rendered by the mobile bottom nav. */
export const MOBILE_NAV_ITEMS: readonly NavItem[] = NAV_ITEMS.filter(
  (item) => item.mobile,
);

/** A nav item is active when the path matches it or is nested beneath it. */
export function isActiveRoute(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}
