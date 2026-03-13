#!/bin/bash

# Net 仔 Podcast System - Startup Script
# 快速啟動所有服務

set -e

echo "🚀 Starting Net 仔 Podcast System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Create .env file if not exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your API keys before starting"
    echo "   Required: AZURE_SPEECH_KEY, OPENAI_API_KEY"
    exit 0
fi

# Start all services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Show access information
echo ""
echo "✅ All services started successfully!"
echo ""
echo "📡 Access points:"
echo "   - Frontend:        http://localhost:3001 (already running)"
echo "   - Backend API:     http://localhost:8000"
echo "   - API Docs:        http://localhost:8000/docs"
echo "   - MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
echo "   - Flower Monitor:  http://localhost:5555"
echo "   - Grafana:         http://localhost:3000 (admin/admin)"
echo ""
echo "🎙️  Ready to generate Cantonese podcasts!"
echo ""
