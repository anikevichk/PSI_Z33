set -e

MODE=${1:-client}
MAX_CLIENTS=${2:-5}

echo "[i] Mode: $MODE"
echo "[i] Max clients: $MAX_CLIENTS"

cd "$(dirname "$0")"

docker rm -f z33_server z33_client z33_multi_test >/dev/null 2>&1 || true
docker network create z33_network >/dev/null 2>&1 || true

echo "[i] Building server image"
docker build -t z33_server_image -f server/Dockerfile .

echo "[i] Building client image"
docker build -t z33_client_image -f client/Dockerfile .

echo "[i] Starting server"
docker run -d \
  --name z33_server \
  --network z33_network \
  z33_server_image \
  python /app/server.py --max-clients "$MAX_CLIENTS"

sleep 2

if [[ "$MODE" == "client" ]]; then
  echo "[i] Starting interactive client"
  docker run -it --rm \
    --name z33_client \
    --network z33_network \
    -e MINITLS_DEBUG=1 \
    z33_client_image \
    python /app/client.py z33_server
fi

if [[ "$MODE" == "multi" ]]; then
  echo "[i] Starting multi-client test"
  docker run --rm \
    --name z33_multi_test \
    --network z33_network \
    -e MINITLS_DEBUG=1 \
    z33_client_image \
    python /app/multi_client_test.py
fi
docker logs -f z33_server
docker stop z33_server >/dev/null 2>&1 || true
docker rm -f z33_server >/dev/null 2>&1 || true
