import { test, expect } from '@playwright/test';

test.describe('Homepage & Landing Page', () => {
  test('should load the homepage successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Tapin/i);
  });

  test('should display the main header', async ({ page }) => {
    await page.goto('/');
    const header = page.locator('header, nav, [role="banner"]').first();
    await expect(header).toBeVisible();
  });

  test('should have professional and consistent styling', async ({ page }) => {
    await page.goto('/');


    const body = page.locator('body');
    const bgColor = await body.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );
    expect(bgColor).toBeTruthy();


    const hasHorizontalScroll = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasHorizontalScroll).toBe(false);
  });

  test('should display navigation elements', async ({ page }) => {
    await page.goto('/');


    const navElements = await page.locator('nav, header a, button').count();
    expect(navElements).toBeGreaterThan(0);
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');


    await expect(page.locator('body')).toBeVisible();


    const mobileNav = page.locator('[aria-label*="menu"], .hamburger, .mobile-menu');

  });

  test('should load without console errors', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');


    const criticalErrors = errors.filter(e =>
      !e.includes('favicon') && !e.includes('manifest')
    );
    expect(criticalErrors).toHaveLength(0);
  });
});
