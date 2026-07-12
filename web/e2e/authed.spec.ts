import { test, type Page } from "@playwright/test";

/**
 * Capture auth-gated screens AND edge/flow states with a stubbed Supabase
 * session + stubbed FastAPI responses. Self-contained on purpose: relative
 * imports between e2e files break Playwright's loader on this host
 * (Node 22 + Windows), so fixtures live inline.
 * Run: pnpm exec playwright test authed
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
const CDN = "https://cdn.jsdelivr.net/gh/hasaneyldrm/exercises-dataset@main";
const exerciseCard = (id: string, name: string, target: string, media: string) => ({
  id,
  name,
  body_part: "chest",
  target,
  equipment: "barbell",
  image_url: `${CDN}/images/${media}.jpg`,
  gif_url: `${CDN}/videos/${media}.gif`,
});

const API_FIXTURES: Record<string, unknown> = {
  "/exercises": {
    items: [
      exerciseCard("0025", "barbell bench press", "pectorals", "0025-EIeI8Vf"),
      exerciseCard("0033", "barbell decline bench press", "pectorals", "0033-GrO65fd"),
    ],
    next_cursor: null,
  },
  "/exercises/0025": {
    ...exerciseCard("0025", "barbell bench press", "pectorals", "0025-EIeI8Vf"),
    muscle_group: "triceps",
    secondary_muscles: ["triceps", "shoulders"],
    instructions: [
      "Lie flat on the bench with your feet planted on the floor.",
      "Grip the bar slightly wider than shoulder width and unrack it.",
      "Lower the bar to mid-chest with control, then press back up.",
    ],
    attribution: "Gym visual — https://gymvisual.com/",
  },
  "/strength/plans/current": {
    plan: {
      id: "sp1",
      goal_kind: "weight_loss",
      weeks: 8,
      frequency: 2,
      level: "intermediate",
      equipment: ["barbell", "body weight"],
      start_date: "2026-06-22",
      status: "active",
      narrative: null,
      structure: {
        frequency: 2,
        level: "intermediate",
        equipment: ["barbell", "body weight"],
        blocks: [
          { block: "adaptation", weeks: 2 },
          { block: "hypertrophy", weeks: 4 },
          { block: "strength", weeks: 2 },
        ],
        weeks: [1, 2, 3, 4, 5, 6, 7, 8].map((n) => ({
          week: n,
          start_date: [
            "2026-06-22", "2026-06-29", "2026-07-06", "2026-07-13",
            "2026-07-20", "2026-07-27", "2026-08-03", "2026-08-10",
          ][n - 1],
          block: n <= 2 ? "adaptation" : n <= 6 ? "hypertrophy" : "strength",
          is_deload: n % 4 === 0,
          focus: "Build muscle — volume at controlled effort",
          sessions: [
            {
              day: 0,
              focus: "full",
              title: "Full body A",
              items: [
                {
                  slot: "push",
                  exercise_id: "0025",
                  name: "barbell bench press",
                  equipment: "barbell",
                  gif_url: `${CDN}/videos/0025-EIeI8Vf.gif`,
                  target_weight_kg: null,
                  sets: 4,
                  reps: 10,
                  rpe: 8,
                  rest_sec: 90,
                },
                {
                  slot: "core",
                  exercise_id: "0001",
                  name: "3/4 sit-up",
                  equipment: "body weight",
                  gif_url: `${CDN}/videos/0001-2gPfomN.gif`,
                  target_weight_kg: null,
                  sets: 4,
                  reps: 10,
                  rpe: 8,
                  rest_sec: 90,
                },
              ],
            },
            {
              day: 3,
              focus: "full",
              title: "Full body B",
              items: [
                {
                  slot: "push",
                  exercise_id: "0033",
                  name: "barbell decline bench press",
                  equipment: "barbell",
                  gif_url: `${CDN}/videos/0033-GrO65fd.gif`,
                  target_weight_kg: null,
                  sets: 4,
                  reps: 10,
                  rpe: 8,
                  rest_sec: 90,
                },
              ],
            },
          ],
        })),
      },
    },
  },
  "/strength/logs": {
    sets: [],
    summary: {
      week: 3,
      day: 0,
      title: "Full body A",
      sets_prescribed: 8,
      sets_logged: 0,
      volume_kg: 0,
      completed: false,
    },
  },
  "/coach/today": {
    status: "ok",
    date: "2026-06-24",
    week: 6,
    phase: "build",
    session: {
      day_index: 2,
      kind: "interval",
      prescription: "Intervals 6×1 km @ threshold",
      target_tss: 70,
    },
    is_rest: false,
    adherence: {
      adherence_pct: 80,
      completed: 4,
      partial: 0,
      missed: 1,
      extras: 0,
    },
    goal_band: "on_track",
    headline: "Projected finish 3:28:00",
  },
  "/coach/brief": {
    day: "2026-06-24",
    headline: "Interval day — you're fresh enough to hit it.",
    body: "Recovery came back at 74 overnight and yesterday stayed easy, so today's 6×1 km at threshold lands on fresh legs. Lock in the paces from Tuesday and let the last two reps hurt a little.",
    prescription: null,
    model: "gpt-4o-mini",
  },
  "/dashboard": {
    goal: {
      race_name: "Paris Marathon",
      race_date: "2026-09-14",
      days_to_go: 82,
      weeks_to_go: 12,
      progress_pct: 52,
      is_past: false,
    },
    goal_structured: {
      kind: "marathon",
      label: "Race time",
      on_track_band: "on_track",
      headline: "Projected finish 3:28:00 — on track for Paris.",
      projection: "3:28:00",
      target: "3:30:00",
      eta: "2026-09-14",
    },
    goal_variant: {
      kind: "marathon",
      panels: [
        { label: "Fitness", value: 62, unit: "CTL", hint: "42-day load" },
        { label: "Form", value: -9, unit: "TSB", hint: "balance" },
        { label: "Threshold pace", value: "4:24/km", unit: "", hint: "best recent run" },
      ],
    },
    this_week: {
      this_week: { activity_count: 4, distance_m: 48200, tss: 287, duration_s: 16800 },
      last_week: { activity_count: 5, distance_m: 52100, tss: 312, duration_s: 18600 },
      week_start: "2026-06-22",
    },
    health: {
      resting_hr: 48,
      hrv: 52,
      sleep_score: 81,
      steps: 9840,
      body_battery: 76,
      stress_avg: 32,
      weight_kg: 71.2,
      days: 7,
      feature: "hrv",
    },
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
  "/plans/current": {
    plan: {
      id: "plan-1",
      goal: "marathon",
      weeks: 12,
      start_date: "2026-06-01",
      status: "active",
      structure: {
        goal: "marathon",
        weeks: [
          { week: 1, start_date: "2026-06-01", phase: "base", is_recovery: false, target_tss: 280, focus: "Aerobic base — easy mileage + strides" },
          { week: 2, start_date: "2026-06-08", phase: "base", is_recovery: false, target_tss: 310, focus: "Volume build + first tempo" },
          { week: 3, start_date: "2026-06-15", phase: "base", is_recovery: true, target_tss: 210, focus: "Down week — absorb the load" },
          { week: 4, start_date: "2026-06-22", phase: "build", is_recovery: false, target_tss: 340, focus: "Threshold intervals + long run" },
          { week: 5, start_date: "2026-06-29", phase: "build", is_recovery: false, target_tss: 365, focus: "Marathon-pace progression" },
          {
            week: 6,
            start_date: "2026-07-06",
            phase: "peak",
            is_recovery: false,
            target_tss: 390,
            focus: "Peak long run + race-pace blocks",
            sessions: [
              { day_index: 0, kind: "easy", prescription: "Easy run 50 min Z2", target_tss: 65 },
              { day_index: 1, kind: "interval", prescription: "Intervals 6×1 km @ threshold", target_tss: 65 },
              { day_index: 3, kind: "tempo", prescription: "Tempo 2×20 min @ marathon pace", target_tss: 65 },
              { day_index: 4, kind: "easy", prescription: "Recovery jog 40 min", target_tss: 65 },
              { day_index: 5, kind: "long", prescription: "Long run 32 km with 3×5 km @ race pace", target_tss: 130 },
            ],
          },
          { week: 7, start_date: "2026-07-13", phase: "taper", is_recovery: false, target_tss: 250, focus: "Taper — sharpen and freshen" },
        ],
      },
      narrative:
        "Twelve weeks to Paris. We start by widening your aerobic base, then layer threshold and marathon-pace work through the build, peak around week 6, and taper into race day. Recovery weeks are deliberate — that's where the gains consolidate.",
      model: "gpt-4o",
    },
  },
  "/profile": {
    id: "00000000-0000-0000-0000-000000000001",
    email: "marc@example.com",
    display_name: "Marc",
    primary_goal: "marathon",
    race_name: "Paris Marathon",
    race_date: "2026-09-14",
    goal_params: { target_time_s: 12600, race_distance_m: 42195 },
    units: "metric",
    weekly_email_opt_in: true,
    onboarding_complete: true,
    subscription_status: "free",
  },
  "/subscription/status": {
    status: "free",
    is_premium: false,
    current_period_end: null,
  },
  "/signals": {
    signals: [
      {
        key: "fitness",
        eyebrow: "Fitness · CTL trend",
        question: "How is my fitness trending?",
        points: Array.from({ length: 21 }, (_, i) => 50 + i * 0.6),
        color: "text-primary",
        interpretation:
          "You're in the productive training zone. Fitness is climbing steadily and fatigue is where we want it 12 weeks out from Paris.",
      },
      {
        key: "form",
        eyebrow: "Form · TSB balance",
        question: "Is my form race-ready?",
        points: Array.from({ length: 21 }, (_, i) => 4 - i * 0.3),
        color: "text-olive",
        interpretation:
          "You're carrying productive fatigue — normal for a build block. Keep an eye on recovery.",
      },
      {
        key: "recovery",
        eyebrow: "Recovery · today",
        question: "Am I recovered enough to push?",
        points: null,
        color: "text-accent",
        interpretation:
          "Recovery is strong at 74/100 — green light for quality work today.",
      },
    ],
  },
  "/garmin/status": {
    status: "connected",
    garmin_username: "marc@example.com",
    last_sync_at: "2026-06-23T07:30:00Z",
  },
  "/activities": {
    windowed: false,
    next_cursor: null,
    items: [
      { id: "a1", activity_type: "running", name: "Threshold intervals", start_time: "2026-06-21T07:00:00Z", distance_m: 14200, duration_s: 4500, avg_hr: 158, tss: 96 },
      { id: "a2", activity_type: "running", name: "Easy recovery run", start_time: "2026-06-20T17:30:00Z", distance_m: 8100, duration_s: 2760, avg_hr: 132, tss: 41 },
      { id: "a3", activity_type: "cycling", name: "Endurance ride", start_time: "2026-06-19T09:00:00Z", distance_m: 52000, duration_s: 7200, avg_hr: 141, tss: 118 },
      { id: "a4", activity_type: "running", name: "Long run", start_time: "2026-06-17T08:00:00Z", distance_m: 28000, duration_s: 9300, avg_hr: 147, tss: 165 },
    ],
  },
  "/activities/a1": {
    id: "a1",
    activity_type: "running",
    name: "Threshold intervals",
    start_time: "2026-06-21T07:00:00Z",
    distance_m: 14200,
    duration_s: 4500,
    avg_hr: 158,
    max_hr: 178,
    elevation_gain_m: 142,
    avg_power_w: null,
    tss: 96,
    streams: {
      has_route: true,
      route: Array.from({ length: 40 }, (_, i) => [
        50.84 + Math.sin(i / 6) * 0.01 + i * 0.0004,
        4.35 + Math.cos(i / 5) * 0.012,
      ]),
      samples: Array.from({ length: 60 }, (_, i) => ({
        t: i * 60,
        hr: 140 + Math.round(Math.sin(i / 8) * 18 + i * 0.2),
        pace_s_per_km: 250 + Math.round(Math.cos(i / 7) * 20),
        elevation_m: 40 + Math.round(Math.sin(i / 10) * 12),
        distance_m: i * 230,
      })),
      splits: [
        { km: 1, duration_s: 248 },
        { km: 2, duration_s: 242 },
        { km: 3, duration_s: 255 },
        { km: 4, duration_s: 239 },
      ],
    },
  },
  "/activities/a1/analysis": {
    activity_id: "a1",
    model: "gpt-4o-mini",
    prompt_version: "v1",
    facts: { tss: 96, avg_hr: 158, time_in_z4_min: 22, pace_min_km: 4.12 },
    narrative:
      "This was a quality threshold session — 22 minutes in zone 4 with heart rate holding steady at 158 bpm tells me you held the effort honestly without drifting into anaerobic territory. That's exactly the stimulus we want in the build phase: enough time at threshold to lift your lactate clearance, but controlled enough to recover for the weekend long run. Slot an easy day tomorrow and let this one consolidate.",
  },
};

/** Stub Supabase session + FastAPI. `overrides` replace/add per-path fixtures;
 * a value of `{ __status: N, ...body }` fulfills with that HTTP status. */
async function setupAuth(
  page: Page,
  overrides: Record<string, unknown> = {},
) {
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
    const body = { ...API_FIXTURES, ...overrides }[path];
    if (body === undefined) {
      await route.fulfill({ status: 404, body: JSON.stringify({ error: { message: "no fixture" } }) });
      return;
    }
    const { __status, ...payload } =
      typeof body === "object" && body !== null
        ? (body as Record<string, unknown>)
        : { __status: undefined };
    await route.fulfill({
      status: typeof __status === "number" ? __status : 200,
      contentType: "application/json",
      body: JSON.stringify(typeof body === "object" ? payload : body),
    });
  });
}


const AUTHED_ROUTES: Array<{ name: string; path: string }> = [
  { name: "dashboard", path: "/dashboard" },
  { name: "coach", path: "/coach" },
  { name: "plan", path: "/plan" },
  { name: "settings", path: "/settings" },
  { name: "subscription", path: "/settings/subscription" },
  { name: "activities", path: "/activities" },
  { name: "activity-detail", path: "/activities/a1" },
  { name: "exercises", path: "/exercises" },
  { name: "exercise-detail", path: "/exercises/0025" },
  { name: "strength", path: "/strength" },
  { name: "strength-session", path: "/strength/session?week=3&day=0" },
  { name: "privacy", path: "/settings/privacy" },
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

async function shoot(page: import("@playwright/test").Page, name: string, project: string) {
  await page.waitForTimeout(400);
  await page.screenshot({
    path: `e2e/__shots__/state-${name}-${project}.png`,
    fullPage: true,
  });
}

test("garmin mfa step", async ({ page }, testInfo) => {
  await setupAuth(page, {
    "/garmin/connect": { __status: 409, error: { message: "garmin_mfa_required" } },
  });
  await page.goto("/onboarding", { waitUntil: "networkidle" });
  await page.getByLabel(/garmin email/i).fill("marc@example.com");
  await page.getByLabel(/garmin password/i).fill("pw");
  await page.getByRole("button", { name: /connect garmin/i }).click();
  await page.getByLabel(/verification code/i).waitFor();
  await shoot(page, "garmin-mfa", testInfo.project.name);
});

test("subscription premium with cancel confirm", async ({ page }, testInfo) => {
  await setupAuth(page, {
    "/subscription/status": {
      status: "active",
      is_premium: true,
      current_period_end: "2026-12-31T00:00:00+00:00",
      cancel_at_period_end: false,
    },
  });
  await page.goto("/settings/subscription", { waitUntil: "networkidle" });
  await page.getByRole("button", { name: /cancel subscription/i }).click();
  await shoot(page, "subscription-cancel-confirm", testInfo.project.name);
});

test("subscription won't renew", async ({ page }, testInfo) => {
  await setupAuth(page, {
    "/subscription/status": {
      status: "active",
      is_premium: true,
      current_period_end: "2026-12-31T00:00:00+00:00",
      cancel_at_period_end: true,
    },
  });
  await page.goto("/settings/subscription", { waitUntil: "networkidle" });
  await shoot(page, "subscription-wont-renew", testInfo.project.name);
});

test("subscription past_due dunning banner", async ({ page }, testInfo) => {
  await setupAuth(page, {
    "/subscription/status": {
      status: "past_due",
      is_premium: true,
      current_period_end: "2026-12-31T00:00:00+00:00",
      cancel_at_period_end: false,
    },
  });
  await page.goto("/settings/subscription", { waitUntil: "networkidle" });
  await shoot(page, "subscription-past-due", testInfo.project.name);
});

test("dashboard garmin reconnect banner", async ({ page }, testInfo) => {
  await setupAuth(page, {
    "/garmin/status": { status: "auth_expired", last_sync_at: null },
  });
  await page.goto("/dashboard", { waitUntil: "networkidle" });
  await shoot(page, "dashboard-reconnect", testInfo.project.name);
});

test("plan adaptation notice", async ({ page }, testInfo) => {
  const base = API_FIXTURES["/plans/current"] as {
    plan: { structure: { weeks: unknown[] } };
  };
  const today = new Date().toISOString().slice(0, 10);
  await setupAuth(page, {
    "/plans/current": {
      plan: {
        ...base.plan,
        structure: {
          ...base.plan.structure,
          last_adaptation: {
            at: today,
            adherence_pct: 64,
            changes: [
              { week: 7, from: 250, to: 228 },
              { week: 6, from: 390, to: 352 },
            ],
          },
        },
      },
    },
  });
  await page.goto("/plan", { waitUntil: "networkidle" });
  await shoot(page, "plan-adapted", testInfo.project.name);
});

test("garmin import progress checklist", async ({ page }, testInfo) => {
  await setupAuth(page, {
    "/garmin/connect": { job_id: "job-9", status: "queued" },
    "/garmin/import-status/job-9": {
      status: "running",
      progress_label: "Analyzing metrics…",
    },
  });
  await page.goto("/onboarding", { waitUntil: "networkidle" });
  await page.getByLabel(/garmin email/i).fill("marc@example.com");
  await page.getByLabel(/garmin password/i).fill("pw");
  await page.getByRole("button", { name: /connect garmin/i }).click();
  await page.getByText(/analyzing metrics/i).first().waitFor();
  await shoot(page, "garmin-importing", testInfo.project.name);
});

test("empty coach thread with starter chips", async ({ page }, testInfo) => {
  await setupAuth(page, { "/chat/messages": { messages: [] } });
  await page.goto("/coach", { waitUntil: "networkidle" });
  await shoot(page, "coach-empty", testInfo.project.name);
});

for (const path of ["terms", "privacy", "contact"]) {
  test(`legal ${path}`, async ({ page }, testInfo) => {
    await page.goto(`/${path}`, { waitUntil: "networkidle" });
    await shoot(page, `legal-${path}`, testInfo.project.name);
  });
}
