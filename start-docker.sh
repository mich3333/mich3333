#!/bin/bash

echo "🐳 Starting AgentHub with Docker..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - VITE_SUPABASE_URL"
    echo "   - VITE_SUPABASE_ANON_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start
echo "🔨 Building and starting containers..."
docker-compose up --build -d

# Show logs
echo ""
echo "✅ AgentHub is starting!"
echo ""
echo "📊 Frontend: http://localhost:5173"
echo "⚡ Backend:  http://localhost:5000"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "🛑 To stop:     docker-compose down"
echo ""
