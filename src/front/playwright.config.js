import { defineConfig, devices } from "@playwright/test";

// Allow opting into the lightweight mock API for CI/dev by setting
// USE_MOCK_API=1. By default tests will assume a real backend is available
// (so deployments and real-db debugging use the real database).
const useMock = process.env.USE_MOCK_API === "1";

const webServerCommand = useMock
  ? "node mock-api.cjs & npm --prefix ../.. run dev"
  : "npm --prefix ../.. run dev";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",

  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: {
    // Start the frontend dev server. When USE_MOCK_API=1 the test harness
    // will start the lightweight `mock-api.cjs` on :5000 first. By default
    // we prefer using a real backend so deployments and local realtime
    // testing use the actual DB.
    command: webServerCommand,
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
