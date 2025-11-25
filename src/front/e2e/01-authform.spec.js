import { test, expect } from "@playwright/test";

test.describe("AuthForm E2E", () => {
  test("login and register tabs are visible", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Get Started");
    await expect(page.locator("text=Login")).toBeVisible();
    await expect(page.locator("text=Register")).toBeVisible();
  });

  test("shows error for password mismatch on register", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Get Started");
    await page.click("text=Register");
    await page.fill('input[placeholder="email"]', "test@example.com");
    await page.fill('input[placeholder="password"]', "abc123");
    await page.fill('input[placeholder="confirm password"]', "xyz789");
    await page.click('button:has-text("Register")');
    await expect(page.locator("text=Passwords do not match")).toBeVisible();
  });

  test("shows error for missing organization name", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Get Started");
    await page.click("text=Register");
    await page.click('label:has-text("Organization")');
    await page.fill('input[placeholder="email"]', "org@example.com");
    await page.fill('input[placeholder="password"]', "abc123");
    await page.fill('input[placeholder="confirm password"]', "abc123");
    await page.click('button:has-text("Register")');
    await expect(
      page.locator("text=Organization name is required")
    ).toBeVisible();
  });
});
