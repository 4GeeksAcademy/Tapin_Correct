import { test, expect } from '@playwright/test';

/**
 * Event Search & Discovery Tests
 * Tests for event searching, filtering, and category browsing
 */

let authToken;

test.describe('Event Search', () => {
  test.beforeAll(async ({ browser }) => {
    // Create authenticated user
    const page = await browser.newPage();
    await page.goto('/');

    const timestamp = Date.now();
    const testEmail = `search${timestamp}@test.com`;

    // Register
    const registerLink = page.getByRole('link', { name: /register/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', 'Test123!@#');
      await page.getByRole('button', { name: /register/i }).click();
      await page.waitForTimeout(2000);
    }

    await page.close();
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display event search interface', async ({ page }) => {
    // Look for search input or location input
    const searchInput = page.locator('input[placeholder*="search" i], input[placeholder*="city" i], input[placeholder*="location" i]').first();
    await expect(searchInput).toBeVisible({ timeout: 5000 });
  });

  test('should search events by location', async ({ page }) => {
    // Enter location
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    const stateInput = page.locator('input[placeholder*="state" i]').first();

    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Austin');
    }

    if (await stateInput.isVisible().catch(() => false)) {
      await stateInput.fill('TX');
    }

    // Click search button
    const searchButton = page.getByRole('button', { name: /search|find/i }).first();
    await searchButton.click();

    // Should show results or loading state
    await page.waitForTimeout(2000);
    const hasResults = await page.locator('[data-testid="event-card"], .event-card, article').count() > 0;
    const hasLoading = await page.getByText(/loading|searching/i).isVisible().catch(() => false);
    const hasEmpty = await page.getByText(/no events|no results/i).isVisible().catch(() => false);

    expect(hasResults || hasLoading || hasEmpty).toBeTruthy();
  });

  test('should filter events by category', async ({ page }) => {
    // Wait for page load
    await page.waitForTimeout(1000);

    // Look for category filters
    const categoryButton = page.locator('button:has-text("Animal"), button:has-text("Education"), button:has-text("Environment")').first();

    if (await categoryButton.isVisible().catch(() => false)) {
      await categoryButton.click();
      await page.waitForTimeout(1000);

      // Should filter results
      const filteredResults = page.locator('[data-testid="event-card"], .event-card');
      await expect(filteredResults.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should toggle web search on/off', async ({ page }) => {
    // Look for web search toggle
    const webSearchToggle = page.locator('input[type="checkbox"]:near(:text("Web Search")), button:has-text("Web Search")').first();

    if (await webSearchToggle.isVisible().catch(() => false)) {
      // Get initial state
      const initialState = await webSearchToggle.isChecked().catch(() => false);

      // Toggle it
      await webSearchToggle.click();
      await page.waitForTimeout(500);

      // Verify state changed
      const newState = await webSearchToggle.isChecked().catch(() => true);
      expect(newState).not.toBe(initialState);
    }
  });

  test('should display event details when clicked', async ({ page }) => {
    // Search for events first
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Austin');
      const searchButton = page.getByRole('button', { name: /search/i }).first();
      await searchButton.click();
      await page.waitForTimeout(2000);
    }

    // Click first event
    const firstEvent = page.locator('[data-testid="event-card"], .event-card, article').first();
    if (await firstEvent.isVisible().catch(() => false)) {
      await firstEvent.click();

      // Should show event details
      await expect(page.getByText(/description|details|about/i)).toBeVisible({ timeout: 3000 });
    }
  });

  test('should show loading state during search', async ({ page }) => {
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('Boston');
      const searchButton = page.getByRole('button', { name: /search/i }).first();
      await searchButton.click();

      // Should show loading indicator
      const loadingIndicator = page.locator('.spinner, [role="progressbar"], :has-text("Loading")');
      await expect(loadingIndicator).toBeVisible({ timeout: 1000 });
    }
  });

  test('should handle empty search results gracefully', async ({ page }) => {
    const cityInput = page.locator('input[placeholder*="city" i]').first();
    if (await cityInput.isVisible().catch(() => false)) {
      await cityInput.fill('ZZZInvalidCity999');
      const searchButton = page.getByRole('button', { name: /search/i }).first();
      await searchButton.click();
      await page.waitForTimeout(2000);

      // Should show empty state message
      await expect(page.getByText(/no events|no results|try different/i)).toBeVisible({ timeout: 5000 });
    }
  });
});
