import { test, expect } from "@playwright/test";

/**
 * Authentication Tests
 * Tests for user registration, login, and authentication flows
 */

test.describe("Authentication", () => {
  // Robust locator: try data-testid -> CSS fallback (with text) -> CSS fallback -> role/text
  async function findLocator(
    page,
    { testId, fallbackCssWithText, fallbackCss, role, nameRegex }
  ) {
    if (testId) {
      const byTestId = page.getByTestId(testId);
      if (await byTestId.isVisible().catch(() => false)) return byTestId;
    }
    if (fallbackCssWithText) {
      const loc = page.locator(fallbackCssWithText).first();
      if (await loc.isVisible().catch(() => false)) return loc;
    }
    if (fallbackCss) {
      const loc = page.locator(fallbackCss).first();
      if (await loc.isVisible().catch(() => false)) return loc;
    }
    if (role && nameRegex) {
      const byRole = page.getByRole(role, { name: nameRegex });
      if (await byRole.isVisible().catch(() => false)) return byRole;
    }
    return testId ? page.getByTestId(testId) : page.locator("");
  }

  // Fill an input: try data-testid first, then fallbacks (CSS selectors array)
  async function fillInput(page, testId, fallbacks = [], value) {
    if (testId) {
      const sel = `[data-testid="${testId}"]`;
      if (
        await page
          .locator(sel)
          .first()
          .isVisible()
          .catch(() => false)
      ) {
        await page.fill(sel, value);
        return;
      }
    }
    for (const s of fallbacks) {
      const loc = page.locator(s).first();
      if (await loc.isVisible().catch(() => false)) {
        await loc.fill(value);
        return;
      }
    }
    // last resort: try testId selector (will throw)
    if (testId) await page.fill(`[data-testid="${testId}"]`, value);
  }

  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should load the homepage without errors", async ({ page }) => {
    await expect(page).toHaveTitle(/Tapin/i);
  });

  test("should show login/register form", async ({ page }) => {
    // Wait for landing page to load
    await page.waitForLoadState("domcontentloaded");

    // Look for initial landing buttons (use test ids)
    const loginButton = page.getByTestId("login-btn");
    const getStartedButton = page.getByTestId("get-started-btn");

    // At least one should be visible
    const loginVisible = await loginButton.isVisible().catch(() => false);
    const getStartedVisible = await getStartedButton
      .isVisible()
      .catch(() => false);

    expect(loginVisible || getStartedVisible).toBeTruthy();

    // Click to open auth form
    if (loginVisible) {
      await loginButton.click();
    } else {
      await getStartedButton.click();
    }

    // Wait for auth form to appear
    await page.waitForSelector(".auth-form", { timeout: 5000 });

    // Verify auth tabs are visible
    const loginTab = await findLocator(page, {
      testId: "auth-tab-login",
      fallbackCssWithText: 'button.auth-tab:has-text("Login")',
      role: "button",
      nameRegex: /login/i,
    });
    const registerTab = await findLocator(page, {
      testId: "auth-tab-register",
      fallbackCssWithText: 'button.auth-tab:has-text("Register")',
      role: "button",
      nameRegex: /register/i,
    });
    await expect(loginTab).toBeVisible();
    await expect(registerTab).toBeVisible();
  });

  test("should register a new volunteer user", async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `volunteer${timestamp}@test.com`;

    // Click Get Started to open auth form
    const getStartedButton = page.getByTestId("get-started-btn");
    await getStartedButton.click();

    // Wait for auth form
    await page.waitForSelector(".auth-form", { timeout: 5000 });

    // Click Register tab
    const registerTab = await findLocator(page, {
      testId: "auth-tab-register",
      fallbackCssWithText: 'button.auth-tab:has-text("Register")',
      role: "button",
      nameRegex: /register/i,
    });
    await registerTab.click();

    // Wait a moment for tab switch
    await page.waitForTimeout(500);

    // Fill registration form (support deployed selectors)
    await fillInput(
      page,
      "auth-email-input",
      ["#email", 'input[type="email"]'],
      testEmail
    );
    await fillInput(
      page,
      "auth-password-input",
      ["#password", 'input[type="password"]'],
      "Test123!@#"
    );
    await fillInput(
      page,
      "auth-confirm-password-input",
      ["#confirm-password", "input#confirm-password", 'input[type="password"]'],
      "Test123!@#"
    );

    // Select volunteer role (should be default)
    const volunteerRadio = page.locator('input[value="volunteer"]').first();
    if (await volunteerRadio.isVisible().catch(() => false)) {
      await volunteerRadio.check();
    }

    // Submit form
    const submitButton = page.getByTestId("register-submit-btn");
    await submitButton.click();

    // Should show listings or dashboard after successful registration
    await page.waitForTimeout(3000);

    // Verify we're no longer on the auth form or we see the main app
    const mainContent = await page
      .locator("main")
      .isVisible()
      .catch(() => false);
    expect(mainContent).toBeTruthy();
  });

  test("should login with valid credentials", async ({ page }) => {
    // First register a user
    const timestamp = Date.now();
    const testEmail = `user${timestamp}@test.com`;
    const testPassword = "Test123!@#"; // pragma: allowlist secret

    // Register user
    const getStartedButton = page.getByTestId("get-started-btn");
    await getStartedButton.click();
    await page.waitForSelector(".auth-form", { timeout: 5000 });

    const registerTab = await findLocator(page, {
      testId: "auth-tab-register",
      fallbackCssWithText: 'button.auth-tab:has-text("Register")',
      role: "button",
      nameRegex: /register/i,
    });
    await registerTab.click();
    await page.waitForTimeout(500);

    await fillInput(
      page,
      "auth-email-input",
      ["#email", 'input[type="email"]'],
      testEmail
    );
    await fillInput(
      page,
      "auth-password-input",
      ["#password", 'input[type="password"]'],
      testPassword
    );
    await fillInput(
      page,
      "auth-confirm-password-input",
      ["#confirm-password", "input#confirm-password", 'input[type="password"]'],
      testPassword
    );

    await page.getByTestId("register-submit-btn").click();
    await page.waitForTimeout(2000);

    // Clear local storage to force re-login
    await page.evaluate(() => localStorage.clear());
    await page.goto("/");

    // Now login with registered credentials
    const loginButton = page.getByTestId("login-btn");
    await loginButton.click();
    await page.waitForSelector(".auth-form", { timeout: 5000 });

    // Should default to login tab
    await page.fill('[data-testid="auth-email-input"]', testEmail);
    await page.fill('[data-testid="auth-password-input"]', testPassword);
    await page.getByTestId("login-submit-btn").click();

    // Should be authenticated and see main app
    await page.waitForTimeout(3000);
    const mainContent = await page
      .locator("main")
      .isVisible()
      .catch(() => false);
    expect(mainContent).toBeTruthy();
  });

  test("should show error for invalid login", async ({ page }) => {
    // Click Log In to open auth form
    const loginButton = page.getByTestId("login-btn");
    await loginButton.click();
    await page.waitForSelector(".auth-form", { timeout: 5000 });

    // Fill with invalid credentials
    await fillInput(
      page,
      "auth-email-input",
      ["#email", 'input[type="email"]'],
      "invalid@test.com"
    );
    await fillInput(
      page,
      "auth-password-input",
      ["#password", 'input[type="password"]'],
      "wrongpassword"
    );
    await page.getByTestId("login-submit-btn").click();

    // Should show error
    await page.waitForTimeout(2000);
    const errorMessage = await page
      .locator(".error")
      .isVisible()
      .catch(() => false);
    expect(errorMessage).toBeTruthy();
  });

  test("should logout successfully", async ({ page }) => {
    // Login first
    const timestamp = Date.now();
    const testEmail = `user${timestamp}@test.com`;
    const testPassword = "Test123!@#"; // pragma: allowlist secret

    // Register user
    const getStartedButton = page.getByTestId("get-started-btn");
    await getStartedButton.click();
    await page.waitForSelector(".auth-form", { timeout: 5000 });

    const registerTab = await findLocator(page, {
      testId: "auth-tab-register",
      fallbackCssWithText: 'button.auth-tab:has-text("Register")',
      role: "button",
      nameRegex: /register/i,
    });
    await registerTab.click();
    await page.waitForTimeout(500);

    await fillInput(page, null, ["#email", 'input[type="email"]'], testEmail);
    await fillInput(
      page,
      null,
      ["#password", 'input[type="password"]'],
      testPassword
    );
    await fillInput(
      page,
      null,
      ["#confirm-password", "input#confirm-password"],
      testPassword
    );

    await page.getByTestId("register-submit-btn").click();
    await page.waitForTimeout(3000);

    // Look for logout button in header
    const logoutButton = await findLocator(page, {
      testId: "logout-btn",
      fallbackCssWithText: 'button:has-text("Log Out")',
      fallbackCss:
        'button[aria-label*="logout" i], button[aria-label*="sign out" i]',
      role: "button",
      nameRegex: /log out|logout|sign out/i,
    });
    await expect(logoutButton).toBeVisible({ timeout: 5000 });

    // Click logout
    await logoutButton.click();

    // Should be redirected to landing page
    await page.waitForTimeout(2000);
    // Check for either "Get Started" or "Log In" button
    const landingGetStarted = page.getByRole("button", {
      name: /get started/i,
    });
    const landingLogin = page.getByRole("button", { name: /log in/i });
    const getStartedVisible = await landingGetStarted
      .isVisible()
      .catch(() => false);
    const loginVisible = await landingLogin.isVisible().catch(() => false);
    expect(getStartedVisible || loginVisible).toBeTruthy();
  });
});
