# Tapin E2E Test Suite

Comprehensive end-to-end tests for the Tapin volunteer discovery platform using Playwright.

## Test Coverage

### 01-auth.spec.js
- User registration (volunteer and organization roles)
- Login with valid/invalid credentials
- Logout functionality
- Authentication error handling

### 02-event-search.spec.js
- Event search by location (city/state)
- Category filtering
- Web search toggle
- Event detail views
- Loading states
- Empty search results handling

### 03-surprise-me.spec.js
- Surprise Me feature interface
- Mood selection (energetic, chill, creative, social, romantic, adventurous)
- Surprise event generation
- Surprise explanation display
- Preference customization (budget, time, adventure level)
- Event regeneration

### 04-personalized-discovery.spec.js
- Personalized event feed
- Match score display
- Location-based personalization
- Organizational values display
- Event sorting by match score
- Multi-source event aggregation (Database + Web)

### 05-gamification.spec.js
- Achievements page display
- User level and XP tracking
- Achievement progress display
- XP earning from interactions
- Locked/unlocked achievements
- Achievement descriptions

### 06-event-interactions.spec.js
- Like/unlike events
- Super-like functionality
- Mark events as attending
- Event view tracking
- Share event functionality
- Interaction state persistence

## Running Tests

### Prerequisites
```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### Run All Tests
```bash
npm test
```

### Run Specific Test Suite
```bash
npx playwright test tests/e2e/01-auth.spec.js
```

### Run Tests by Browser
```bash
npm run test:chromium
npm run test:firefox
npm run test:webkit
```

### Run Tests in UI Mode
```bash
npm run test:ui
```

### Run Tests in Headed Mode (visible browser)
```bash
npm run test:headed
```

### View Test Report
```bash
npm run test:report
```

## Test Architecture

### Configuration
- **Config File**: `playwright.config.js`
- **Test Directory**: `tests/e2e/`
- **Base URL**: `http://localhost:5173` (Vite dev server)
- **Backend URL**: `http://127.0.0.1:5000` (Flask API)

### Web Servers
Tests automatically start two web servers:
1. **Backend**: Flask API with mock LLM provider
2. **Frontend**: Vite dev server

### Browser Support
- Chromium (Desktop Chrome)
- Firefox (Desktop)
- WebKit (Desktop Safari)
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)

### Test Features
- **Parallel Execution**: Tests run in parallel for faster execution
- **Automatic Retries**: 2 retries in CI, 0 locally
- **Screenshots**: Captured on failure
- **Videos**: Recorded on failure
- **Traces**: Captured on first retry

## Test Best Practices

1. **Authentication**: Each test suite creates its own user with timestamp-based email to avoid conflicts
2. **Isolation**: Tests don't depend on each other - each test can run independently
3. **Resilience**: Tests use `.catch(() => false)` for optional UI elements
4. **Timeouts**: Appropriate timeouts for API calls and UI updates
5. **Assertions**: Clear expectations with helpful error messages

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Install dependencies
  run: cd src/front && npm ci

- name: Install Playwright Browsers
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

## Debugging Tests

### Debug Specific Test
```bash
npx playwright test tests/e2e/01-auth.spec.js --debug
```

### Show Trace Viewer
```bash
npx playwright show-trace trace.zip
```

### VS Code Extension
Install the [Playwright Test for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright) extension for:
- Test discovery
- Running tests from editor
- Debugging with breakpoints
- Viewing test results inline

## Test Data

Tests create users with unique timestamps:
```javascript
const timestamp = Date.now();
const testEmail = `volunteer${timestamp}@test.com`;
```

This ensures no conflicts between test runs and allows running tests multiple times.

## Common Issues

### Backend Not Starting
- Check that Flask dependencies are installed: `cd ../backend && pipenv install`
- Verify PYTHONPATH is set correctly
- Ensure port 5000 is available

### Frontend Not Starting
- Check that Node dependencies are installed: `npm install`
- Verify port 5173 is available
- Check Vite configuration

### Tests Timing Out
- Increase timeout in `playwright.config.js`
- Check network connectivity
- Verify both servers are running

### Flaky Tests
- Tests are designed to be resilient with proper waits
- Use `test.only()` to isolate and debug specific tests
- Check for race conditions in UI updates

## Coverage Report

To generate a coverage report:
```bash
# Run tests with coverage
npx playwright test --reporter=html

# View report
npm run test:report
```

## Future Enhancements

- [ ] Add API response mocking for faster tests
- [ ] Add visual regression testing
- [ ] Add accessibility (a11y) testing with axe-core
- [ ] Add performance testing
- [ ] Add mobile-specific gesture tests
- [ ] Add internationalization (i18n) tests
