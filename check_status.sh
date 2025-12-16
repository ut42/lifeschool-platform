#!/bin/bash

# Check LifeSchool servers status
# Radhe Radhe! 🙏

echo "📊 LifeSchool Platform Status"
echo "================================"
echo ""

# Check backend
echo "🔍 Backend (Port 8000):"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:8000"
    echo "  📚 API Docs - http://localhost:8000/docs"
    curl -s http://localhost:8000/ | python3 -m json.tool 2>/dev/null | head -3 || echo "  Response: OK"
else
    echo "  ❌ Not running"
fi
echo ""

# Check frontend
echo "🔍 Frontend:"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:3000"
elif curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:3001 (port 3000 was in use)"
else
    echo "  ❌ Not running"
fi
echo ""

# Check MongoDB
echo "🔍 MongoDB:"
if mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "  ✅ Running"
else
    echo "  ❌ Not running"
fi
echo ""

echo "================================"
echo "To stop servers: ./stop_servers.sh"
echo "To start servers: ./start_backend.sh and ./start_frontend.sh"

