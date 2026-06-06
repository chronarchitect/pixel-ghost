#!/bin/bash

# Generate a random API key
export API_KEY=$(openssl rand -hex 32)
echo "Generated API Key: $API_KEY"

# Write config.js for the frontend
echo "window.API_KEY = '$API_KEY';" > ./config.js

# Start the services with the generated key
DOMAIN_NAME='yourdomain.com' API_KEY=$API_KEY docker-compose -f compose.prod.yaml up -d --build
