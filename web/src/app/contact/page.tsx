import type { Metadata } from "next";
import { LegalShell } from "@/components/marketing/legal-shell";

export const metadata: Metadata = { title: "Contact — Endurance Coach" };

export default function ContactPage() {
  return (
    <LegalShell title="Contact">
      <section>
        <p>
          We&apos;re a small team of athletes building the coach we wanted for
          ourselves. Every message is read by a human.
        </p>
      </section>
      <section>
        <h2>Support &amp; questions</h2>
        <p>
          Email{" "}
          <a
            className="text-primary underline-offset-4 hover:underline"
            href="mailto:support@endurancecoach.app"
          >
            support@endurancecoach.app
          </a>{" "}
          — we answer within one business day. Include the email address of your
          Endurance Coach account so we can help faster.
        </p>
      </section>
      <section>
        <h2>Billing</h2>
        <p>
          Subscriptions are billed by Paddle, our merchant of record. You can
          cancel any time from Settings → Subscription; for refund requests,
          email us and we&apos;ll sort it out with Paddle.
        </p>
      </section>
      <section>
        <h2>Privacy</h2>
        <p>
          Export or delete your data any time from Settings → Privacy &amp; data.
          For other privacy requests, use the same address.
        </p>
      </section>
    </LegalShell>
  );
}
