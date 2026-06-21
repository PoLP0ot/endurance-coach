import { BarChart3, MessageSquare, CalendarRange } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const FEATURES = [
  {
    icon: BarChart3,
    title: "Understand Every Metric",
    body: "Training load (CTL/ATL/TSB), recovery scores, HRV trends. All the data Garmin collects — explained.",
    bullets: [
      "Fitness, fatigue and form on one chart",
      "Recovery score before every session",
      "Plain-language read on what each number means",
    ],
  },
  {
    icon: MessageSquare,
    title: "Ask Anything",
    body: '"Am I overtraining?" "When should I do my next speed workout?" Your coach knows YOUR data.',
    bullets: [
      "Chat that references your real activities",
      "Answers grounded in your numbers, never invented",
      "Available 24/7, instant replies",
    ],
  },
  {
    icon: CalendarRange,
    title: "Adaptive Plans",
    body: "Personalized plans for 5K to marathon that adapt to your actual performance and fatigue.",
    bullets: [
      "Rebuilds when life gets in the way",
      "Push this week's workouts to your watch",
      "Race-day projection that updates as you train",
    ],
  },
] as const;

/** Three-column feature grid, each with a concrete benefit list (1.4). */
export function Features() {
  return (
    <section id="features" className="container scroll-mt-20 py-20">
      <h2 className="text-center font-display text-3xl font-bold tracking-tight">
        Everything your watch should have told you
      </h2>
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, body, bullets }) => (
          <Card key={title}>
            <CardHeader>
              <Icon className="mb-2 h-8 w-8 text-accent" aria-hidden />
              <CardTitle className="font-display">{title}</CardTitle>
              <CardDescription>{body}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {bullets.map((bullet) => (
                  <li key={bullet} className="flex gap-2">
                    <span aria-hidden className="text-accent">
                      ·
                    </span>
                    {bullet}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
