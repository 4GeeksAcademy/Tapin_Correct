# Presentation Data Verification Test Plan

## Objective
Verify that the Tapin_Correct platform is populated with volunteer organizations and events from Dallas, Houston, and Miami for presentation purposes.

## Test Scope

### 1. Database Seed Data Verification
**What to check:**
- Examine `src/backend/seed_data.py` to see if it includes listings for Dallas, Houston, and Miami
- Check the database file `src/backend/instance/data.db` to verify actual seeded data
- Count how many volunteer listings exist per city

**Commands to run:**
```bash
# Check if database exists
ls -lh src/backend/instance/data.db

# Use Python to query the database
cd /Users/houseofobi/Documents/GitHub/Tapin_Correct
PYTHONPATH=src/backend python3 -c "
from app import app, db, Listing
with app.app_context():
    # Get all listings
    all_listings = Listing.query.all()
    print(f'Total listings in database: {len(all_listings)}')

    # Check for specific cities
    cities = ['Dallas', 'Houston', 'Miami']
    for city in cities:
        city_listings = Listing.query.filter(Listing.city.ilike(f'%{city}%')).all()
        print(f'\n{city}: {len(city_listings)} listings')
        for listing in city_listings[:3]:  # Show first 3
            print(f'  - {listing.title} ({listing.category})')
"
```

### 2. Backend API Endpoint Tests
**Endpoints to test:**

#### A. Get all listings (should include target cities)
```bash
# Start the backend server first
cd /Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend
LLM_PROVIDER=perplexity PERPLEXITY_API_KEY="$PERPLEXITY_API_KEY" pipenv run python app.py &  # pragma: allowlist secret
SERVER_PID=$!
sleep 5

# Test endpoints
curl -s http://localhost:5000/api/listings | python3 -m json.tool | head -100

# Filter by city (if supported)
curl -s "http://localhost:5000/api/listings?city=Dallas" | python3 -m json.tool
curl -s "http://localhost:5000/api/listings?city=Houston" | python3 -m json.tool
curl -s "http://localhost:5000/api/listings?city=Miami" | python3 -m json.tool

# Kill server when done
kill $SERVER_PID
```

#### B. Test Google Event Search API (External Events)
```bash
# Check if Google API credentials are configured
cat /Users/houseofobi/Documents/GitHub/Tapin_Correct/.env | grep GOOGLE

# Test the search_events function directly
cd /Users/houseofobi/Documents/GitHub/Tapin_Correct
PYTHONPATH=src/backend python3 -c "
from google_search import search_events
import os

# Test searches for each city
cities = ['Dallas', 'Houston', 'Miami']
categories = ['Community Development', 'Education', 'Environment']

for city in cities:
    print(f'\n=== Testing {city} ===')
    for category in categories:
        query = f'volunteer opportunities {category} {city}'
        try:
            results = search_events(query, category)
            print(f'{category}: {len(results)} results found')
            if results:
                print(f'  Example: {results[0].get(\"title\", \"N/A\")}')
        except Exception as e:
            print(f'{category}: ERROR - {str(e)}')
"
```

#### C. Test Event Search API Endpoint
```bash
# Start backend
cd /Users/houseofobi/Documents/GitHub/Tapin_Correct/src/backend
LLM_PROVIDER=perplexity PERPLEXITY_API_KEY="$PERPLEXITY_API_KEY" pipenv run python app.py &  # pragma: allowlist secret
SERVER_PID=$!
sleep 5

# Test event search for each city
curl -s "http://localhost:5000/api/search/events?query=volunteer%20Dallas" | python3 -m json.tool
curl -s "http://localhost:5000/api/search/events?query=volunteer%20Houston&category=Education" | python3 -m json.tool
curl -s "http://localhost:5000/api/search/events?query=volunteer%20Miami&category=Environment" | python3 -m json.tool

kill $SERVER_PID
```

### 3. Frontend Data Display Verification
**What to check:**
- Can the frontend display listings from the database?
- Does the EventSearch component work with the API?
- Are maps showing correct locations for Dallas, Houston, Miami?

```bash
# Start both backend and frontend
cd /Users/houseofobi/Documents/GitHub/Tapin_Correct

# Terminal 1: Backend
cd src/backend
LLM_PROVIDER=perplexity PERPLEXITY_API_KEY="$PERPLEXITY_API_KEY" pipenv run python app.py &  # pragma: allowlist secret
BACKEND_PID=$!

# Terminal 2: Frontend
cd /Users/houseofobi/Documents/GitHub/Tapin_Correct
npm run dev &
FRONTEND_PID=$!

# Wait and check if services are running
sleep 10
curl -s http://localhost:5000/api/listings | head -20
curl -s http://localhost:5173/ | head -20

# Cleanup
kill $BACKEND_PID $FRONTEND_PID
```

### 4. Data Population Assessment

**Read and analyze these files:**
1. `src/backend/seed_data.py` - Check the seeding logic
   - Does it include Dallas, Houston, Miami listings?
   - How many listings per city?
   - Are they diverse categories?

2. `src/backend/google_search.py` - Check search implementation
   - Is the API key configured?
   - Is the Custom Search Engine ID set?
   - Does it handle city-specific queries?

3. `src/front/src/components/EventSearch.jsx` - Check frontend integration
   - Does it pass city/location to API?
   - Does it display results properly?

### 5. Presentation Readiness Checklist

Create a report with:
- [ ] Total volunteer listings in database
- [ ] Listings count for Dallas: __
- [ ] Listings count for Houston: __
- [ ] Listings count for Miami: __
- [ ] Google Event Search working: Yes/No
- [ ] Sample event results for Dallas: Yes/No
- [ ] Sample event results for Houston: Yes/No
- [ ] Sample event results for Miami: Yes/No
- [ ] Frontend can display local listings: Yes/No
- [ ] Frontend can search external events: Yes/No
- [ ] Maps showing correct city locations: Yes/No

### 6. If Data is Missing - Quick Fix

If the database is not populated with Dallas, Houston, Miami data:

```python
# Quick seed script for presentation cities
PYTHONPATH=src/backend python3 -c "
from app import app, db, Listing
from datetime import datetime

presentation_listings = [
    # Dallas
    {'title': 'Dallas Food Bank Volunteer', 'description': 'Help sort and distribute food', 'city': 'Dallas', 'state': 'TX', 'category': 'Community Development', 'location': {'type': 'Point', 'coordinates': [-96.7970, 32.7767]}},
    {'title': 'Dallas Animal Shelter Helper', 'description': 'Care for shelter animals', 'city': 'Dallas', 'state': 'TX', 'category': 'Animal Welfare', 'location': {'type': 'Point', 'coordinates': [-96.7970, 32.7767]}},

    # Houston
    {'title': 'Houston Habitat for Humanity', 'description': 'Build homes for families in need', 'city': 'Houston', 'state': 'TX', 'category': 'Community Development', 'location': {'type': 'Point', 'coordinates': [-95.3698, 29.7604]}},
    {'title': 'Houston Youth Tutoring Program', 'description': 'Tutor elementary students', 'city': 'Houston', 'state': 'TX', 'category': 'Education', 'location': {'type': 'Point', 'coordinates': [-95.3698, 29.7604]}},

    # Miami
    {'title': 'Miami Beach Cleanup', 'description': 'Help keep beaches clean', 'city': 'Miami', 'state': 'FL', 'category': 'Environment', 'location': {'type': 'Point', 'coordinates': [-80.1918, 25.7617]}},
    {'title': 'Miami Senior Center Assistant', 'description': 'Assist seniors with activities', 'city': 'Miami', 'state': 'FL', 'category': 'Senior Services', 'location': {'type': 'Point', 'coordinates': [-80.1918, 25.7617]}},
]

with app.app_context():
    for listing_data in presentation_listings:
        # Check if exists
        existing = Listing.query.filter_by(title=listing_data['title']).first()
        if not existing:
            listing = Listing(
                title=listing_data['title'],
                description=listing_data['description'],
                city=listing_data['city'],
                state=listing_data['state'],
                category=listing_data['category'],
                organization='Demo Organization',
                created_at=datetime.utcnow()
            )
            db.session.add(listing)

    db.session.commit()
    print('Presentation data seeded successfully')
"
```

## Expected Output Format

Provide a summary report like:

```
PRESENTATION DATA VERIFICATION REPORT
=====================================

Database Status:
- Total Listings: 45
- Dallas Listings: 12
- Houston Listings: 8
- Miami Listings: 10

API Endpoints:
- GET /api/listings: ✓ Working (returns 45 listings)
- Dallas listings API: ✓ Returns 12 results
- Houston listings API: ✓ Returns 8 results
- Miami listings API: ✓ Returns 10 results

External Event Search:
- Google API Configured: ✓ Yes
- Dallas search: ✓ Returns 10 external events
- Houston search: ✓ Returns 8 external events
- Miami search: ✓ Returns 12 external events

Frontend:
- Backend connection: ✓ Connected
- Listings display: ✓ Working
- EventSearch component: ✓ Working
- Map locations: ✓ Showing correct coordinates

PRESENTATION READINESS: ✓ READY / ✗ NOT READY

Issues Found:
[List any problems discovered]

Recommendations:
[List any suggestions for improvement]
```

## Notes for Agent

1. Run all commands from the project root: `/Users/houseofobi/Documents/GitHub/Tapin_Correct`
2. Use `LLM_PROVIDER=perplexity` with the API key for backend testing (Google Search API is separate and uses GOOGLE_API_KEY from .env)
3. Check for environment variables in `.env` file
4. If backend fails to start, check for port conflicts: `lsof -i :5000`
5. Take screenshots of any errors encountered
6. Document actual vs expected results for each test

## Success Criteria

The presentation is ready if:
- ✓ At least 5 listings per city (Dallas, Houston, Miami)
- ✓ External event search returns results for each city
- ✓ Frontend displays both local listings and external events
- ✓ Maps show accurate locations for all three cities
- ✓ No critical errors in console or logs
