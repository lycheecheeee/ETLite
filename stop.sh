#!/bin/bash

# Net 仔 Podcast System - Stop Script

echo "👋 Stopping Net 仔 Podcast System..."

docker-compose down

echo "✅ All services stopped"
echo "💾 Data is preserved in volumes"
echo ""
echo "To restart: ./start.sh"
echo "To remove all data: docker-compose down -v"
