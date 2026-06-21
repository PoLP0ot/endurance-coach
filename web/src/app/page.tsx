import { Activity, Brain, LineChart, Watch } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const features = [
  {
    icon: Watch,
    title: "Connect your Garmin",
    body: "One-tap import of your runs, rides and health data. We do the heavy lifting.",
  },
  {
    icon: Brain,
    title: "Coach-first, not data-first",
    body: "We translate raw numbers into a clear answer: where you are, and what to do next.",
  },
  {
    icon: LineChart,
    title: "Metrics you can trust",
    body: "TSS, fitness and form are computed deterministically — never invented by an AI.",
  },
  {
    icon: Activity,
    title: "Adaptive plans",
    body: "Training plans that flex with your recovery and push straight to your watch.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen">
      <section className="container flex flex-col items-center gap-8 py-24 text-center md:py-32">
        <span className="rounded-full border border-border bg-secondary/50 px-4 py-1.5 text-sm text-muted-foreground">
          AI coaching for serious endurance athletes
        </span>
        <h1 className="max-w-3xl font-display text-5xl font-bold tracking-tight md:text-6xl">
          Your data, finally translated into{" "}
          <span className="text-primary">coaching</span>.
        </h1>
        <p className="max-w-xl text-lg text-muted-foreground">
          Endurance Coach connects to your Garmin and tells you what every run
          means for your goal — then adapts the plan to get you there.
        </p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Button size="lg">Get started</Button>
          <Button size="lg" variant="outline">
            See how it works
          </Button>
        </div>
      </section>

      <section className="container grid gap-6 pb-24 md:grid-cols-2 lg:grid-cols-4">
        {features.map(({ icon: Icon, title, body }) => (
          <Card key={title}>
            <CardHeader>
              <Icon className="mb-2 h-8 w-8 text-accent" aria-hidden />
              <CardTitle className="font-display">{title}</CardTitle>
              <CardDescription>{body}</CardDescription>
            </CardHeader>
            <CardContent />
          </Card>
        ))}
      </section>
    </main>
  );
}
