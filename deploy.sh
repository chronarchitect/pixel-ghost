#!/bin/bash

# Configuration
APP_PORT=${1:-8080}

echo "🚀 Deploying Pixel Ghost on port $APP_PORT..."

# Stop and remove existing containers defined in compose.prod.yaml
# Use 'docker compose' (V2) with a fallback to 'docker-compose' (V1)
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD -f compose.prod.yaml down

# Start the services
APP_PORT=$APP_PORT $COMPOSE_CMD -f compose.prod.yaml up -d --build

echo "✅ Deployment complete. Accessible at http://localhost:$APP_PORT"
echo "🔗 You can now configure your host Caddy to reverse_proxy to this port."
