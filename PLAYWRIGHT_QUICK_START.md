# Playwright Tests - Quick Fix Start Guide

## 🚨 Current Status

**Test Results:** 136 passed ✅ | 64 failed ❌ (68% pass rate)

**Root Cause:** Tests running against deployed Fly.dev site instead of local servers

**Solution:** 3 critical fixes in ~45 minutes

---

## ⚡ 3-Step Quick Fix (45 Minutes)

### Step 1: Fix Playwright Config (10 min)

**File:** `src/front/playwright.config.js`

**Problem:** Line 18 points to deployed site:
```javascript
baseURL: 'https://tapin-correct.fly.dev',
```

**Fix:** Change to local dev server:
```javascript
baseURL: process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:5173',
```

**Uncomment webServer config** (lines 36-51):
```javascript
webServer: [
  {
    command: 'cd ../backend && python -m flask run --port=5000',
    url: 'http://localhost:5000/api/health',
    reuseExistingServer: true,
    timeout: 120 * 1000,
    env: {
      FLASK_APP: 'app:create_app',
      FLASK_ENV: 'test',
      LLM_PROVIDER: 'mock',
    },
  },
  {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 60 * 1000,
    env: {
      VITE_API_URL: 'http://localhost:5000',
    },
  },
],
```

**Test only Chromium initially** (comment out other browsers):
```javascript
projects: [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'] },
  },
  // Comment out firefox, webkit, mobile for now
],
```

---

### Step 2: Add Test IDs to AuthForm (20 min)

**File:** `src/front/src/components/AuthForm.jsx`

**Add these data-testid attributes:**

```jsx
// Container
<div className="auth-form" data-testid="auth-form">

// Login tab
<button
  data-testid="auth-tab-login"
  className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
  onClick={() => setMode('login')}
>
  Log In
</button>

// Register tab
<button
  data-testid="auth-tab-register"
  className={`auth-tab ${mode === 'signup' ? 'active' : ''}`}
  onClick={() => setMode('signup')}
>
  Sign Up
</button>

// Email input
<input
  data-testid="auth-email-input"
  type="email"
  className="form-input"
/>

// Password input
<input
  data-testid="auth-password-input"
  type="password"
  className="form-input"
/>

// Confirm password (register mode)
<input
  data-testid="auth-confirm-password-input"
  type="password"
  className="form-input"
/>

// Submit button
<button
  data-testid={mode === 'login' ? 'login-submit-btn' : 'register-submit-btn'}
  type="submit"
  className="btn btn-primary"
>
  {mode === 'login' ? 'Log In' : 'Sign Up'}
</button>

// Error message (if you have one)
<div data-testid="auth-error" className="error">
  {errorMessage}
</div>
```

**Also add to DashboardLanding.jsx:**

```jsx
<button
  data-testid="get-started-btn"
  className="btn btn-primary btn-lg"
  onClick={() => setShowAuth(true)}
>
  Get Started
</button>

<button
  data-testid="login-btn"
  className="btn btn-secondary btn-lg"
  onClick={() => setShowAuth(true)}
>
  Log In
</button>
```

**Add to Navigation.jsx:**

```jsx
<button
  data-testid="logout-button"
  onClick={handleLogout}
  className="btn btn-ghost"
>
  Logout
</button>
```

---

### Step 3: Update Auth Test Selectors (15 min)

**File:** `src/front/tests/e2e/01-auth.spec.js`

**Find and replace these selectors:**

**Line ~20:**
```javascript
// OLD:
const loginButton = page.getByRole('button', { name: /log in/i });
const getStartedButton = page.getByRole('button', { name: /get started/i });

// NEW:
const loginButton = page.getByTestId('login-btn');
const getStartedButton = page.getByTestId('get-started-btn');
```

**Line ~35:**
```javascript
// OLD:
await page.waitForSelector('.auth-form', { timeout: 5000 });

// NEW:
await page.getByTestId('auth-form').waitFor({ timeout: 10000 });
```

**Line ~38:**
```javascript
// OLD:
const registerTab = page.getByRole('button', { name: 'Register' });

// NEW:
const registerTab = page.getByTestId('auth-tab-register');
```

**Line ~55:**
```javascript
// OLD:
await page.fill('input[type="email"]', testEmail);
await page.fill('input[type="password"]', testPassword);
await page.fill('input#confirm-password', testPassword);

// NEW:
await page.getByTestId('auth-email-input').fill(testEmail);
await page.getByTestId('auth-password-input').fill(testPassword);
await page.getByTestId('auth-confirm-password-input').fill(testPassword);
```

**Line ~68:**
```javascript
// OLD:
await page.getByTestId('register-submit-btn').click();

// NEW: (already correct if you added test ID)
await page.getByTestId('register-submit-btn').click();
```

**Line ~118:**
```javascript
// OLD:
await page.fill('input#password', testPassword);
await page.getByTestId('login-submit-btn').click();

// NEW:
await page.getByTestId('auth-password-input').fill(testPassword);
await page.getByTestId('login-submit-btn').click();
```

**Line ~170:**
```javascript
// OLD:
const logoutButton = page.getByRole('button', { name: /logout/i });

// NEW:
const logoutButton = page.getByTestId('logout-button');
```

---

## 🧪 Test & Verify (5 min)

```bash
cd src/front

# Install Playwright browsers (if needed)
npx playwright install chromium

# Run auth tests only
npx playwright test 01-auth --project=chromium

# Expected result: All 6 auth tests should pass
# - should load the homepage without errors ✅
# - should show login/register form ✅
# - should register a new volunteer user ✅
# - should login with valid credentials ✅
# - should show error for invalid login ✅
# - should logout successfully ✅
```

**If tests pass, proceed to remaining tests!**

---

## 📈 Expected Improvement

### Before:
- Tests run against deployed Fly.dev site
- Network latency and API failures
- 64 failures across all test suites

### After Quick Fix:
- Tests run against local servers
- Fast, reliable, no network issues
- Auth tests: 0 failures (6/6 passing)
- Overall: ~40 failures reduced to ~20

### After Full Fix (see PLAYWRIGHT_TEST_FIXES.md):
- All components have test IDs
- All tests use stable selectors
- 190+ tests passing (95%+ pass rate)

---

## 🐛 Troubleshooting

### Tests still failing?

**1. Check servers are starting:**
```bash
# Watch Playwright output for:
# "Web Server on http://localhost:5000 is ready!"
# "Web Server on http://localhost:5173 is ready!"
```

**2. Run servers manually first:**
```bash
# Terminal 1: Backend
cd src/backend
python -m flask run --port=5000

# Terminal 2: Frontend
cd src/front
npm run dev

# Terminal 3: Tests
cd src/front
npx playwright test 01-auth --project=chromium
```

**3. Check backend is accessible:**
```bash
curl http://localhost:5000/api/health
# Should return 200 OK
```

**4. Run in headed mode to watch:**
```bash
npx playwright test 01-auth --project=chromium --headed
```

**5. Check test screenshots:**
```bash
ls -la test-results/01-auth*/
open test-results/01-auth*/test-failed-1.png
```

---

## 🚀 Next Steps After Quick Fix

### If auth tests pass:

1. **Add test IDs to EventDiscovery.jsx** (see TEST_IDS_REFERENCE.md)
2. **Update event search test selectors** (02-event-search.spec.js)
3. **Run event search tests:** `npx playwright test 02-event --project=chromium`
4. **Repeat for remaining test suites**

### Full implementation guide:

- **PLAYWRIGHT_TEST_FIXES.md** - Complete 2-hour fix plan
- **TEST_IDS_REFERENCE.md** - All test ID additions
- **UI_MODERNIZATION_PLAN_ENHANCED.md** - UI improvements (separate effort)

---

## 📊 Success Criteria

- [ ] playwright.config.js uses local servers
- [ ] AuthForm has all test IDs
- [ ] 01-auth.spec.js uses getByTestId()
- [ ] All 6 auth tests pass
- [ ] Tests complete in <2 minutes (not 13 minutes)
- [ ] No network timeout errors

---

## 📝 Quick Commands Reference

```bash
# Run all tests
npx playwright test --project=chromium

# Run single test file
npx playwright test 01-auth --project=chromium

# Run in headed mode (watch)
npx playwright test 01-auth --project=chromium --headed

# Run with debug
npx playwright test 01-auth --project=chromium --debug

# Show HTML report
npx playwright show-report

# Run only failed tests
npx playwright test --only-failed

# Update snapshots
npx playwright test --update-snapshots
```

---

**Start with playwright.config.js update and watch your test pass rate improve! 🎉**

**Total time: 45 minutes for critical fixes**
