"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const FAQ_ITEMS = [
  {
    q: "Is my Garmin data safe?",
    a: "Yes. Your data is encrypted at rest and in transit. We never sell your data. We're GDPR compliant, and you can export or delete your data anytime.",
  },
  {
    q: "How is this different from Garmin Coach?",
    a: "Garmin Coach offers static, pre-built plans. Our AI coach analyzes YOUR actual data, adapts daily, and you can have a conversation with it. It's like a human coach, powered by AI.",
  },
  {
    q: "Do I need a Garmin watch?",
    a: "Currently, yes — we start with Garmin integration. COROS, Polar, Suunto, and Strava import are coming in V2.",
  },
  {
    q: "Can I import from Strava too?",
    a: "Not yet — Strava import is planned for V2. For now, connect your Garmin directly.",
  },
  {
    q: "What's included in the free plan?",
    a: "Full dashboard analytics for the last 30 days, basic metrics, and your weekly training-load trend. Premium unlocks unlimited history, the AI coach, and training plans.",
  },
  {
    q: "Can I cancel anytime?",
    a: "Yes. Cancel with one click, no questions asked. Your data stays accessible in read-only mode.",
  },
] as const;

/** Single-open FAQ accordion (1.8). */
export function Faq() {
  return (
    <section id="faq" className="container scroll-mt-20 py-20">
      <h2 className="text-center font-display text-3xl font-bold tracking-tight">
        Frequently asked questions
      </h2>
      <Accordion
        type="single"
        collapsible
        className="mx-auto mt-10 max-w-2xl"
      >
        {FAQ_ITEMS.map((item, index) => (
          <AccordionItem key={item.q} value={`item-${index}`}>
            <AccordionTrigger>{item.q}</AccordionTrigger>
            <AccordionContent>{item.a}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  );
}
