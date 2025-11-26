# Playwright Test Failures - Complete Fix Guide

## 📊 Test Results Summary

**Result:** 136 passed ✅ | 64 failed ❌ (68% pass rate)

**Critical Issues Identified:**
1. Tests run against deployed site (Fly.dev) instead of local servers
2. API connectivity issues
3. Missing data-testid attributes in components
4. Clipboard permission errors
5. UI selectors don't match actual rendered elements
6. Backend not accessible or seeded with test data

---

## 🔴 Root Cause Analysis

### Issue #1: Wrong Test Target
**Problem:** `playwright.config.js` line 18:
```javascript
baseURL: 'https://tapin-correct.fly.dev',
```

**Why it fails:**
- Deployed site may be down or slow
- Backend API not accessible
- No test data seeded
- CORS issues
- Network latency causing timeouts

**Solution:** Run against local dev servers

---

### Issue #2: Commented Out webServer Config
**Problem:** Lines 36-51 in `playwright.config.js` are commented out

**Why it fails:**
- Playwright doesn't start local backend/frontend
- Tests have nothing to test against if deployed site is down

**Solution:** Uncomment and configure properly

---

### Issue #3: Missing Test IDs
**Problem:** Tests use generic selectors:
```javascript
await page.getByRole('button', { name: /logout/i })
await page.locator('.auth-form')
```

**Why it fails:**
- UI structure changed during modernization
- Selectors are brittle and break easily
- Class names might have changed

**Solution:** Add `data-testid` attributes to components

---

### Issue #4: Clipboard Permission Error
**Problem:** `06-event-interactions.spec.js`:
```javascript
await context.grantPermissions(['clipboard-read', 'clipboard-write']);
```

**Why it fails:**
- `clipboard-write` is not a valid Playwright permission
- Only `clipboard-read` is supported

**Solution:** Remove unsupported permission or mock clipboard API

---

### Issue #5: API Not Seeded
**Problem:** Tests expect data that doesn't exist
- Personalized feed expects events
- Search expects results
- No test user accounts

**Solution:** Seed test database or mock API responses

---

## ✅ Complete Fix Implementation

### Fix 1: Update playwright.config.js (CRITICAL)

**Replace entire file with:**

```javascript
import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Tapin E2E tests
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false, // Changed to false for stability
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1, // Allow 1 retry locally
  workers: process.env.CI ? 1 : 2, // Limit workers for stability
  timeout: 60 * 1000, // 60 second timeout per test

  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
    ['json', { outputFile: 'test-results.json' }]
  ],

  use: {
    // Use local dev server instead of deployed site
    baseURL: process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:5173',

    // Increased timeouts for API calls
    actionTimeout: 15 * 1000,
    navigationTimeout: 30 * 1000,

    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // Set viewport
    viewport: { width: 1280, height: 720 },
  },

  // Run local servers before tests
  webServer: [
    // Backend API server
    {
      command: 'cd ../backend && python -m flask run --port=5000',
      url: 'http://localhost:5000/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        FLASK_APP: 'app:create_app',
        FLASK_ENV: 'test',
        DATABASE_URL: process.env.TEST_DATABASE_URL || 'sqlite:///test.db',
        LLM_PROVIDER: 'mock',
      },
    },
    // Frontend dev server
    {
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 60 * 1000,
      env: {
        VITE_API_URL: 'http://localhost:5000',
      },
    },
  ],

  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Optionally enable other browsers after fixing chromium
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    // Mobile browsers - enable after desktop works
    // {
    //   name: 'mobile-chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'mobile-safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],
});
```

**Key changes:**
- ✅ baseURL points to local dev server
- ✅ webServer starts backend + frontend
- ✅ Longer timeouts for stability
- ✅ Only test Chromium initially (faster iteration)
- ✅ Mock LLM provider for tests

---

### Fix 2: Add Test IDs to Components

#### AuthForm.jsx - Add test IDs:

```jsx
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
  id="email"
  type="email"
  className="form-input"
  placeholder="you@example.com"
  required
/>

// Password input
<input
  data-testid="auth-password-input"
  id="password"
  type="password"
  className="form-input"
  placeholder="••••••••"
  required
/>

// Confirm password (register only)
<input
  data-testid="auth-confirm-password-input"
  id="confirm-password"
  type="password"
  className="form-input"
  required
/>

// Submit button
<button
  data-testid={mode === 'login' ? 'login-submit-btn' : 'register-submit-btn'}
  type="submit"
  className="btn btn-primary w-100"
>
  {mode === 'login' ? 'Log In' : 'Sign Up'}
</button>
```

#### Navigation.jsx - Add test IDs:

```jsx
// Logout button
<button
  data-testid="logout-button"
  onClick={handleLogout}
  className="btn btn-ghost"
>
  Logout
</button>

// Get Started button
<button
  data-testid="get-started-btn"
  className="btn btn-primary btn-lg"
  onClick={() => setShowAuth(true)}
>
  Get Started
</button>

// Log In button
<button
  data-testid="login-btn"
  className="btn btn-secondary btn-lg"
  onClick={() => setShowAuth(true)}
>
  Log In
</button>
```

#### EventCard.jsx - Add test IDs:

```jsx
<div
  data-testid="event-card"
  className="card event-card"
  onClick={onClick}
>
  <h3
    data-testid="event-title"
    className="event-card-title"
  >
    {event.title}
  </h3>

  <button
    data-testid="like-event-btn"
    onClick={handleLike}
  >
    ❤️ Like
  </button>

  <button
    data-testid="attend-event-btn"
    onClick={handleAttend}
  >
    ✓ Attend
  </button>

  <button
    data-testid="share-event-btn"
    onClick={handleShare}
  >
    ↗ Share
  </button>
</div>
```

#### EventDiscovery.jsx - Add test IDs:

```jsx
// Location search
<input
  data-testid="location-search-input"
  placeholder="Search city or location..."
  className="form-input"
/>

// Search button
<button
  data-testid="search-events-btn"
  className="btn btn-primary"
>
  Search
</button>

// Surprise Me button
<button
  data-testid="surprise-me-btn"
  onClick={() => setShowSurpriseMe(true)}
  className="btn btn-accent btn-lg"
>
  🎲 Surprise Me!
</button>

// Events container
<div
  data-testid="events-list"
  className="events-grid"
>
  {/* Event cards */}
</div>
```

---

### Fix 3: Fix Clipboard Permission Error

**File:** `tests/e2e/06-event-interactions.spec.js`

**Find (around line 10-15):**
```javascript
await context.grantPermissions(['clipboard-read', 'clipboard-write']);
```

**Replace with:**
```javascript
// Only use supported permissions
await context.grantPermissions(['clipboard-read']);

// OR mock the clipboard API
await page.evaluateOnNewDocument(() => {
  Object.assign(navigator.clipboard, {
    writeText: async (text) => {
      window.__clipboardText = text;
      return Promise.resolve();
    },
    readText: async () => {
      return Promise.resolve(window.__clipboardText || '');
    },
  });
});
```

---

### Fix 4: Update Test Selectors

**File:** `tests/e2e/01-auth.spec.js`

**Replace generic selectors with test IDs:**

**Before:**
```javascript
const loginButton = page.getByRole('button', { name: /log in/i });
const getStartedButton = page.getByRole('button', { name: /get started/i });
```

**After:**
```javascript
const loginButton = page.getByTestId('login-btn');
const getStartedButton = page.getByTestId('get-started-btn');
```

**Before:**
```javascript
await page.waitForSelector('.auth-form', { timeout: 5000 });
```

**After:**
```javascript
await page.waitForSelector('[data-testid="auth-form"]', { timeout: 10000 });
```

**Before:**
```javascript
const registerTab = page.getByRole('button', { name: 'Register' });
```

**After:**
```javascript
const registerTab = page.getByTestId('auth-tab-register');
```

**Before:**
```javascript
await page.fill('input[type="email"]', testEmail);
await page.fill('input[type="password"]', testPassword);
```

**After:**
```javascript
await page.getByTestId('auth-email-input').fill(testEmail);
await page.getByTestId('auth-password-input').fill(testPassword);
```

**Before:**
```javascript
const logoutButton = page.getByRole('button', { name: /logout/i });
```

**After:**
```javascript
const logoutButton = page.getByTestId('logout-button');
```

---

### Fix 5: Create Test Environment File

**Create:** `src/front/.env.test`

```bash
VITE_API_URL=http://localhost:5000
VITE_ENV=test
```

---

### Fix 6: Create Backend Test Setup

**Create:** `src/backend/tests/conftest.py`

```python
import pytest
from app import create_app
from app.models import db
import os

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    os.environ['FLASK_ENV'] = 'test'
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    os.environ['LLM_PROVIDER'] = 'mock'

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    with app.app_context():
        db.create_all()
        seed_test_data()
        yield app
        db.session.remove()
        db.drop_all()

def seed_test_data():
    """Seed database with test data"""
    # Add test users, events, etc.
    pass
```

---

## 🚀 Quick Fix Commands

### Step 1: Update Config (5 min)
```bash
cd src/front

# Backup current config
cp playwright.config.js playwright.config.js.backup

# Apply new config (copy from Fix 1 above)
# Edit playwright.config.js
```

### Step 2: Add Test IDs (20 min)
```bash
# Edit each component file and add data-testid attributes
# Follow Fix 2 examples above

cd src/front/src/components
# Edit: AuthForm.jsx, Navigation.jsx, EventCard.jsx

cd ../pages
# Edit: EventDiscovery.jsx
```

### Step 3: Fix Clipboard Test (2 min)
```bash
cd tests/e2e
# Edit: 06-event-interactions.spec.js
# Apply Fix 3 above
```

### Step 4: Update Test Selectors (15 min)
```bash
cd tests/e2e
# Edit: 01-auth.spec.js, 02-event-search.spec.js
# Replace generic selectors with getByTestId()
# Follow Fix 4 examples
```

### Step 5: Run Tests Locally (5 min)
```bash
cd src/front

# Install Playwright browsers if not already installed
npx playwright install chromium

# Run tests
npx playwright test --project=chromium

# Run specific failing test in headed mode
npx playwright test tests/e2e/01-auth.spec.js --project=chromium --headed

# Show HTML report
npx playwright show-report
```

---

## 📊 Priority Order

### 🔴 Priority 1 (Do First - 30 min):
1. ✅ Update `playwright.config.js` (Fix 1)
2. ✅ Add test IDs to AuthForm (Fix 2)
3. ✅ Fix clipboard error (Fix 3)
4. ✅ Run auth tests only: `npx playwright test 01-auth --project=chromium`

### 🟡 Priority 2 (Next - 30 min):
1. ✅ Add test IDs to EventDiscovery, EventCard
2. ✅ Update event search test selectors
3. ✅ Run search tests: `npx playwright test 02-event --project=chromium`

### 🟢 Priority 3 (Polish - 20 min):
1. ✅ Add remaining test IDs
2. ✅ Update all test selectors
3. ✅ Run full suite: `npx playwright test --project=chromium`

---

## ✅ Verification Checklist

After fixes, verify:

- [ ] `npx playwright test 01-auth --project=chromium` - All auth tests pass
- [ ] `npx playwright test 02-event-search --project=chromium` - Search tests pass
- [ ] `npx playwright test 03-surprise --project=chromium` - Surprise Me tests pass
- [ ] `npx playwright test 04-personalized --project=chromium` - Discovery tests pass
- [ ] `npx playwright test 06-event-interactions --project=chromium` - Interaction tests pass
- [ ] No clipboard permission errors
- [ ] Tests run against local servers (check console output)
- [ ] Screenshots show correct UI (check test-results/)

---

## 🐛 Debugging Tips

### If tests still fail:

**1. Check servers are running:**
```bash
# Terminal 1: Backend
cd src/backend
python -m flask run --port=5000

# Terminal 2: Frontend
cd src/front
npm run dev

# Terminal 3: Tests
cd src/front
npx playwright test
```

**2. Run in headed mode to watch:**
```bash
npx playwright test 01-auth --project=chromium --headed --timeout=120000
```

**3. Use debug mode:**
```bash
npx playwright test 01-auth --project=chromium --debug
```

**4. Check screenshots:**
```bash
open test-results/01-auth-*/test-failed-1.png
```

**5. View trace:**
```bash
npx playwright show-trace test-results/01-auth-*/trace.zip
```

---

## 📈 Expected Results

### Before fixes:
- 136 passed / 64 failed (68% pass rate)

### After Priority 1 fixes:
- ~160 passed / 40 failed (80% pass rate)
- All auth tests passing

### After all fixes:
- ~190+ passed / <10 failed (95%+ pass rate)
- Only edge case failures

---

## 🎯 Next Steps

1. **Start with Priority 1 fixes** (30 min)
2. **Run auth tests** and verify they pass
3. **Move to Priority 2** if auth passes
4. **Iterate** until all critical tests pass
5. **Enable other browsers** once Chromium is stable

**Total estimated time: 1.5-2 hours for complete fix**

---

**Start with playwright.config.js update and test ID additions! 🚀**
