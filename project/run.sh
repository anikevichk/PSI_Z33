#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

docker network create z33_network >/dev/null 2>&1 || true
docker rm -f z33_server z33_client >/dev/null 2>&1 || true

docker build -f server/Dockerfile -t z33_server_image .
docker build -f client/Dockerfile -t z33_client_image .

# flag MINITLS_DEBUG used to see extra info
docker run -d --name z33_server --network z33_network -e MINITLS_DEBUG=1 z33_server_image
sleep 1

docker run -it --rm --name z33_client --network z33_network -e MINITLS_DEBUG=1 z33_client_image z33_server

docker stop z33_server >/dev/null 2>&1 || true
docker rm -f z33_server >/dev/null 2>&1 || true
