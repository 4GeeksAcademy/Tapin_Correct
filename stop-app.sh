#!/bin/bash
# Stop all Tapin Correct processes

echo "🛑 Stopping Tapin Correct..."

# Kill Flask/Python processes on port 5000
FLASK_PID=$(lsof -ti:5000)
if [ ! -z "$FLASK_PID" ]; then
    echo "   Stopping backend (port 5000)..."
    kill $FLASK_PID 2>/dev/null
    echo "   ✅ Backend stopped"
else
    echo "   ℹ️  Backend not running"
fi

# Kill Vite/Node processes on port 3000
VITE_PID=$(lsof -ti:3000)
if [ ! -z "$VITE_PID" ]; then
    echo "   Stopping frontend (port 3000)..."
    kill $VITE_PID 2>/dev/null
    echo "   ✅ Frontend stopped"
else
    echo "   ℹ️  Frontend not running"
fi

echo ""
echo "✅ All servers stopped"
