import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Tapin E2E tests
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list']
  ],

  use: {
    baseURL: 'https://tapin-correct.fly.dev',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // webServer: [
  //   {
  //     command: 'cd ../backend && PYTHONPATH=/Users/houseofobi/Documents/GitHub/Tapin_Correct/src:/Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend LLM_PROVIDER=mock FLASK_APP=app:create_app .venv/bin/flask run --host=127.0.0.1 --port=5000',
  //     url: 'http://127.0.0.1:5000',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120 * 1000,
  //     stdout: 'pipe',
  //     stderr: 'pipe',
  //   },
  //   {
  //     command: '$HOME/.nvm/versions/node/v18.20.8/bin/npm run dev',
  //     url: 'http://localhost:3000',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 60 * 1000,
  //   },
  // ],
});
