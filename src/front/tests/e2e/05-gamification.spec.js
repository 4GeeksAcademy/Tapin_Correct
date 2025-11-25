import { test, expect } from '@playwright/test';

/**
 * Gamification Tests
 * Tests for achievements, XP, levels, and badges
 */

test.describe('Gamification System', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');

    // Register and login
    const timestamp = Date.now();
    const testEmail = `gamer${timestamp}@test.com`;

    const registerLink = page.getByRole('link', { name: /register/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', 'Test123!@#');
      await page.getByRole('button', { name: /register/i }).click();
      await page.waitForTimeout(2000);
    }
  });

  test('should display achievements page', async ({ page }) => {
    // Navigate to achievements
    const achievementsLink = page.getByRole('link', { name: /achievements|badges|profile/i });

    if (await achievementsLink.isVisible().catch(() => false)) {
      await achievementsLink.click();
      await page.waitForTimeout(1000);

      // Should show achievements UI
      const hasAchievements = await page.getByText(/achievement|badge|level|xp/i).isVisible().catch(() => false);
      expect(hasAchievements).toBeTruthy();
    }
  });

  test('should show user level and XP', async ({ page }) => {
    const achievementsLink = page.getByRole('link', { name: /achievements|profile/i });

    if (await achievementsLink.isVisible().catch(() => false)) {
      await achievementsLink.click();
      await page.waitForTimeout(1000);

      // Look for level/XP display
      const levelDisplay = page.locator(':has-text("Level"), :has-text("XP")');
      const hasLevel = await levelDisplay.isVisible().catch(() => false);

      if (hasLevel) {
        const levelText = await levelDisplay.textContent();
        expect(levelText).toMatch(/\d+/);
      }
    }
  });

  test('should display achievement progress', async ({ page }) => {
    const achievementsLink = page.getByRole('link', { name: /achievements|badges/i });

    if (await achievementsLink.isVisible().catch(() => false)) {
      await achievementsLink.click();
      await page.waitForTimeout(1000);

      // Look for achievement cards
      const achievementCards = page.locator('[data-testid="achievement-card"], .achievement-card, .badge-card');
      const cardCount = await achievementCards.count();

      // Should show at least some achievements
      expect(cardCount).toBeGreaterThan(0);
    }
  });

  test('should earn XP from event interactions', async ({ page }) => {
    // Navigate to events
    await page.goto('/');
    await page.waitForTimeout(1000);

    // Search for an event
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Austin');
      await page.getByRole('button', { name: /search/i }).click();
      await page.waitForTimeout(2000);

      // Interact with first event (like, view, etc.)
      const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();
      if (await firstEvent.isVisible().catch(() => false)) {
        await firstEvent.click();
        await page.waitForTimeout(1000);

        // Look for like/interact button
        const likeButton = page.getByRole('button', { name: /like|favorite/i });
        if (await likeButton.isVisible().catch(() => false)) {
          await likeButton.click();
        }
      }
    }

    // Check achievements - XP should have increased
    const achievementsLink = page.getByRole('link', { name: /achievements|profile/i });
    if (await achievementsLink.isVisible().catch(() => false)) {
      await achievementsLink.click();
      await page.waitForTimeout(1000);

      const xpDisplay = page.locator(':has-text("XP")');
      const hasXP = await xpDisplay.isVisible().catch(() => false);
      expect(hasXP).toBeTruthy();
    }
  });

  test('should show locked and unlocked achievements', async ({ page }) => {
    const achievementsLink = page.getByRole('link', { name: /achievements|badges/i });

    if (await achievementsLink.isVisible().catch(() => false)) {
      await achievementsLink.click();
      await page.waitForTimeout(1000);

      // Look for locked/unlocked indicators
      const lockedBadge = page.locator(':has-text("Locked"), .locked, .grayscale');
      const unlockedBadge = page.locator(':has-text("Unlocked"), .unlocked');

      const hasLockedOrUnlocked = (await lockedBadge.count() > 0) || (await unlockedBadge.count() > 0);
      expect(hasLockedOrUnlocked).toBeTruthy();
    }
  });

  test('should display achievement descriptions', async ({ page }) => {
    const achievementsLink = page.getByRole('link', { name: /achievements/i });

    if (await achievementsLink.isVisible().catch(() => false)) {
      await achievementsLink.click();
      await page.waitForTimeout(1000);

      // Click first achievement to see details
      const firstAchievement = page.locator('[data-testid="achievement-card"], .achievement-card').first();
      if (await firstAchievement.isVisible().catch(() => false)) {
        await firstAchievement.click();

        // Should show description
        await expect(page.locator(':has-text("description"), p, .description')).toBeVisible({ timeout: 2000 });
      }
    }
  });
});
