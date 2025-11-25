import { test, expect } from '@playwright/test';

/**
 * Authentication Tests
 * Tests for user registration, login, and authentication flows
 */

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the homepage without errors', async ({ page }) => {
    await expect(page).toHaveTitle(/Tapin/i);
  });

  test('should show login/register form', async ({ page }) => {
    // Look for auth-related elements
    const loginButton = page.getByRole('button', { name: /login|sign in/i });
    const registerButton = page.getByRole('button', { name: /register|sign up/i });

    // At least one should be visible
    const hasAuthUI = await Promise.race([
      loginButton.isVisible(),
      registerButton.isVisible(),
    ]).catch(() => false);

    expect(hasAuthUI).toBeTruthy();
  });

  test('should register a new volunteer user', async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `volunteer${timestamp}@test.com`;

    // Navigate to register
    const registerLink = page.getByRole('link', { name: /register|sign up/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
    }

    // Fill registration form
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', 'Test123!@#');

    // Select volunteer role if available
    const volunteerRadio = page.locator('input[value="volunteer"]').first();
    if (await volunteerRadio.isVisible().catch(() => false)) {
      await volunteerRadio.click();
    }

    // Submit form
    const submitButton = page.getByRole('button', { name: /register|sign up|create account/i });
    await submitButton.click();

    // Should redirect or show success
    await page.waitForTimeout(2000);
    const url = page.url();
    expect(url).not.toContain('register');
  });

  test('should login with valid credentials', async ({ page }) => {
    // First register a user
    const timestamp = Date.now();
    const testEmail = `user${timestamp}@test.com`;
    const testPassword = 'Test123!@#';  // pragma: allowlist secret

    // Register
    const registerLink = page.getByRole('link', { name: /register|sign up/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', testPassword);
      await page.getByRole('button', { name: /register|sign up/i }).click();
      await page.waitForTimeout(1000);
    }

    // Now login
    const loginLink = page.getByRole('link', { name: /login|sign in/i }).first();
    if (await loginLink.isVisible().catch(() => false)) {
      await loginLink.click();
    }

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Should be authenticated
    await page.waitForTimeout(2000);
    const logoutButton = page.getByRole('button', { name: /logout|sign out/i });
    await expect(logoutButton).toBeVisible({ timeout: 5000 });
  });

  test('should show error for invalid login', async ({ page }) => {
    const loginLink = page.getByRole('link', { name: /login|sign in/i }).first();
    if (await loginLink.isVisible().catch(() => false)) {
      await loginLink.click();
    }

    await page.fill('input[type="email"]', 'invalid@test.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Should show error
    await expect(page.getByText(/invalid|incorrect|failed/i)).toBeVisible({ timeout: 3000 });
  });

  test('should logout successfully', async ({ page, context }) => {
    // Login first
    const timestamp = Date.now();
    const testEmail = `user${timestamp}@test.com`;
    const testPassword = 'Test123!@#';  // pragma: allowlist secret

    // Quick register
    await page.goto('/');
    const registerLink = page.getByRole('link', { name: /register/i }).first();
    if (await registerLink.isVisible().catch(() => false)) {
      await registerLink.click();
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', testPassword);
      await page.getByRole('button', { name: /register/i }).click();
      await page.waitForTimeout(2000);
    }

    // Logout
    const logoutButton = page.getByRole('button', { name: /logout|sign out/i });
    await logoutButton.click();

    // Should be logged out
    await page.waitForTimeout(1000);
    const loginButton = page.getByRole('button', { name: /login|sign in/i });
    await expect(loginButton).toBeVisible({ timeout: 3000 });
  });
});
