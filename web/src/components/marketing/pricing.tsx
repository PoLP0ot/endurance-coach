"use client";

import { useState } from "react";
import Link from "next/link";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const FREE_FEATURES = [
  "Dashboard analytics",
  "Last 30 days of history",
  "Basic training metrics",
] as const;

const PREMIUM_FEATURES = [
  "Full activity history",
  "AI Coach — unlimited chat",
  "Adaptive training plans",
  "Weekly email reports",
] as const;

type Billing = "monthly" | "annual";

/** Pricing section with a monthly/annual billing toggle (1.6). */
export function Pricing() {
  const [billing, setBilling] = useState<Billing>("monthly");
  const premiumPrice = billing === "monthly" ? "$8" : "$79";
  const premiumSuffix = billing === "monthly" ? "/mo" : "/yr";

  return (
    <section id="pricing" className="container scroll-mt-20 py-20">
      <h2 className="text-center font-display text-3xl font-bold tracking-tight">
        Simple pricing
      </h2>

      <div
        role="group"
        aria-label="Billing period"
        className="mx-auto mt-8 flex w-fit items-center gap-1 rounded-md border border-border p-1"
      >
        <Button
          variant={billing === "monthly" ? "secondary" : "ghost"}
          size="sm"
          aria-pressed={billing === "monthly"}
          onClick={() => setBilling("monthly")}
        >
          Monthly
        </Button>
        <Button
          variant={billing === "annual" ? "secondary" : "ghost"}
          size="sm"
          aria-pressed={billing === "annual"}
          onClick={() => setBilling("annual")}
        >
          Annual
          <span className="ml-2 rounded-sm bg-accent/15 px-1.5 py-0.5 text-xs text-accent">
            Save 18%
          </span>
        </Button>
      </div>

      <div className="mx-auto mt-10 grid max-w-3xl gap-6 md:grid-cols-2">
        <PlanCard
          name="Free"
          price="$0"
          suffix="forever"
          features={FREE_FEATURES}
          cta="Start Free"
        />
        <PlanCard
          name="Premium"
          price={premiumPrice}
          suffix={premiumSuffix}
          features={PREMIUM_FEATURES}
          cta={`Go Premium — ${premiumPrice}${premiumSuffix}`}
          highlighted
        />
      </div>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        10x cheaper than a human coach ($100–300/mo). Cancel anytime.
      </p>
    </section>
  );
}

interface PlanCardProps {
  name: string;
  price: string;
  suffix: string;
  features: readonly string[];
  cta: string;
  highlighted?: boolean;
}

function PlanCard({
  name,
  price,
  suffix,
  features,
  cta,
  highlighted = false,
}: PlanCardProps) {
  return (
    <div
      className={cn(
        "flex flex-col rounded-md border border-border bg-card p-6",
        highlighted && "border-accent",
      )}
    >
      <h3 className="font-display text-lg font-semibold">{name}</h3>
      <p className="mt-2">
        <span className="font-display text-4xl font-bold tabular-nums">
          {price}
        </span>{" "}
        <span className="text-sm text-muted-foreground">{suffix}</span>
      </p>
      <ul className="mt-6 flex-1 space-y-2 text-sm">
        {features.map((feature) => (
          <li key={feature} className="flex items-center gap-2">
            <Check className="h-4 w-4 text-accent" aria-hidden />
            {feature}
          </li>
        ))}
      </ul>
      <Button
        asChild
        className="mt-6"
        variant={highlighted ? "default" : "outline"}
      >
        <Link href="/signup">{cta}</Link>
      </Button>
    </div>
  );
}
