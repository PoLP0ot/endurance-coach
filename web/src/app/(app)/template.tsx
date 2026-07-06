/**
 * Re-mounts on every route change inside the app shell, giving each page the
 * documented 200 ms fade-in (ux-direction § Interaction Standards). Motion is
 * disabled for users who prefer reduced motion (see globals.css).
 */
export default function AppTemplate({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return <div className="animate-page-in">{children}</div>;
}
