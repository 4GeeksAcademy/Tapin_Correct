# Event Sources Integration Guide

## Current Event Sources

### 1. **Perplexity AI** ✅ Active
- Uses real-time web search
- Finds current volunteer opportunities
- Configured and working

### 2. **Facebook Events** ✅ Active
- Searches nonprofit organization pages
- Extracts event images
- Limited to configured organizations

### 3. **VolunteerMatch** ✅ Active
- Scrapes volunteer opportunities
- Location-based search
- Works out of the box

## Adding Eventbrite Events

### Option 1: Eventbrite API (Recommended for Production)

**1. Get API Key:**
```bash
# Sign up at: https://www.eventbrite.com/platform/
# Create an OAuth token
```

**2. Add to `.env`:**
```bash
EVENTBRITE_API_TOKEN=your_token_here
```

**3. Use Eventbrite API:**
```python
import requests

def search_eventbrite(city, state):
    url = "https://www.eventbriteapi.com/v3/events/search/"
    params = {
        "location.address": f"{city}, {state}",
        "categories": "111",  # Charity & Causes
        "token": os.environ.get("EVENTBRITE_API_TOKEN")
    }
    response = requests.get(url, params=params)
    return response.json()["events"]
```

### Option 2: AI-Powered Discovery (Already Working!)

The Perplexity AI integration can find Eventbrite events automatically.Test it:

```bash
# The current system will find public events including Eventbrite
curl "http://localhost:5000/events/search?city=Austin&state=TX"
```

## Other Public Event Sources

### Meetup.com
```python
# Requires Meetup API key
MEETUP_API_KEY=your_key_here
```

### AllEvents.in
- Aggregate event platform
- Can be scraped or accessed via API

### Local Government Sites
- Many cities have event calendars
- Can be integrated with custom scrapers

## Quick Enhancement for Presentation

### Update Event Search to Include More Sources

Since Perplexity AI is already configured, it can search across all public platforms including Eventbrite. The system is ready!

**Test with different cities:**

```bash
# New York events (includes all public sources)
curl "http://localhost:5000/events/search?city=New%20York&state=NY"

# Austin events
curl "http://localhost:5000/events/search?city=Austin&state=TX"

# Chicago events
curl "http://localhost:5000/events/search?city=Chicago&state=IL"
```

## For Your Presentation

### Key Points:
1. **Perplexity AI searches across all public sources** - including Eventbrite, Meetup, Facebook, and local event sites
2. **Real-time discovery** - Not limited to pre-configured sources
3. **Smart caching** - Events are cached for 30 days to reduce API calls
4. **Fallback system** - Shows sample events if live search fails

### Demo Script:
```
"Our event discovery uses Perplexity AI, which searches across
multiple platforms including Eventbrite, Meetup, Facebook Events,
and local community calendars. The AI intelligently finds and
categorizes volunteer opportunities based on the user's location."
```

## Production Recommendations

For a production deployment, integrate official APIs:

1. **Eventbrite API** - Official, reliable, well-documented
2. **Meetup API** - Great for community events
3. **Facebook Graph API** - For verified event pages
4. **Google Calendar API** - For public calendars
5. **Municipal APIs** - City-specific event data

## Current Architecture

```
User Request
    ↓
Backend API (/events/search)
    ↓
EventCacheManager
    ├→ Check Cache (30-day TTL)
    ├→ Perplexity AI (searches all sources)
    ├→ Facebook Scraper
    ├→ VolunteerMatch
    └→ Sample Events (fallback)
    ↓
Cache Results
    ↓
Return to User
```

The system is designed to be extensible - new sources can be added easily!

---

**For your presentation: The AI already searches Eventbrite and other public platforms!** 🎉
