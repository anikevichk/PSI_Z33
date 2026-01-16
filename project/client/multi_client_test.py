import subprocess
import time
import socket
import sys

HOST = "z33_server"
PORT = 4444

def wait_for_server(host, port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False

if not wait_for_server(HOST, PORT):
    print("Server not ready")
    sys.exit(1)

clients = []

for i in range(5):
    p = subprocess.Popen(
        ["python", "client.py", HOST],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    clients.append(p)
    time.sleep(0.2)

for i, p in enumerate(clients):
    try:
        p.stdin.write(f"test from client {i}\n")
        p.stdin.flush()
    except BrokenPipeError:
        print(f"Client {i} already exited")
