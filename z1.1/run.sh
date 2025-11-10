#!/bin/bash
set -e

cd server
docker build -t z33_server_image .
docker run -d --rm --name z33_server --network z33_network z33_server_image
cd ..

sleep 5

cd client
docker build -t z33_client_image .
docker run -it --rm --name z33_client --network z33_network z33_client_image z33_server_image 8000
cd ..

docker stop z33_server

