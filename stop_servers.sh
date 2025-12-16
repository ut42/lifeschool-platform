#!/bin/bash

# Stop LifeSchool servers
# Radhe Radhe! 🙏

echo "🛑 Stopping LifeSchool servers..."

# Stop backend
if [ -f "backend/backend.pid" ]; then
    PID=$(cat backend/backend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Backend stopped (PID: $PID)"
    else
        echo "⚠️  Backend process not running"
    fi
    rm -f backend/backend.pid backend/backend.log
else
    echo "⚠️  Backend PID file not found"
fi

# Stop frontend
if [ -f "frontend/frontend.pid" ]; then
    PID=$(cat frontend/frontend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Frontend stopped (PID: $PID)"
    else
        echo "⚠️  Frontend process not running"
    fi
    rm -f frontend/frontend.pid frontend/frontend.log
else
    echo "⚠️  Frontend PID file not found"
fi

# Also kill any remaining processes on ports 8000 and 3000
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 8000" || true
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 3000" || true

echo ""
echo "✅ All servers stopped"

