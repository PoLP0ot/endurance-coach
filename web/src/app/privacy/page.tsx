import type { Metadata } from "next";
import { LegalShell } from "@/components/marketing/legal-shell";

export const metadata: Metadata = { title: "Privacy Policy — Endurance Coach" };

export default function PrivacyPage() {
  return (
    <LegalShell title="Privacy Policy" updated="July 6, 2026">
      <section>
        <h2>What we collect</h2>
        <p>
          To coach you, we process training and health data imported from your
          Garmin account: activities (GPS routes, pace, heart rate, power),
          daily health metrics (resting heart rate, HRV, sleep, steps, stress,
          body battery, weight), plus your account email, goal settings and your
          conversations with the coach.
        </p>
      </section>
      <section>
        <h2>How we use it</h2>
        <p>
          Exclusively to provide the service: computing your training metrics,
          generating coaching narratives and plans, and sending the emails you
          opt into. We do not sell your data, we do not use it for advertising,
          and we do not train AI models on it.
        </p>
      </section>
      <section>
        <h2>Where it lives and who processes it</h2>
        <ul>
          <li><strong>Supabase</strong> (EU region) — database and authentication.</li>
          <li><strong>OpenAI</strong> — coaching narration. It receives computed training facts and your chat messages, not your raw Garmin archive.</li>
          <li><strong>Paddle</strong> — payments (merchant of record). We never see your card details.</li>
          <li><strong>Resend</strong> — transactional and weekly coaching emails, if you opt in.</li>
        </ul>
        <p>
          Your Garmin credentials are used once to establish a session; the
          resulting token is stored encrypted at rest (Fernet). Your password is
          never stored.
        </p>
      </section>
      <section>
        <h2>Your rights (GDPR)</h2>
        <p>
          Self-service, no email required: you can export everything we hold
          about you (JSON) and delete your account and all associated data from
          Settings → Privacy &amp; data. Deletion is immediate, cascades through
          activities, health data, chats, plans and analyses, and is recorded in
          an anonymised audit log. For anything else (rectification, objection,
          portability), write to us and we respond within 30 days.
        </p>
      </section>
      <section>
        <h2>Retention</h2>
        <p>
          We keep your data for as long as your account exists. Disconnecting
          Garmin stops new imports but keeps history; deleting your account
          removes everything.
        </p>
      </section>
      <section>
        <h2>Contact</h2>
        <p>
          Data controller: Endurance Coach. Privacy questions:{" "}
          <a className="text-primary underline-offset-4 hover:underline" href="mailto:support@endurancecoach.app">support@endurancecoach.app</a>.
        </p>
      </section>
    </LegalShell>
  );
}
