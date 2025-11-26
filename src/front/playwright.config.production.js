import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config for running tests against the deployed Fly app
 * Use for presentation / production verification
 */
export default defineConfig({
  testDir: "./tests/e2e",
  /* Run tests one at a time for stability against production */
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 1,
  workers: 1,
  timeout: 120 * 1000,
  reporter: [
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["list"],
  ],

  use: {
    baseURL: "https://tapin-correct.fly.dev",
    actionTimeout: 30 * 1000,
    navigationTimeout: 60 * 1000,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  // No webServer here: tests run against the live deployed site
});
