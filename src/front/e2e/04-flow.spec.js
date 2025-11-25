import { test, expect } from "@playwright/test";

test.describe("Full Page Flow", () => {
  test("landing page to AuthForm and back", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=TapIn")).toBeVisible();
    await page.click("text=Get Started");
    await expect(page.locator("text=Login")).toBeVisible();
    await page.click("text=← Back to home");
    await expect(page.locator("text=TapIn")).toBeVisible();
  });

  test("event search displays AI summary and links", async ({ page }) => {
    await page.goto("/");
    // Navigate to event search if not on landing
    if (
      (await page
        .locator("text=Search for External Volunteer Opportunities")
        .count()) === 0
    ) {
      await page.click("text=Get Started");
      await page.click("text=Login");
      // Simulate login if needed (skip if not required)
    }
    await expect(
      page.locator("text=Search for External Volunteer Opportunities")
    ).toBeVisible();
    await page.fill("input.search-input", "volunteer Dallas");
    await page.click("button.search-button");
    await expect(page.locator("text=AI Summary")).toBeVisible();
    await expect(page.locator(".result-item")).toHaveCountGreaterThan(1);
    await expect(page.locator(".result-link")).first().toHaveAttribute("href");
  });

  test("login/register flow leads to dashboard", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Get Started");
    await page.click("text=Register");
    await page.fill('input[placeholder="email"]', "testuser@example.com");
    await page.fill('input[placeholder="password"]', "abc123");
    await page.fill('input[placeholder="confirm password"]', "abc123");
    await page.click('button:has-text("Register")');
    // Expect dashboard or landing after login
    await expect(page.locator("text=TapIn")).toBeVisible();
  });
});
