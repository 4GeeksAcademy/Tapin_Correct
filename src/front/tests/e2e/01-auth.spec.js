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
    // Wait for landing page to load
    await page.waitForLoadState('domcontentloaded');

    // Look for initial landing buttons
    const loginButton = page.getByRole('button', { name: /log in/i });
    const getStartedButton = page.getByRole('button', { name: /get started/i });

    // At least one should be visible
    const loginVisible = await loginButton.isVisible().catch(() => false);
    const getStartedVisible = await getStartedButton.isVisible().catch(() => false);

    expect(loginVisible || getStartedVisible).toBeTruthy();

    // Click to open auth form
    if (loginVisible) {
      await loginButton.click();
    } else {
      await getStartedButton.click();
    }

    // Wait for auth form to appear
    await page.waitForSelector('.auth-form', { timeout: 5000 });

    // Verify auth tabs are visible
    const loginTab = page.getByRole('button', { name: 'Login', exact: true }).first();
    const registerTab = page.getByRole('button', { name: 'Register', exact: true }).first();
    await expect(loginTab).toBeVisible();
    await expect(registerTab).toBeVisible();
  });

  test('should register a new volunteer user', async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `volunteer${timestamp}@test.com`;

    // Click Get Started to open auth form
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    await getStartedButton.click();

    // Wait for auth form
    await page.waitForSelector('.auth-form', { timeout: 5000 });

    // Click Register tab
    const registerTab = page.getByRole('button', { name: 'Register' });
    await registerTab.click();

    // Wait a moment for tab switch
    await page.waitForTimeout(500);

    // Fill registration form
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', 'Test123!@#');
    await page.fill('input#confirm-password', 'Test123!@#');

    // Select volunteer role (should be default)
    const volunteerRadio = page.locator('input[value="volunteer"]').first();
    if (await volunteerRadio.isVisible().catch(() => false)) {
      await volunteerRadio.check();
    }

    // Submit form
    const submitButton = page.getByTestId('register-submit-btn');
    await submitButton.click();

    // Should show listings or dashboard after successful registration
    await page.waitForTimeout(3000);

    // Verify we're no longer on the auth form or we see the main app
    const mainContent = await page.locator('main').isVisible().catch(() => false);
    expect(mainContent).toBeTruthy();
  });

  test('should login with valid credentials', async ({ page }) => {
    // First register a user
    const timestamp = Date.now();
    const testEmail = `user${timestamp}@test.com`;
    const testPassword = 'Test123!@#';  // pragma: allowlist secret

    // Register user
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    await getStartedButton.click();
    await page.waitForSelector('.auth-form', { timeout: 5000 });

    const registerTab = page.getByRole('button', { name: 'Register' });
    await registerTab.click();
    await page.waitForTimeout(500);

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.fill('input#confirm-password', testPassword);

    await page.getByTestId('register-submit-btn').click();
    await page.waitForTimeout(2000);

    // Clear local storage to force re-login
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');

    // Now login with registered credentials
    const loginButton = page.getByRole('button', { name: /log in/i });
    await loginButton.click();
    await page.waitForSelector('.auth-form', { timeout: 5000 });

    // Should default to login tab
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input#password', testPassword);
    await page.getByTestId('login-submit-btn').click();

    // Should be authenticated and see main app
    await page.waitForTimeout(3000);
    const mainContent = await page.locator('main').isVisible().catch(() => false);
    expect(mainContent).toBeTruthy();
  });

  test('should show error for invalid login', async ({ page }) => {
    // Click Log In to open auth form
    const loginButton = page.getByRole('button', { name: /log in/i });
    await loginButton.click();
    await page.waitForSelector('.auth-form', { timeout: 5000 });

    // Fill with invalid credentials
    await page.fill('input[type="email"]', 'invalid@test.com');
    await page.fill('input#password', 'wrongpassword');
    await page.getByTestId('login-submit-btn').click();

    // Should show error
    await page.waitForTimeout(2000);
    const errorMessage = await page.locator('.error').isVisible().catch(() => false);
    expect(errorMessage).toBeTruthy();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    const timestamp = Date.now();
    const testEmail = `user${timestamp}@test.com`;
    const testPassword = 'Test123!@#';  // pragma: allowlist secret

    // Register user
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    await getStartedButton.click();
    await page.waitForSelector('.auth-form', { timeout: 5000 });

    const registerTab = page.getByRole('button', { name: 'Register' });
    await registerTab.click();
    await page.waitForTimeout(500);

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.fill('input#confirm-password', testPassword);

    await page.getByTestId('register-submit-btn').click();
    await page.waitForTimeout(3000);

    // Look for logout button in header
    const logoutButton = page.getByRole('button', { name: /logout/i });
    await expect(logoutButton).toBeVisible({ timeout: 5000 });

    // Click logout
    await logoutButton.click();

    // Should be redirected to landing page
    await page.waitForTimeout(2000);
    // Check for either "Get Started" or "Log In" button
    const landingGetStarted = page.getByRole('button', { name: /get started/i });
    const landingLogin = page.getByRole('button', { name: /log in/i });
    const getStartedVisible = await landingGetStarted.isVisible().catch(() => false);
    const loginVisible = await landingLogin.isVisible().catch(() => false);
    expect(getStartedVisible || loginVisible).toBeTruthy();
  });
});
