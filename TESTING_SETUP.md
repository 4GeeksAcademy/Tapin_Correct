# Testing Setup Documentation

## Overview
Comprehensive testing infrastructure for the Tapin volunteer discovery platform, covering both backend unit tests and frontend end-to-end tests.

## Backend Testing (Python/Pytest)

### Test Framework
- **Framework**: pytest 9.0.1
- **Location**: `src/backend/tests/`
- **Test Runner**: pipenv run pytest

### Gamification Tests
**File**: `src/backend/tests/test_gamification.py`

**Coverage**:
- ✅ Achievement endpoints (volunteer and organization)
- ✅ Badge earning system
- ✅ XP progression and level calculation
- ✅ Multiple achievement types:
  - Weekend Warrior (5 weekend events streak)
  - Category Completionist (try all 22 categories)
  - Early Bird (10 events discovered >1 week before)
  - Last Minute Larry (10 same-day events)
  - Social Butterfly (20 events with friends)
  - Local Legend (50 events in city)
  - Explorer (events in 5 different cities)
  - Night Owl (15 events after 8 PM)
  - Free Spirit (20 free events)
  - Culture Vulture (15 arts/culture events)

**Test Results**: ✅ All 15 tests passing

**Run Command**:
```bash
cd src/backend
PYTHONPATH=/Users/houseofobi/Documents/GitHub/Tapin_Correct/src:/Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend:$PYTHONPATH \
LLM_PROVIDER=mock \
pipenv run pytest tests/test_gamification.py -v
```

## Frontend Testing (Playwright)

### Test Framework
- **Framework**: Playwright 1.57.0
- **Location**: `src/front/tests/e2e/`
- **Configuration**: `src/front/playwright.config.js`

### Test Suites Created

#### 1. Authentication Tests (`01-auth.spec.js`)
- Homepage loading
- Login/register form display
- New user registration (volunteer role)
- Login with valid credentials
- Error handling for invalid login
- Logout functionality

#### 2. Event Search Tests (`02-event-search.spec.js`)
- Event search interface
- Location-based search (city/state)
- Category filtering
- Web search toggle
- Event detail views
- Loading states
- Empty results handling

#### 3. Surprise Me Tests (`03-surprise-me.spec.js`)
- Surprise Me interface
- Mood selection (6 moods: energetic, chill, creative, social, romantic, adventurous)
- Surprise event generation
- Surprise explanation display
- Preference customization (budget, time, adventure level)
- Event regeneration
- Match score display

#### 4. Personalized Discovery Tests (`04-personalized-discovery.spec.js`)
- Personalized feed display
- Match score indicators
- Location-based personalization
- Organizational values display
- Event sorting by match score
- Multi-source event aggregation (Database + Web)
- Feed refresh functionality

#### 5. Gamification Tests (`05-gamification.spec.js`)
- Achievements page
- User level and XP display
- Achievement progress tracking
- XP earning from interactions
- Locked/unlocked achievement states
- Achievement descriptions

#### 6. Event Interaction Tests (`06-event-interactions.spec.js`)
- Like/unlike events
- Super-like functionality
- Mark events as attending
- Event view tracking
- Share event functionality
- Interaction state persistence
- Unauthenticated viewing

### Browser Support
- ✅ Chromium (Desktop Chrome)
- ✅ Firefox (Desktop)
- ✅ WebKit (Desktop Safari)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

### Test Features
- **Parallel Execution**: Multiple tests run simultaneously
- **Automatic Retries**: 2 retries in CI, 0 locally
- **Screenshots**: Captured on test failure
- **Videos**: Recorded on test failure
- **Traces**: Captured on first retry for debugging

### Running Playwright Tests

**Install Dependencies**:
```bash
cd src/front
npm install
npx playwright install chromium
```

**Run All Tests**:
```bash
npm test
```

**Run Specific Suite**:
```bash
npx playwright test tests/e2e/01-auth.spec.js
```

**Run by Browser**:
```bash
npm run test:chromium
npm run test:firefox
npm run test:webkit
```

**Interactive UI Mode**:
```bash
npm run test:ui
```

**Headed Mode (visible browser)**:
```bash
npm run test:headed
```

**View Test Report**:
```bash
npm run test:report
```

## Test Architecture

### Backend Tests
- **Database**: SQLite in-memory database per test
- **Authentication**: JWT token-based
- **Fixtures**: Client, volunteer_auth, organization_auth, sample_event
- **LLM Provider**: Mock provider for tests (no API calls)

### Frontend Tests
- **Web Servers**: Auto-start both backend (Flask) and frontend (Vite)
- **Backend URL**: http://127.0.0.1:5000
- **Frontend URL**: http://localhost:5173
- **Test Isolation**: Each test creates unique users (timestamp-based emails)
- **Resilience**: Tests handle optional UI elements gracefully

## Test Data Strategy

### Backend
- Uses in-memory SQLite database
- Fresh database per test suite
- Predefined test credentials: `test@example.com` / `password123`
- Sample events created via fixtures

### Frontend
- Timestamp-based user emails: `volunteer${Date.now()}@test.com`
- Prevents conflicts between test runs
- Each test suite creates its own authenticated user
- Tests can run multiple times without cleanup

## CI/CD Integration

### Recommended GitHub Actions Workflow
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          cd src/backend
          pip install pipenv
          pipenv install --dev
      - name: Run backend tests
        run: |
          cd src/backend
          PYTHONPATH=/Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend \
          LLM_PROVIDER=mock \
          pipenv run pytest tests/ -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd src/front && npm ci
      - name: Install Playwright
        run: cd src/front && npx playwright install --with-deps chromium
      - name: Run Playwright tests
        run: cd src/front && npm test
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: src/front/playwright-report/
```

## Test Coverage Summary

### Backend Coverage
- ✅ Gamification System (15 tests)
  - Achievements endpoint
  - Badge earning
  - XP calculation
  - Level progression
  - Multi-user isolation

### Frontend Coverage
- ✅ Authentication (6+ tests)
- ✅ Event Search (8+ tests)
- ✅ Surprise Me (7+ tests)
- ✅ Personalized Discovery (7+ tests)
- ✅ Gamification (6+ tests)
- ✅ Event Interactions (7+ tests)

**Total**: 40+ end-to-end tests + 15 backend unit tests = **55+ automated tests**

## Known Issues & Warnings

### Backend
- **Deprecation Warnings**:
  - `datetime.utcnow()` usage (should use `datetime.now(datetime.UTC)`)
  - `Query.get()` method (should use `Session.get()`)
  - These are non-critical and do not affect functionality

### Frontend
- **Optional UI Elements**: Tests gracefully handle elements that may not exist
- **Async Operations**: Proper waits implemented for API calls
- **Multi-browser Support**: All tests designed to work across browsers

## Debugging Tests

### Backend
```bash
# Run specific test
pytest tests/test_gamification.py::TestAchievementsEndpoint::test_volunteer_achievements_empty -v

# Run with print statements
pytest tests/test_gamification.py -v -s

# Run with debugger
pytest tests/test_gamification.py --pdb
```

### Frontend
```bash
# Debug mode
npx playwright test tests/e2e/01-auth.spec.js --debug

# Show trace
npx playwright show-trace trace.zip

# Run single test
npx playwright test tests/e2e/01-auth.spec.js -g "should login with valid credentials"
```

## Future Enhancements

### Backend
- [ ] Add integration tests for Google Search API
- [ ] Add tests for PersonalizationEngine
- [ ] Add tests for SurpriseEngine
- [ ] Add performance benchmarks
- [ ] Add database migration tests

### Frontend
- [ ] Add API mocking for faster tests
- [ ] Add visual regression testing
- [ ] Add accessibility (a11y) tests with axe-core
- [ ] Add performance testing with Lighthouse
- [ ] Add mobile gesture tests
- [ ] Add i18n tests
- [ ] Add component unit tests (React Testing Library)

## Maintenance

### Updating Tests
1. When adding new features, add corresponding tests
2. Follow existing test patterns and naming conventions
3. Ensure tests are isolated and don't depend on each other
4. Use descriptive test names that explain what is being tested
5. Add comments for complex test logic

### Test Stability
- Tests are designed to be resilient with proper waits
- Use `test.only()` to isolate flaky tests for debugging
- Check for race conditions if tests fail intermittently
- Verify both web servers are running before test execution

## Documentation
- **Backend Tests**: See inline comments in test files
- **Frontend Tests**: See `src/front/tests/e2e/README.md`
- **Playwright Config**: See `src/front/playwright.config.js`
- **Test Best Practices**: Follow patterns in existing tests

## Support

For issues or questions about the test suite:
1. Check test output and error messages
2. Review test logs in `playwright-report/`
3. Use `--debug` flag for step-by-step debugging
4. Consult Playwright documentation: https://playwright.dev
5. Consult Pytest documentation: https://docs.pytest.org

---

**Status**: ✅ Test infrastructure fully operational
**Last Updated**: November 25, 2025
**Maintainer**: Development Team
