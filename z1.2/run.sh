#!/bin/bash
set -e

echo "Building images..."
docker-compose build

echo "Starting containers..."
docker-compose up -d

docker-compose ps

CLIENT="udp_client"
SERVER="udp_server"

docker wait "$CLIENT" >/dev/null 2>&1 || true

CLIENT_HASH=$(docker logs "$CLIENT" 2>/dev/null | grep -oE 'Client SHA-256: [0-9a-f]{64}' | tail -n 1 | awk '{print $3}')
SERVER_HASH=$(docker logs "$SERVER" 2>/dev/null | grep -oE 'Server SHA-256: [0-9a-f]{64}' | tail -n 1 | awk '{print $3}')

echo
echo "HASH: client=$CLIENT_HASH  server=$SERVER_HASH"
if [ -n "$CLIENT_HASH" ] && [ "$CLIENT_HASH" = "$SERVER_HASH" ]; then
  echo "RESULT: MATCH"
else
  echo "RESULT: NO MATCH"
fi
