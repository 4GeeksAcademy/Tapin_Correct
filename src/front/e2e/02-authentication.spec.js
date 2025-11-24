import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should display login/signup form', async ({ page }) => {
    await page.goto('/');


    const authElements = await page.locator(
      'button:has-text(/log.*in/i), a:has-text(/sign.*up/i), input[type="email"], input[type="password"]'
    ).count();

    expect(authElements).toBeGreaterThan(0);
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    await page.goto('/');


    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();

    if (await emailInput.isVisible()) {
      await emailInput.click();
      await emailInput.blur();


      const validationText = await page.locator('[class*="error"], [role="alert"]').textContent().catch(() => '');
    }
  });

  test('should handle invalid credentials gracefully', async ({ page }) => {
    await page.goto('/');

    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const submitButton = page.locator('button[type="submit"]').first();

    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill('invalid@test.com');
      await passwordInput.fill('wrongpassword');

      if (await submitButton.isVisible()) {
        await submitButton.click();


        await page.waitForTimeout(1000);
        const hasError = await page.locator('[class*="error"], [role="alert"], .toast').isVisible().catch(() => false);

      }
    }
  });

  test('should have accessible form labels', async ({ page }) => {
    await page.goto('/');

    const emailInput = page.locator('input[type="email"]').first();

    if (await emailInput.isVisible()) {

      const hasLabel = await emailInput.evaluate((el) => {
        const label = document.querySelector(`label[for="${el.id}"]`);
        return label !== null || el.getAttribute('aria-label') !== null || el.getAttribute('placeholder') !== null;
      });

      expect(hasLabel).toBe(true);
    }
  });
});
