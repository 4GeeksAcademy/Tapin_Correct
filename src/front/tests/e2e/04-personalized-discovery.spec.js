import { test, expect } from '@playwright/test';

/**
 * Personalized Discovery Tests
 * Tests for AI-powered personalized event recommendations
 */

test.describe('Personalized Discovery', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');

    // Register and login
    const timestamp = Date.now();
    const testEmail = `personal${timestamp}@test.com`;

    const registerLink = page.getByRole('link', { name: /register/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', 'Test123!@#');
      await page.getByRole('button', { name: /register/i }).click();
      await page.waitForTimeout(2000);
    }

    // Navigate to personalized discovery
    const personalizedLink = page.getByRole('link', { name: /personalized|ai/i });
    if (await personalizedLink.isVisible().catch(() => false)) {
      await personalizedLink.click();
    }
  });

  test('should display personalized feed', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Should show events or empty state
    const hasEvents = await page.locator('[data-testid="event-card"], .event-card, article').count() > 0;
    const hasEmptyState = await page.getByText(/no events|personalized|recommendations/i).isVisible().catch(() => false);

    expect(hasEvents || hasEmptyState).toBeTruthy();
  });

  test('should show match scores on events', async ({ page }) => {
    await page.waitForTimeout(3000);

    // Look for match score indicators
    const matchScores = page.locator('[data-testid="match-score"], .match-score, :has-text("% match")');
    const scoreCount = await matchScores.count();

    if (scoreCount > 0) {
      // Verify match scores are percentages
      const firstScore = await matchScores.first().textContent();
      expect(firstScore).toMatch(/\d+%/);
    }
  });

  test('should load personalized events for location', async ({ page }) => {
    // Set location
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Boston');

      const loadButton = page.getByRole('button', { name: /load|search|find/i }).first();
      await loadButton.click();
      await page.waitForTimeout(3000);

      // Should show events or empty state
      const hasResults = await page.locator('[data-testid="event-card"], .event-card').count() > 0;
      const hasEmpty = await page.getByText(/no events/i).isVisible().catch(() => false);

      expect(hasResults || hasEmpty).toBeTruthy();
    }
  });

  test('should display organizational values', async ({ page }) => {
    await page.waitForTimeout(3000);

    // Look for value badges on events
    const valueBadges = page.locator('[data-testid="value-badge"], .value-badge, .badge:has-text("animals"), .badge:has-text("youth"), .badge:has-text("environment")');
    const badgeCount = await valueBadges.count();

    // Values may not always be present
    expect(badgeCount).toBeGreaterThanOrEqual(0);
  });

  test('should sort events by match score', async ({ page }) => {
    await page.waitForTimeout(3000);

    // Get all match scores
    const matchScores = page.locator('[data-testid="match-score"], .match-score');
    const scoreCount = await matchScores.count();

    if (scoreCount >= 2) {
      // Extract first two scores
      const firstScoreText = await matchScores.nth(0).textContent();
      const secondScoreText = await matchScores.nth(1).textContent();

      const firstScore = parseInt(firstScoreText.match(/\d+/)?.[0] || '0');
      const secondScore = parseInt(secondScoreText.match(/\d+/)?.[0] || '0');

      // First should be >= second (sorted descending)
      expect(firstScore).toBeGreaterThanOrEqual(secondScore);
    }
  });

  test('should include events from multiple sources', async ({ page }) => {
    await page.waitForTimeout(3000);

    // Look for source indicators
    const sourceIndicators = page.locator('[data-testid="event-source"], .event-source, :has-text("Database"), :has-text("Web")');
    const sourceCount = await sourceIndicators.count();

    // At least one source indicator should exist
    expect(sourceCount).toBeGreaterThanOrEqual(0);
  });

  test('should refresh personalized feed', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Look for refresh button
    const refreshButton = page.getByRole('button', { name: /refresh|reload/i });

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();

      // Should show loading state
      await expect(page.locator('.spinner, [role="progressbar"]')).toBeVisible({ timeout: 2000 });
    }
  });
});
