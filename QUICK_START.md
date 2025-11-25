# Tapin Correct - Quick Start Guide

## 🚀 Start the Application

```bash
./start-app.sh
```

This starts both:

- **Backend** (Flask + configured LLM provider): http://localhost:5000
- **Frontend** (React + Vite): http://localhost:3000

Press `Ctrl+C` to stop both servers.

## 🛑 Stop the Application

```bash
./stop-app.sh
```

Forcefully stops all running servers.

## 🧪 Run Tests

```bash
./test-app.sh
```

Runs the complete test suite (LLM provider-dependent) (32 tests).

## 📝 Manual Commands

### Backend Only

```bash
cd src/backend

PYTHONPATH=$(pwd) \
# LLM_PROVIDER is configurable; set in your environment if needed
pipenv run python app.py
```

### Frontend Only

```bash
cd src/front
npm install  # First time only
npm run dev
```

## 🔧 Key API Endpoints

### Public

- `GET /api/health` - Health check
- `GET /api/categories` - Event categories
- `POST /api/register` - Register user
- `POST /api/login` - Login

### Authenticated (requires JWT token)

- `GET /api/me` - Current user info
- `POST /api/discover-events` - AI-powered event discovery
- `POST /api/discover-tonight` - Tonight's events
- `POST /api/events/{id}/interact` - Track event interactions
- `GET /api/surprise-me` - AI surprise recommendations

## 🎯 Testing the AI Features

### 1. Register/Login

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### 2. Discover Events (with AI)

```bash
curl -X POST http://localhost:5000/api/discover-events \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_lat": 42.3601,
    "location_lng": -71.0589,
    "categories": ["music", "food"]
  }'
```

### 3. Get Tonight's Events

```bash
curl -X POST http://localhost:5000/api/discover-tonight \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_lat": 42.3601,
    "location_lng": -71.0589,
    "limit": 10
  }'
```

## 📊 Test Results

All tests passing (LLM provider-dependent):

- ✅ API Tests (3/3)
- ✅ Auth Tests (2/2)
- ✅ Listings Tests (3/3)
- ✅ Event Discovery Tests (24/24)
- **Total: 32/32 (100%)**

## 🤖 AI Features

The application uses a configured LLM provider for:

- Event discovery and recommendations
- Personalized event suggestions
- Surprise event generation
- Smart event categorization
- User interaction tracking
- Achievement/gamification system

## 🔍 Troubleshooting

### Backend won't start

```bash
cd src/backend
pipenv install  # Reinstall dependencies
```

### Frontend won't start

```bash
cd src/front
rm -rf node_modules package-lock.json
npm install
```

### Check if ports are in use

```bash
lsof -i :5000  # Backend
lsof -i :3000  # Frontend
```

### View logs

```bash
tail -f src/backend/backend.log
tail -f src/front/frontend.log
```

## 📁 Project Structure

```
Tapin_Correct/
├── start-app.sh          # Start both servers
├── stop-app.sh           # Stop all servers
├── test-app.sh           # Run test suite
├── QUICK_START.md        # This file
└── src/
    ├── backend/          # Flask API + LLM-powered features
    │   ├── app.py
    │   ├── tests/
    │   └── event_discovery/
    └── front/            # React + Vite
        ├── src/
        └── package.json
```

## 🎉 You're Ready!

Run `./start-app.sh` and visit http://localhost:3000 to see the application in action!
