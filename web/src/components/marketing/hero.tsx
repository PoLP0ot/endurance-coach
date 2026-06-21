import Link from "next/link";
import { ArrowDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeroProps {
  /** Live registered-user count; the social-proof line is shown only when > 0. */
  userCount?: number;
}

/** Landing hero: headline, subheadline and primary/secondary CTAs (1.2). */
export function Hero({ userCount = 0 }: HeroProps) {
  return (
    <section className="container flex flex-col items-center gap-6 py-20 text-center md:py-28">
      <h1 className="max-w-3xl font-display text-4xl font-bold tracking-tight md:text-6xl">
        Your Garmin data, finally decoded.
      </h1>
      <p className="max-w-2xl text-lg text-muted-foreground">
        AI coaching that analyzes your training data and tells you exactly what
        to do next — 10x cheaper than a human coach.
      </p>
      <div className="flex w-full flex-col items-center gap-3 sm:w-auto sm:flex-row">
        <Button asChild size="lg" className="w-full sm:w-auto">
          <Link href="/signup">Connect Your Garmin — It&apos;s Free</Link>
        </Button>
        <Button asChild size="lg" variant="ghost" className="w-full sm:w-auto">
          <Link href="#how-it-works">
            See how it works
            <ArrowDown className="h-4 w-4" aria-hidden />
          </Link>
        </Button>
      </div>
      {userCount > 0 ? (
        <p className="text-sm text-muted-foreground">
          Join {userCount}+ runners already training smarter
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">
          Now in early access — built for serious endurance athletes
        </p>
      )}
    </section>
  );
}
