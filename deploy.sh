#!/bin/bash

# Stop and remove existing containers defined in compose.prod.yaml
docker-compose -f compose.prod.yaml down

# Start the services
DOMAIN_NAME='pixelghost.aniketdas.com' docker-compose -f compose.prod.yaml up -d --build
