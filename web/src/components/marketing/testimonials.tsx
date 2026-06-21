import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const FOUNDER_QUOTE = {
  quote:
    "I built Endurance Coach because I was tired of exporting my Garmin data to ChatGPT every week. Now it happens automatically — and it actually understands my training.",
  author: "Thomas, founder & runner",
} as const;

/**
 * Pre-launch testimonials variant: a single founder quote plus an
 * early-access call-to-action (1.7).
 */
export function Testimonials() {
  return (
    <section className="container py-20">
      <h2 className="text-center font-display text-3xl font-bold tracking-tight">
        From the people building it
      </h2>
      <div className="mx-auto mt-10 grid max-w-3xl gap-6 md:grid-cols-2">
        <Card>
          <CardContent className="pt-6">
            <blockquote className="text-sm">
              &ldquo;{FOUNDER_QUOTE.quote}&rdquo;
            </blockquote>
            <p className="mt-4 text-sm font-medium text-muted-foreground">
              — {FOUNDER_QUOTE.author}
            </p>
          </CardContent>
        </Card>
        <Card className="border-accent">
          <CardContent className="flex flex-col items-start gap-4 pt-6">
            <p className="font-display text-lg font-semibold">
              Be one of the first
            </p>
            <p className="text-sm text-muted-foreground">
              We&apos;re onboarding our first cohort of athletes now. Join early
              and help shape the coach.
            </p>
            <Button asChild>
              <Link href="/signup">Get early access</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
