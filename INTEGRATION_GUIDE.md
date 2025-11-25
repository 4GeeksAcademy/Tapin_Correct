# 🚀 Google Custom Search Integration Guide

## Overview
This guide explains how to integrate the new Google Custom Search feature into your Tapin app with a professional, unified design.

## ✅ What's Been Implemented

### Backend (✅ Complete)
- **API Endpoint:** `POST /api/web-search`
- **Features:**
  - Google Custom Search API integration
  - Automatic categorization (14 categories)
  - Contact info extraction (email, phone)
  - Saves organizations to database as Events
  - Requires JWT authentication

### Frontend Components Created

#### 1. **EnhancedEventSearch.jsx** (Recommended)
**Location:** `src/front/src/components/EnhancedEventSearch.jsx`

**Features:**
- ✅ Login protection - only shows to authenticated users
- ✅ Three search modes: Database Only, Web Only, or Both
- ✅ Uses your existing EventCard component
- ✅ Maintains your purple gradient design language
- ✅ Shows unified results from both sources
- ✅ Clear source indicators (Database vs Web)

**Usage:**
```jsx
import EnhancedEventSearch from './components/EnhancedEventSearch';

// In your component:
<EnhancedEventSearch
  onEventsLoaded={(events) => {
    // Optional: Handle loaded events
    console.log('Events loaded:', events);
  }}
/>
```

## 🎨 Design Consistency

The new component matches your existing design:
- **Colors:** Purple gradient (#667eea → #764ba2)
- **Cards:** Same style as your EventCard component
- **Spacing:** Consistent with your app
- **Shadows:** Matches existing shadow system
- **Typography:** Same font weights and sizes

## 📋 Integration Options

### Option 1: Replace Existing EventSearch (Recommended)
Replace your current `EventSearch` component with `EnhancedEventSearch`:

```jsx
// In your pages or components
- import EventSearch from './components/EventSearch';
+ import EnhancedEventSearch from './components/EnhancedEventSearch';

// Use it:
- <EventSearch onEventsLoaded={handleEvents} />
+ <EnhancedEventSearch onEventsLoaded={handleEvents} />
```

### Option 2: Add as New Tab
Add web search as a new option in your existing interface:

```jsx
const [searchType, setSearchType] = useState('database');

{searchType === 'database' && <EventSearch />}
{searchType === 'web' && <EnhancedEventSearch />}
```

### Option 3: Side-by-Side
Show both search options on the same page:

```jsx
<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
  <EventSearch />
  <EnhancedEventSearch />
</div>
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Already configured:
GOOGLE_API_KEY=your_key_here
CUSTOM_SEARCH_ENGINE_ID=your_cx_here
LLM_PROVIDER=google

# Optional:
GOOGLE_MAX_REQUESTS_PER_MONTH=100  # Default: 100
```

### Updating Category Filters
To add new web search categories to your Filters component:

```jsx
// src/front/src/components/Filters.jsx
const chips = [
  'All',
  'Community',
  'Environment',
  'Education',
  'Health',
  'Animals',
  // Add new categories:
  'Arts & Culture',
  'Children & Youth',
  'Disaster Relief',
  'Human Rights',
  'Seniors',
  'Technology',
  "Women's Issues"
];
```

## 🗺️ Map Integration (Future Enhancement)

To show web-sourced events on your map:

```jsx
// The events already have location data:
// event.location_city
// event.location_state
// event.latitude (if available)
// event.longitude (if available)

// In your MapView component, filter events:
const webEvents = events.filter(e => e.source === 'google_custom_search');
const dbEvents = events.filter(e => e.source !== 'google_custom_search');

// Show different markers for each type
```

## 📊 Data Flow

```
User Search
    ↓
EnhancedEventSearch Component
    ↓
    ├─→ Database Search (/api/events/search)
    │   └─→ Returns curated events
    │
    └─→ Web Search (/api/web-search)
        ├─→ Google Custom Search API
        ├─→ Categorizes results
        ├─→ Extracts contact info
        ├─→ Saves to database as Events
        └─→ Returns enriched events
    ↓
Unified Event List
    ↓
EventCard Components
    ↓
Shows "Volunteer" button with contact info
```

## 🎯 User Experience Flow

1. **User logs in** (required)
2. **Selects search mode:**
   - 💾 Our Database (curated events)
   - 🌐 Web Search (search entire web)
   - 🚀 Both (maximum results)
3. **Enters location** (city autocomplete)
4. **Optionally adds keywords** (for web search)
5. **Clicks Search**
6. **Views unified results:**
   - Database events marked with 💾
   - Web events marked with 🌐
   - Contact info visible via "Volunteer" button
7. **Clicks event card** to view details/website

## 🔒 Security

- ✅ JWT authentication required for all searches
- ✅ API key stored securely in .env (not committed)
- ✅ Rate limiting via `GOOGLE_MAX_REQUESTS_PER_MONTH`
- ✅ Input validation on backend
- ✅ CORS properly configured

## 🧪 Testing

### Test the API directly:
```bash
# Run the integration test:
pipenv run python test_integration.py
```

### Test the component:
1. Start your React dev server: `npm run dev`
2. Log in to the app
3. Navigate to the event search
4. Try all three search modes
5. Verify results display correctly
6. Check contact info shows in volunteer button

## 📈 Monitoring

Check Google API usage:
```bash
# Usage is tracked in:
src/backend/.usage/google_usage.json

# Contains:
{
  "month": "2025-11",
  "count": 42  # Number of requests this month
}
```

## 🐛 Troubleshooting

### "API key not valid"
- Verify `GOOGLE_API_KEY` in `.env`
- Ensure Custom Search API is enabled in Google Cloud Console
- Check API key has no restrictions or Custom Search is in allowed list

### "Quota reached"
- Increase `GOOGLE_MAX_REQUESTS_PER_MONTH` in `.env`
- Check `.usage/google_usage.json` for current count
- Resets automatically each month

### "No events found"
- Verify location is in "City, State" format
- Try broader search keywords
- Check if events exist in that area

### Contact info not showing
- Only 3 events per search have contact info extracted (configurable)
- Some websites don't have extractable contact info
- Users can still visit the website directly

## 🚀 Next Steps

1. **Test the EnhancedEventSearch component** in your app
2. **Decide on integration approach** (replace, tab, or side-by-side)
3. **Update your Filters** if you want all categories
4. **Consider map integration** for web-sourced events
5. **Monitor API usage** to stay within quota

## 📞 Support

For issues or questions:
- Check the backend logs: `app.log`
- Test API directly with `test_integration.py`
- Verify Google Cloud Console settings

---

**Summary:** The system is ready to use! The backend API is working, the component matches your design, and everything is protected behind login. Choose your integration approach and you're good to go! 🎉
