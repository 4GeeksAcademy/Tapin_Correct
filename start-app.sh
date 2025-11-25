#!/bin/bash
# Tapin Correct - Application Startup Script
# This script starts both the backend (Flask) and frontend (React/Vite)

set -e

echo "🚀 Starting Tapin Correct Application..."
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start Backend
echo "📦 Starting Backend (Flask)..."
cd "$SCRIPT_DIR/src/backend"

PYTHONPATH="$SCRIPT_DIR/src/backend" \
# LLM provider is configurable via environment: set LLM_PROVIDER if needed
pipenv run python app.py > backend.log 2>&1 &

BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID) - http://localhost:5000"
echo "   Logs: src/backend/backend.log"
echo ""

# Wait a moment for backend to initialize
sleep 2

# Check if backend is still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check backend.log for errors."
    cat "$SCRIPT_DIR/src/backend/backend.log"
    exit 1
fi

# Install frontend dependencies if needed
cd "$SCRIPT_DIR/src/front"
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
    echo ""
else
    echo "✓ Frontend dependencies already installed"
    echo ""
fi

# Start Frontend
echo "⚛️  Starting Frontend (React + Vite)..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID) - http://localhost:3000"
echo "   Logs: src/front/frontend.log"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Tapin Correct is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Frontend:    http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "🤖 LLM:         configured provider (check LLM_PROVIDER env variable)"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
