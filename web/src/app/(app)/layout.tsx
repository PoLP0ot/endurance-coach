import { AppShell } from "@/components/shell/app-shell";

/** Layout for all authenticated app routes — wraps pages in the nav shell. */
export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return <AppShell>{children}</AppShell>;
}
