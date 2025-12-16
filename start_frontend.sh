#!/bin/bash

# LifeSchool Frontend Startup Script
# Radhe Radhe! 🙏

cd "$(dirname "$0")/frontend"

echo "🚀 Starting LifeSchool Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "✅ Starting Vite dev server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
npm run dev

