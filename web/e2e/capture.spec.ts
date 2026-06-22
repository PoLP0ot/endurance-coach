import { test } from "@playwright/test";

/**
 * Capture full-page screenshots of public routes for visual review against
 * docs/design/prototype.html. Run: pnpm exec playwright test capture
 * Output: e2e/__shots__/<route>-<project>.png
 */
const PUBLIC_ROUTES: Array<{ name: string; path: string }> = [
  { name: "landing", path: "/" },
  { name: "login", path: "/login" },
  { name: "signup", path: "/signup" },
  { name: "forgot-password", path: "/forgot-password" },
  { name: "onboarding", path: "/onboarding" },
  { name: "pricing", path: "/pricing" },
  { name: "coachonboard", path: "/coachonboard" },
];

for (const route of PUBLIC_ROUTES) {
  test(`capture ${route.name}`, async ({ page }, testInfo) => {
    await page.goto(route.path, { waitUntil: "networkidle" });
    await page.screenshot({
      path: `e2e/__shots__/${route.name}-${testInfo.project.name}.png`,
      fullPage: true,
    });
  });
}
