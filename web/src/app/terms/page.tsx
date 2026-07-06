import type { Metadata } from "next";
import { LegalShell } from "@/components/marketing/legal-shell";

export const metadata: Metadata = { title: "Terms of Service — Endurance Coach" };

export default function TermsPage() {
  return (
    <LegalShell title="Terms of Service" updated="July 6, 2026">
      <section>
        <h2>1. The service</h2>
        <p>
          Endurance Coach is an AI coaching platform for endurance athletes. It
          imports your Garmin data, computes training metrics deterministically,
          and generates coaching guidance, adaptive training plans and analysis.
          Coaching output is informational — it is not medical advice. Consult a
          physician before starting or changing a training program.
        </p>
      </section>
      <section>
        <h2>2. Your account</h2>
        <p>
          You need an account to use the service. You are responsible for keeping
          your credentials confidential and for all activity under your account.
          You must be at least 16 years old.
        </p>
      </section>
      <section>
        <h2>3. Garmin integration</h2>
        <p>
          We are not affiliated with Garmin. The integration uses your Garmin
          Connect credentials, stored encrypted, solely to import your training
          and health data and to push workouts you request. Garmin may change or
          restrict this access at any time; if that happens, import features may
          degrade or stop until we can restore them. You can disconnect Garmin at
          any time from Settings without losing already-imported data.
        </p>
      </section>
      <section>
        <h2>4. Subscriptions and billing</h2>
        <p>
          Premium is a monthly subscription sold through our merchant of record,
          Paddle, which handles payment, taxes and receipts. You can cancel your
          subscription at any time from Settings → Subscription; you keep premium
          access until the end of the paid period, and you will not be charged
          again. Refund requests are handled through Paddle in line with their
          buyer terms — contact us and we will help.
        </p>
      </section>
      <section>
        <h2>5. Your data</h2>
        <p>
          Your training data stays yours. You can export everything we hold or
          permanently delete your account and all associated data from Settings →
          Privacy &amp; data. See the Privacy Policy for details.
        </p>
      </section>
      <section>
        <h2>6. Acceptable use</h2>
        <ul>
          <li>Don&apos;t attempt to access other users&apos; data.</li>
          <li>Don&apos;t abuse, overload or reverse-engineer the service.</li>
          <li>Don&apos;t use the AI coach output to provide paid coaching to third parties.</li>
        </ul>
      </section>
      <section>
        <h2>7. Liability</h2>
        <p>
          The service is provided &quot;as is&quot;. To the maximum extent permitted by
          law, our liability is limited to the amount you paid us in the twelve
          months before the claim. Nothing in these terms limits liability that
          cannot be limited by law.
        </p>
      </section>
      <section>
        <h2>8. Changes and termination</h2>
        <p>
          We may update these terms; material changes will be announced in-app or
          by email at least 14 days in advance. You may stop using the service at
          any time. We may suspend accounts that break these terms.
        </p>
      </section>
      <section>
        <h2>9. Contact</h2>
        <p>
          Questions about these terms: <a className="text-primary underline-offset-4 hover:underline" href="mailto:support@endurancecoach.app">support@endurancecoach.app</a>.
        </p>
      </section>
    </LegalShell>
  );
}
