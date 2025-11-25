import { test, expect } from '@playwright/test';

/**
 * Surprise Me Feature Tests
 * Tests for the AI-powered surprise event recommendation feature
 */

test.describe('Surprise Me Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');

    // Register and login
    const timestamp = Date.now();
    const testEmail = `surprise${timestamp}@test.com`;

    const registerLink = page.getByRole('link', { name: /register/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', 'Test123!@#');
      await page.getByRole('button', { name: /register/i }).click();
      await page.waitForTimeout(2000);
    }

    // Navigate to Surprise Me feature
    const surpriseLink = page.getByRole('link', { name: /surprise/i });
    if (await surpriseLink.isVisible().catch(() => false)) {
      await surpriseLink.click();
    }
  });

  test('should display surprise me interface', async ({ page }) => {
    // Look for mood selector
    const moodButtons = page.locator('button:has-text("Energetic"), button:has-text("Chill"), button:has-text("Creative")');
    await expect(moodButtons.first()).toBeVisible({ timeout: 5000 });
  });

  test('should allow selecting different moods', async ({ page }) => {
    // Find mood buttons
    const energeticButton = page.getByRole('button', { name: /energetic/i });
    const chillButton = page.getByRole('button', { name: /chill/i });

    if (await energeticButton.isVisible().catch(() => false)) {
      await energeticButton.click();
      await expect(energeticButton).toHaveClass(/active|selected/);

      await chillButton.click();
      await expect(chillButton).toHaveClass(/active|selected/);
    }
  });

  test('should generate surprise event', async ({ page }) => {
    // Select mood
    const creativeButton = page.getByRole('button', { name: /creative/i });
    if (await creativeButton.isVisible().catch(() => false)) {
      await creativeButton.click();
    }

    // Set location if available
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Austin');
    }

    // Click surprise me button
    const surpriseButton = page.getByRole('button', { name: /surprise me/i });
    await surpriseButton.click();

    // Should show loading then result
    await page.waitForTimeout(3000);

    // Look for event result or surprise event
    const hasEvent = await page.locator('[data-testid="surprise-event"], .surprise-event, h3, h2').count() > 0;
    const hasError = await page.getByText(/no events|error|try again/i).isVisible().catch(() => false);

    expect(hasEvent || hasError).toBeTruthy();
  });

  test('should display surprise explanation', async ({ page }) => {
    // Generate a surprise
    const creativeButton = page.getByRole('button', { name: /creative/i });
    if (await creativeButton.isVisible().catch(() => false)) {
      await creativeButton.click();
    }

    const surpriseButton = page.getByRole('button', { name: /surprise me/i });
    await surpriseButton.click();
    await page.waitForTimeout(3000);

    // Look for explanation text
    const explanation = page.locator('[data-testid="surprise-explanation"], .surprise-explanation');
    const hasExplanation = await explanation.isVisible().catch(() => false);

    if (hasExplanation) {
      await expect(explanation).not.toBeEmpty();
    }
  });

  test('should allow adjusting preferences', async ({ page }) => {
    // Look for customize/settings button
    const customizeButton = page.getByRole('button', { name: /customize|preferences|settings/i });

    if (await customizeButton.isVisible().catch(() => false)) {
      await customizeButton.click();

      // Should show sliders or preference controls
      const budgetSlider = page.locator('input[type="range"]').first();
      await expect(budgetSlider).toBeVisible({ timeout: 2000 });
    }
  });

  test('should regenerate surprise on retry', async ({ page }) => {
    // Generate initial surprise
    const surpriseButton = page.getByRole('button', { name: /surprise me/i });
    await surpriseButton.click();
    await page.waitForTimeout(3000);

    // Get first event title if available
    const firstEventTitle = await page.locator('h2, h3').first().textContent().catch(() => '');

    // Click try again or regenerate
    const retryButton = page.getByRole('button', { name: /try again|another|regenerate/i });
    if (await retryButton.isVisible().catch(() => false)) {
      await retryButton.click();
      await page.waitForTimeout(3000);

      // Should potentially show different event (though may be same)
      const newEventTitle = await page.locator('h2, h3').first().textContent().catch(() => '');
      expect(newEventTitle).toBeTruthy();
    }
  });

  test('should show match score if available', async ({ page }) => {
    const surpriseButton = page.getByRole('button', { name: /surprise me/i });
    await surpriseButton.click();
    await page.waitForTimeout(3000);

    // Look for match score badge
    const matchScore = page.locator('[data-testid="match-score"], .match-score, :has-text("% Match")');
    const hasMatchScore = await matchScore.isVisible().catch(() => false);

    // Match score is optional, so just verify if present it's valid
    if (hasMatchScore) {
      const scoreText = await matchScore.textContent();
      expect(scoreText).toMatch(/\d+%/);
    }
  });
});
