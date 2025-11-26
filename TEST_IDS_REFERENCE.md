# Test IDs Reference - Quick Implementation Guide

## 🎯 Component Test ID Additions

### AuthForm.jsx
```jsx
// Container
<div className="auth-form" data-testid="auth-form">

// Tabs
<button data-testid="auth-tab-login" ...>Log In</button>
<button data-testid="auth-tab-register" ...>Sign Up</button>

// Inputs
<input data-testid="auth-email-input" type="email" .../>
<input data-testid="auth-password-input" type="password" .../>
<input data-testid="auth-confirm-password-input" type="password" .../>

// Submit buttons
<button data-testid="login-submit-btn" type="submit">Log In</button>
<button data-testid="register-submit-btn" type="submit">Sign Up</button>

// Error message
<div data-testid="auth-error" className="error">{error}</div>
```

### DashboardLanding.jsx
```jsx
// CTA Buttons
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

### Navigation.jsx
```jsx
// Logout button
<button
  data-testid="logout-button"
  onClick={handleLogout}
  className="btn btn-ghost"
>
  Logout
</button>

// Logo/Home link
<Link data-testid="nav-home-link" to="/">TapIn</Link>

// Nav links
<Link data-testid="nav-discover-link" to="/discover">Discover</Link>
<Link data-testid="nav-dashboard-link" to="/dashboard">Dashboard</Link>
```

### EventDiscovery.jsx
```jsx
// Location search
<input
  data-testid="location-search-input"
  type="text"
  placeholder="Enter city or location"
  value={locationInput}
  onChange={(e) => setLocationInput(e.target.value)}
/>

// Search button
<button
  data-testid="search-events-btn"
  onClick={handleSearch}
  className="btn btn-primary"
>
  Search
</button>

// Category filters
<button
  data-testid={`category-filter-${category.toLowerCase()}`}
  className={`filter-btn ${selectedCategory === category ? 'active' : ''}`}
  onClick={() => setSelectedCategory(category)}
>
  {category}
</button>

// Mode tabs
<button
  data-testid="mode-personalized-btn"
  className={`mode-tab ${discoveryMode === 'personalized' ? 'active' : ''}`}
>
  AI Personalized
</button>

<button
  data-testid="mode-swipe-btn"
  className={`mode-tab ${discoveryMode === 'swipe' ? 'active' : ''}`}
>
  Swipe Mode
</button>

<button
  data-testid="mode-surprise-btn"
  className={`mode-tab ${discoveryMode === 'surprise' ? 'active' : ''}`}
>
  Surprise Me
</button>

<button
  data-testid="mode-browse-btn"
  className={`mode-tab ${discoveryMode === 'browse' ? 'active' : ''}`}
>
  Browse All
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
  {events.map(event => (
    <EventCard key={event.id} event={event} data-testid={`event-${event.id}`} />
  ))}
</div>

// Loading state
<div data-testid="events-loading" className="loading-container">
  <div className="spinner" />
  <p>Loading events...</p>
</div>

// Empty state
<div data-testid="events-empty" className="empty-state">
  <p>No events found</p>
</div>

// Web search toggle
<input
  data-testid="web-search-toggle"
  type="checkbox"
  checked={webSearchEnabled}
  onChange={(e) => setWebSearchEnabled(e.target.checked)}
/>
```

### EventCard.jsx
```jsx
// Card container
<div
  data-testid="event-card"
  data-event-id={event.id}
  className="card event-card"
  onClick={onClick}
>
  // Title
  <h3
    data-testid="event-title"
    className="event-card-title"
  >
    {event.title}
  </h3>

  // Description
  <p data-testid="event-description">{event.description}</p>

  // Date
  <span data-testid="event-date">{event.date}</span>

  // Location
  <span data-testid="event-location">{event.location}</span>

  // Category badge
  <span data-testid="event-category" className="event-card-badge">
    {event.category}
  </span>
</div>
```

### Dashboard.jsx
```jsx
// Stats cards
<div data-testid="stats-events-attended" className="card card-stats">
  <div>{userStats.eventsAttended}</div>
  <div>Events Attended</div>
</div>

<div data-testid="stats-events-liked" className="card card-stats">
  <div>{userStats.eventsLiked}</div>
  <div>Events Liked</div>
</div>

<div data-testid="stats-achievements" className="card card-stats">
  <div>{userStats.achievementsUnlocked}</div>
  <div>Achievements</div>
</div>

// Taste profile
<div data-testid="taste-profile" className="card">
  <h2>Your Taste Profile</h2>
  {/* Profile content */}
</div>

// Personalized events
<div data-testid="personalized-events" className="card">
  <h2>Recommended For You</h2>
  {/* Events */}
</div>
```

### SurpriseMe.jsx
```jsx
// Container
<div data-testid="surprise-me-container" className="card">

// Mood selector
<select data-testid="surprise-me-mood" ...>
  <option value="energetic">Energetic</option>
  <option value="relaxed">Relaxed</option>
  <option value="adventurous">Adventurous</option>
</select>

// Generate button
<button
  data-testid="surprise-me-generate-btn"
  onClick={handleGenerate}
>
  Find My Event!
</button>

// Result
<div data-testid="surprise-me-result">
  {/* Event card */}
</div>
```

---

## 📋 Test Selector Updates

### 01-auth.spec.js Updates

```javascript
// OLD: Generic selectors
const loginButton = page.getByRole('button', { name: /log in/i });
const getStartedButton = page.getByRole('button', { name: /get started/i });
await page.waitForSelector('.auth-form');
const registerTab = page.getByRole('button', { name: 'Register' });
await page.fill('input[type="email"]', testEmail);
await page.fill('input[type="password"]', testPassword);

// NEW: Test ID selectors
const loginButton = page.getByTestId('login-btn');
const getStartedButton = page.getByTestId('get-started-btn');
await page.getByTestId('auth-form').waitFor();
const registerTab = page.getByTestId('auth-tab-register');
await page.getByTestId('auth-email-input').fill(testEmail);
await page.getByTestId('auth-password-input').fill(testPassword);
await page.getByTestId('auth-confirm-password-input').fill(testPassword);
await page.getByTestId('register-submit-btn').click();

// Logout
const logoutButton = page.getByTestId('logout-button');
await expect(logoutButton).toBeVisible();
```

### 02-event-search.spec.js Updates

```javascript
// OLD: Generic selectors
const searchInput = page.locator('input[placeholder*="search" i]').first();
const cityInput = page.locator('input[placeholder*="city" i]').first();
const searchButton = page.getByRole('button', { name: /search|find/i }).first();
const categoryButton = page.locator('button:has-text("Animal")').first();
const webSearchToggle = page.locator('input[type="checkbox"]').first();

// NEW: Test ID selectors
const locationInput = page.getByTestId('location-search-input');
const searchButton = page.getByTestId('search-events-btn');
const categoryButton = page.getByTestId('category-filter-animal');
const webSearchToggle = page.getByTestId('web-search-toggle');
const eventsList = page.getByTestId('events-list');
const firstEvent = page.getByTestId('event-card').first();
```

### 03-surprise-me.spec.js Updates

```javascript
// OLD: Generic selectors
const surpriseMeBtn = page.getByRole('button', { name: /surprise me/i });
const moodSelect = page.locator('select').first();

// NEW: Test ID selectors
const surpriseMeBtn = page.getByTestId('surprise-me-btn');
const surpriseMeContainer = page.getByTestId('surprise-me-container');
const moodSelect = page.getByTestId('surprise-me-mood');
const generateBtn = page.getByTestId('surprise-me-generate-btn');
const result = page.getByTestId('surprise-me-result');
```

### 04-personalized-discovery.spec.js Updates

```javascript
// OLD: Generic selectors
const personalizedTab = page.locator('button:has-text("Personalized")').first();
const eventCards = page.locator('[data-testid="event-card"], .event-card');

// NEW: Test ID selectors
const personalizedModeBtn = page.getByTestId('mode-personalized-btn');
const eventsList = page.getByTestId('events-list');
const eventCards = page.getByTestId('event-card');
const emptyState = page.getByTestId('events-empty');
const loadingState = page.getByTestId('events-loading');
```

### 06-event-interactions.spec.js Updates

```javascript
// OLD: Generic selectors
const likeButton = page.locator('button:has-text("Like")').first();
const attendButton = page.locator('button:has-text("Attend")').first();
const shareButton = page.locator('button:has-text("Share")').first();

// NEW: Test ID selectors
const firstEvent = page.getByTestId('event-card').first();
await firstEvent.getByTestId('like-event-btn').click();
await firstEvent.getByTestId('attend-event-btn').click();
await firstEvent.getByTestId('share-event-btn').click();
```

---

## ⚡ Quick Implementation Script

```bash
#!/bin/bash
# File: add-test-ids.sh

echo "Adding test IDs to components..."

# AuthForm.jsx
echo "Updating AuthForm.jsx..."
cd src/front/src/components
# Manually edit and add test IDs from reference above

# DashboardLanding.jsx
echo "Updating DashboardLanding.jsx..."
cd ../pages
# Manually edit and add test IDs

# EventDiscovery.jsx
echo "Updating EventDiscovery.jsx..."
# Manually edit and add test IDs

# EventCard.jsx
echo "Updating EventCard.jsx..."
cd ../components
# Manually edit and add test IDs

echo "Done! Now update test files with new selectors."
```

---

## ✅ Verification Commands

```bash
# Check if test IDs were added
cd src/front
grep -r "data-testid=" src/components src/pages | wc -l
# Should show 30+ matches

# Run single test to verify
npx playwright test 01-auth --project=chromium --headed

# Check test uses new selectors
grep "getByTestId" tests/e2e/01-auth.spec.js | wc -l
# Should show 10+ matches
```

---

## 📊 Priority Order

1. **AuthForm.jsx** - Most critical (auth tests fail without this)
2. **DashboardLanding.jsx** - Second most critical (entry point)
3. **EventDiscovery.jsx** - High impact (search + discovery tests)
4. **EventCard.jsx** - Medium impact (event interaction tests)
5. **Dashboard.jsx** - Lower impact (stats tests)
6. **SurpriseMe.jsx** - Optional (nice to have)

---

**Start with AuthForm.jsx and update 01-auth.spec.js selectors first! 🚀**
