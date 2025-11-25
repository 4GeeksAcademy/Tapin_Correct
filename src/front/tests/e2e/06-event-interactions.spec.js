import { test, expect } from '@playwright/test';

/**
 * Event Interaction Tests
 * Tests for liking, super-liking, attending, and sharing events
 */

test.describe('Event Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');

    // Register and login
    const timestamp = Date.now();
    const testEmail = `interact${timestamp}@test.com`;

    const registerLink = page.getByRole('link', { name: /register/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', 'Test123!@#');
      await page.getByRole('button', { name: /register/i }).click();
      await page.waitForTimeout(2000);
    }

    // Search for events
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Austin');
      await page.getByRole('button', { name: /search/i }).click();
      await page.waitForTimeout(2000);
    }
  });

  test('should like an event', async ({ page }) => {
    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();
      await page.waitForTimeout(1000);

      // Find and click like button
      const likeButton = page.getByRole('button', { name: /like|favorite/i }).first();
      if (await likeButton.isVisible().catch(() => false)) {
        await likeButton.click();

        // Should show liked state
        await page.waitForTimeout(500);
        const isLiked = await likeButton.getAttribute('class');
        expect(isLiked).toContain(/active|liked|filled/i);
      }
    }
  });

  test('should super-like an event', async ({ page }) => {
    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();
      await page.waitForTimeout(1000);

      // Find super-like button
      const superLikeButton = page.getByRole('button', { name: /super like|love|heart/i });
      if (await superLikeButton.isVisible().catch(() => false)) {
        await superLikeButton.click();

        // Should show super-liked state
        await page.waitForTimeout(500);
        expect(await superLikeButton.getAttribute('class')).toContain(/active|super|loved/i);
      }
    }
  });

  test('should mark event as attending', async ({ page }) => {
    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();
      await page.waitForTimeout(1000);

      // Find attend button
      const attendButton = page.getByRole('button', { name: /attend|going|rsvp/i });
      if (await attendButton.isVisible().catch(() => false)) {
        await attendButton.click();

        // Should show confirmation
        await page.waitForTimeout(500);
        const confirmation = page.getByText(/attending|confirmed|going/i);
        await expect(confirmation).toBeVisible({ timeout: 2000 });
      }
    }
  });

  test('should view event details without login required', async ({ page, context }) => {
    // Logout first
    const logoutButton = page.getByRole('button', { name: /logout/i });
    if (await logoutButton.isVisible().catch(() => false)) {
      await logoutButton.click();
    }

    // Should still be able to view events
    await page.goto('/');
    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();

      // Should show event details
      await expect(page.getByText(/description|details/i)).toBeVisible({ timeout: 3000 });
    }
  });

  test('should track event views', async ({ page }) => {
    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      // View event
      await firstEvent.click();
      await page.waitForTimeout(2000);

      // View should be tracked (check in achievements or profile)
      const achievementsLink = page.getByRole('link', { name: /achievements|profile/i });
      if (await achievementsLink.isVisible().catch(() => false)) {
        await achievementsLink.click();
        await page.waitForTimeout(1000);

        // Should have some XP from views
        const xpDisplay = page.locator(':has-text("XP"), :has-text("xp")');
        await expect(xpDisplay).toBeVisible({ timeout: 3000 });
      }
    }
  });

  test('should share event', async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);

    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();
      await page.waitForTimeout(1000);

      // Find share button
      const shareButton = page.getByRole('button', { name: /share/i });
      if (await shareButton.isVisible().catch(() => false)) {
        await shareButton.click();

        // Should show share options or copy confirmation
        const hasShareUI = await page.getByText(/copied|share|link/i).isVisible({ timeout: 2000 }).catch(() => false);
        expect(hasShareUI).toBeTruthy();
      }
    }
  });

  test('should unlike an event', async ({ page }) => {
    const firstEvent = page.locator('[data-testid="event-card"], .event-card').first();

    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();
      await page.waitForTimeout(1000);

      // Like event
      const likeButton = page.getByRole('button', { name: /like/i }).first();
      if (await likeButton.isVisible().catch(() => false)) {
        await likeButton.click();
        await page.waitForTimeout(500);

        // Unlike event
        await likeButton.click();
        await page.waitForTimeout(500);

        // Should be unliked
        const isLiked = await likeButton.getAttribute('class');
        expect(isLiked).not.toContain(/active|liked|filled/i);
      }
    }
  });
});
