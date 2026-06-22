import { defineConfig, devices } from "@playwright/test";

/**
 * Visual validation harness for the design-loop.
 * Screenshots live under e2e/__screenshots__/ and are compared to the
 * prototype (docs/design/prototype.html) by eye during each loop iteration.
 */
export default defineConfig({
  testDir: "./e2e",
  outputDir: "./e2e/.output",
  fullyParallel: true,
  reporter: [["list"]],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    screenshot: "off",
    trace: "off",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 900 } } },
    { name: "mobile", use: { ...devices["iPhone 13"], browserName: "chromium" } },
  ],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
