#!/bin/bash

# FastAPI Metrics Monitoring System with Supabase - Quick Start Script
# This script sets up and starts the complete monitoring stack with database integration

set -e

echo "🚀 FastAPI Metrics Monitoring System with Supabase - Quick Start"
echo "================================================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if ports are available
echo "🔍 Checking port availability..."

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $1 is already in use. Please free up the port or stop the conflicting service."
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

check_port 8000 || exit 1
check_port 9090 || exit 1
check_port 3000 || exit 1

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cp .env.example .env
    echo "✅ Environment file created (.env)"
else
    echo "✅ Environment file already exists"
fi

# Display Supabase information
echo ""
echo "🗄️ Database Configuration:"
echo "  • Using Supabase for persistent data storage"
echo "  • Pre-configured demo database included"
echo "  • For your own database, see SUPABASE_SETUP.md"
echo ""

# Start the services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🏥 Checking service health..."

check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $name is healthy"
            return 0
        fi
        echo "⏳ Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $name failed to start properly"
    return 1
}

check_service "http://localhost:8000/health" "FastAPI Application"
check_service "http://localhost:8000/health/database" "Database Connection"
check_service "http://localhost:9090/-/healthy" "Prometheus"
check_service "http://localhost:3000/api/health" "Grafana"

# Display access information
echo ""
echo "🎉 All services are running successfully!"
echo "========================================"
echo ""
echo "📱 Access URLs:"
echo "  • FastAPI Application:    http://localhost:8000"
echo "  • API Documentation:      http://localhost:8000/docs"
echo "  • Prometheus:             http://localhost:9090"
echo "  • Grafana Dashboard:      http://localhost:3000"
echo ""
echo "🔐 Default Credentials:"
echo "  • Grafana: admin / admin123"
echo ""
echo "🗄️ Database Information:"
echo "  • Database: Supabase (PostgreSQL)"
echo "  • Pre-configured with demo data"
echo "  • Health check: http://localhost:8000/health/database"
echo ""
echo "📊 Quick Test Commands:"
echo "  # Check application health"
echo "  curl http://localhost:8000/health"
echo ""
echo "  # Check database connectivity"
echo "  curl http://localhost:8000/health/database"
echo ""
echo "  # Create sample data"
echo "  curl -X POST http://localhost:8000/api/v1/data \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"name\":\"Test Item\",\"value\":42.5,\"category\":\"demo\"}'"
echo ""
echo "  # View all data"
echo "  curl http://localhost:8000/api/v1/data"
echo ""
echo "  # View statistics"
echo "  curl http://localhost:8000/api/v1/stats"
echo ""
echo "  # View metrics"
echo "  curl http://localhost:8000/metrics"
echo ""
echo "📚 Documentation:"
echo "  • README.md - Complete setup and usage guide"
echo "  • API_DOCUMENTATION.md - Detailed API reference"
echo "  • DEPLOYMENT_GUIDE.md - Production deployment guide"
echo "  • SUPABASE_SETUP.md - Database setup instructions"
echo ""
echo "🛑 To stop all services:"
echo "  docker-compose down"
echo ""
echo "Happy monitoring with Supabase! 🎯"