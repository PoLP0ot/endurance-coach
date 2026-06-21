import { Link2, LayoutDashboard, Bot } from "lucide-react";

const STEPS = [
  {
    icon: Link2,
    title: "Connect Garmin",
    body: "Link your Garmin account in 2 clicks. We import your entire history automatically.",
  },
  {
    icon: LayoutDashboard,
    title: "Get Your Dashboard",
    body: "See your training load, recovery, and trends in 30 seconds. Finally understand what your watch is telling you.",
  },
  {
    icon: Bot,
    title: "AI Coaching",
    body: "Your personal AI coach analyzes every run and tells you what to do tomorrow. No more guessing.",
  },
] as const;

/** Three-step "how it works" explainer (1.3). */
export function HowItWorks() {
  return (
    <section id="how-it-works" className="container scroll-mt-20 py-20">
      <h2 className="text-center font-display text-3xl font-bold tracking-tight">
        How it works
      </h2>
      <ol className="mt-12 grid gap-10 md:grid-cols-3">
        {STEPS.map(({ icon: Icon, title, body }, index) => (
          <li key={title} className="flex flex-col items-center text-center">
            <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-md border border-border text-accent">
              <Icon className="h-6 w-6" aria-hidden />
            </span>
            <span className="font-mono text-xs text-muted-foreground">
              Step {index + 1}
            </span>
            <h3 className="mt-1 font-display text-lg font-semibold">{title}</h3>
            <p className="mt-2 max-w-xs text-sm text-muted-foreground">{body}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
