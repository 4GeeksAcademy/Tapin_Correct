# Quick Code Fixes for TapIn UI Modernization

## EventDiscovery.jsx - Top 5 Fixes

### 1. Header Gradient (Line ~307)
**Before:** `style={{ background: 'linear-gradient...', color: 'white', padding..., marginBottom... }}`
**After:** `className="gradient-primary"`

### 2. Location Container (Line ~380)
**Before:** `<div style={{ flex: 1 }}>`
**After:** `<div className="location-search-container">`

### 3. Discovery Container (Line ~430)
**Before:** `<div style={{ maxWidth: '1400px', margin: '0 auto', padding: 'var(--space-6)' }}>`
**After:** `<div className="discovery-container">`

### 4. Events Grid (Line ~480)
**Before:** `<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-6)', marginTop: 'var(--space-6)' }}>`
**After:** `<div className="events-grid">`

### 5. Header Flexbox (Line ~320)
**Before:** `<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>`
**After:** `<div className="flex justify-between items-center mb-4">`

---

## Dashboard.jsx - Top 5 Fixes

### 1. Loading Container (Line ~157)
**Before:**
```jsx
<div className="text-center" style={{ minHeight: '60vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-4)' }}>
  <div className="spinner" style={{ width: '50px', height: '50px' }} />
  <p style={{ fontSize: 'var(--fs-xl)', opacity: 0.8 }}>Loading your dashboard...</p>
</div>
```
**After:**
```jsx
<div className="loading-container">
  <div className="spinner spinner-lg" />
  <p className="loading-text">Loading your dashboard...</p>
</div>
```

### 2. Stats Cards (Line ~210, ~220, ~230)
**Before:** `<div className="card text-center">`
**After:** `<div className="card card-stats text-center">`
*Apply to all 3 stat cards*

### 3. Column Layout (Line ~245 & ~305)
**Before:** `<div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>`
**After:** `<div className="flex flex-col gap-6">`
*Apply to both left and right columns*

### 4. Taste Profile Header (Line ~255)
**Before:** `<h2 style={{ fontSize: 'var(--fs-2xl)', fontWeight: 'var(--fw-semibold)', marginBottom: 'var(--space-4)' }}>`
**After:** `<h2 style={{ fontSize: 'var(--fs-2xl)', fontWeight: 'var(--fw-semibold)' }} className="mb-4">`

### 5. Surprise Me Card (Line ~325)
**Before:** `<h2 style={{ fontSize: 'var(--fs-xl)', marginBottom: 'var(--space-3)' }}>`
**After:** `<h2 style={{ fontSize: 'var(--fs-xl)' }} className="mb-3">`

---

## VS Code Find & Replace

Use Cmd/Ctrl + H in VS Code:

### EventDiscovery.jsx
1. Find: `style={{ flex: 1 }}` → Replace: `className="location-search-container"`
2. Find: `style={{ maxWidth: '1400px', margin: '0 auto', padding: 'var(--space-6)' }}` → Replace: `className="discovery-container"`

### Dashboard.jsx
1. Find: `style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}` → Replace: `className="flex flex-col gap-6"`

---

## Component Quick Fixes

### GlassCard.jsx
**Replace entire style prop with:** `className="glass-card"`

### EventCard.jsx
**Add these classes:**
- Container: `className="card event-card"`
- Image: `className="event-card-media"`
- Content: `className="event-card-content"`
- Title: `className="event-card-title"`

### AuthForm.jsx
**Add these classes:**
- Form: `className="auth-form"`
- Tabs container: `className="auth-tabs"`
- Tab button: `className="auth-tab"`
- Input: `className="form-input"`
- Label: `className="form-label"`

---

**Remember:** Add CSS_ADDITIONS.css content to styles.css first!
