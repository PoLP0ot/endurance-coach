import { test, type Page } from "@playwright/test";

/**
 * Capture auth-gated screens with a stubbed Supabase session + stubbed FastAPI
 * responses, so the loop can visually review them against the prototype without
 * a live backend. Run: pnpm exec playwright test authed
 * Output: e2e/__shots__/<name>-<project>.png
 */

const SUPABASE_REF = "jmxaosgnktbthzvvlwlh";
const FAR_FUTURE = 4102444800; // 2100-01-01

const fakeSession = {
  access_token: "stub-access-token",
  token_type: "bearer",
  expires_in: 3600,
  expires_at: FAR_FUTURE,
  refresh_token: "stub-refresh-token",
  user: {
    id: "00000000-0000-0000-0000-000000000001",
    aud: "authenticated",
    role: "authenticated",
    email: "marc@example.com",
    app_metadata: {},
    user_metadata: {},
  },
};

/** API fixtures keyed by request path (pathname only). */
const API_FIXTURES: Record<string, unknown> = {
  "/dashboard": {
    fitness: { ctl: 62, atl: 71, tsb: -9 },
    form: {
      band: "Productive",
      headline: "You're absorbing the load well",
      detail:
        "Fitness is climbing steadily and fatigue is where we want it 12 weeks out from Paris. Keep this rhythm and let Thursday's session land.",
    },
    recovery: 74,
    load_series: Array.from({ length: 21 }, (_, i) => ({
      date: `2026-06-${String(i + 1).padStart(2, "0")}`,
      ctl: 50 + i * 0.6,
      atl: 48 + Math.sin(i / 2) * 14 + i * 0.3,
      tsb: 4 + Math.cos(i / 2) * 8 - i * 0.1,
    })),
    totals: { activity_count: 14, total_distance_m: 132400, window_days: 30 },
    latest_activity: {
      id: "act-1",
      activity_type: "running",
      name: "Morning Run",
      start_time: "2026-06-21T07:12:00Z",
      distance_m: 16200,
      duration_s: 5400,
      avg_hr: 154,
    },
  },
  "/chat/messages": {
    messages: [
      {
        id: 1,
        role: "assistant",
        content:
          "Morning Marc. Your Tuesday tempo landed right on target — 4×2km at threshold with HR holding steady. That's the session we wanted 12 weeks out from Paris.",
        created_at: "2026-06-21T08:00:00Z",
      },
      {
        id: 2,
        role: "user",
        content: "Should I be worried my form is at -9?",
        created_at: "2026-06-21T08:01:00Z",
      },
      {
        id: 3,
        role: "assistant",
        content:
          "Not at all. A TSB of -9 means you're carrying productive fatigue — exactly where a build block should sit. We'll let it rebound during next week's down week before the long-run progression resumes.",
        created_at: "2026-06-21T08:01:30Z",
      },
    ],
  },
};

async function setupAuth(page: Page) {
  await page.addInitScript(
    ([ref, session]) => {
      window.localStorage.setItem(
        `sb-${ref}-auth-token`,
        JSON.stringify(session),
      );
    },
    [SUPABASE_REF, fakeSession] as const,
  );

  // Stub all FastAPI calls (NEXT_PUBLIC_API_URL → :8001) with fixtures.
  await page.route("**://localhost:8001/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    const body = API_FIXTURES[path];
    if (body === undefined) {
      await route.fulfill({ status: 404, body: JSON.stringify({ error: { message: "no fixture" } }) });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
}

const AUTHED_ROUTES: Array<{ name: string; path: string }> = [
  { name: "dashboard", path: "/dashboard" },
  { name: "coach", path: "/coach" },
];

for (const route of AUTHED_ROUTES) {
  test(`authed ${route.name}`, async ({ page }, testInfo) => {
    await setupAuth(page);
    await page.goto(route.path, { waitUntil: "networkidle" });
    await page.waitForTimeout(600);
    await page.screenshot({
      path: `e2e/__shots__/authed-${route.name}-${testInfo.project.name}.png`,
      fullPage: true,
    });
  });
}
