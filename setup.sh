#!/bin/bash

# Traditional Swedish Fika Register - Setup Script
# This script helps you get the application up and running quickly

set -e

echo "🇸🇪 Traditional Swedish Fika Register - Setup"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the app"
    echo "   Required: SUPABASE_URL, SUPABASE_ANON_KEY, OPENROUTER_API_KEY"
    echo ""
fi

# Function to check if a service is running
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            echo "✅ $service is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - $service not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service failed to start within expected time"
    return 1
}

# Start the application
echo "🚀 Starting Traditional Swedish Fika Register..."
echo ""

# Build and start services
docker-compose up -d --build

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "⏳ Waiting for services to initialize..."

# Wait for backend to be ready
if wait_for_service "Backend API" 8000; then
    echo ""
    echo "🎉 Application is ready!"
    echo ""
    echo "📍 Access Points:"
    echo "   Frontend:     http://localhost:3000"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo "   AI Dashboard: http://localhost:8000/ai/dashboard"
    echo ""
    echo "🗄️  Database:"
    echo "   PostgreSQL:   localhost:5432"
    echo "   Redis:        localhost:6379"
    echo ""
    echo "🇸🇪 Explore Swedish Fika Culture!"
    echo "   The application includes sample data for:"
    echo "   - Stockholm: Historic konditoris and modern cafés"
    echo "   - Gothenburg: Famous for giant cinnamon buns"
    echo "   - Malmö: International fika influences"
    echo "   - Uppsala: University town charm"
    echo "   - Västerås: Industrial heritage fika spots"
    echo ""
else
    echo "❌ Failed to start the application"
    echo "📝 Check logs with: docker-compose logs"
    exit 1
fi

# Optional: Run database migrations
echo "🗄️  Setting up database..."
if docker-compose exec -T backend python -c "from app.database import create_tables; create_tables()" 2>/dev/null; then
    echo "✅ Database tables created successfully"
else
    echo "ℹ️  Database might already be initialized"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Visit http://localhost:3000 to explore fika locations"
echo "2. Try the search functionality with Swedish terms like 'kanelbullar'"
echo "3. Browse locations by city (Stockholm, Gothenburg, etc.)"
echo "4. Check the AI dashboard at http://localhost:8000/ai/dashboard"
echo "5. View API documentation at http://localhost:8000/docs"
echo ""
echo "📚 For development:"
echo "   - Edit backend files in ./backend/ (auto-reloads)"
echo "   - Edit frontend files in ./frontend/ (serve statically)"
echo "   - View logs: docker-compose logs -f [service_name]"
echo "   - Stop app: docker-compose down"
echo ""
echo "🤖 This Traditional Swedish Fika Register was built with Claude Code!"
echo "Happy fika exploring! ☕🥐"