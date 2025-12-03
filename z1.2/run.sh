#!/bin/bash
set -e

echo "Building images..."
docker-compose build

echo "Starting containers..."
docker-compose up -d 

docker-compose ps