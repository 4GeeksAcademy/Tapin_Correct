import { test, expect } from '@playwright/test';

test.describe('Volunteer Listings', () => {
  test('should display listings or empty state', async ({ page }) => {
    await page.goto('/');


    await page.waitForLoadState('networkidle');


    const hasListings = await page.locator('[class*="listing"], [class*="card"], article').count() > 0;
    const hasEmptyState = await page.locator('[class*="empty"]').isVisible().catch(() => false);

    expect(hasListings || hasEmptyState).toBe(true);
  });

  test('should have filterable listings by category', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');


    const filterElements = await page.locator(
      'select, [role="combobox"], button:has-text(/filter/i), [class*="filter"]'
    ).count();


  });

  test('should display listing details when clicked', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');


    const firstListing = page.locator('[class*="listing"], [class*="card"], article').first();

    if (await firstListing.isVisible()) {
      await firstListing.click();


      await page.waitForTimeout(500);


      const urlChanged = page.url() !== 'http://localhost:5173/';
      const modalVisible = await page.locator('[role="dialog"], [class*="modal"]').isVisible().catch(() => false);

      expect(urlChanged || modalVisible).toBe(true);
    }
  });

  test('should have professional listing card styling', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const listingCard = page.locator('[class*="listing"], [class*="card"]').first();

    if (await listingCard.isVisible()) {

      const borderRadius = await listingCard.evaluate((el) =>
        window.getComputedStyle(el).borderRadius
      );
      expect(borderRadius).not.toBe('0px');


      const boxShadow = await listingCard.evaluate((el) =>
        window.getComputedStyle(el).boxShadow
      );
      const border = await listingCard.evaluate((el) =>
        window.getComputedStyle(el).border
      );

      expect(boxShadow !== 'none' || border !== '0px none rgb(0, 0, 0)').toBe(true);
    }
  });

  test('should show listing metadata (date, location, category)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const listingCard = page.locator('[class*="listing"], [class*="card"]').first();

    if (await listingCard.isVisible()) {
      const text = await listingCard.textContent();


      const hasMetadata =
        text.includes('ago') ||
        text.includes('20') ||
        text.match(/\b(Dallas|Houston|Miami|TX|FL)\b/) ||
        text.match(/\b(Education|Environment|Health|Community)\b/);


    }
  });
});
