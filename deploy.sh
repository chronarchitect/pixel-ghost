#!/bin/bash

# Start the services
DOMAIN_NAME='yourdomain.com' docker-compose -f compose.prod.yaml up -d --build
