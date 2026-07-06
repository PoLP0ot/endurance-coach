import * as Sentry from "@sentry/nextjs";

// Inert without a DSN. Health-data app: never send PII or request bodies.
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  sendDefaultPii: false,
});
