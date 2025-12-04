import os, sys, time, socket, struct, hashlib

FILE_NAME = "input.bin"
FILE_SIZE = 10000
CHUNK_SIZE = 100

ACK_TIMEOUT = 0.2
FIN_WAIT = 8.0


def make_random_file(path: str, size: int) -> None:
    with open(path, "wb") as f:
        f.write(os.urandom(size))


def sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def recv_exact(sock: socket.socket, maxlen: int = 2048) -> bytes | None:
    try:
        return sock.recv(maxlen)
    except socket.timeout:
        return None


def wait_control_ack(sock: socket.socket) -> bool:
    msg = recv_exact(sock, 16)
    return msg is not None and len(msg) >= 2 and msg[0] == 0 and msg[1] == 1


def wait_data_ack(sock: socket.socket, seq: int) -> bool:
    msg = recv_exact(sock, 64)
    if msg is None or len(msg) < 5:
        return False
    if msg[0] != 2:
        return False
    (ack_seq,) = struct.unpack("!I", msg[1:5])
    return ack_seq == seq


def main():
    if len(sys.argv) < 2:
        print(f"Użycie: {sys.argv[0]} <server_host> [port]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 8888

    make_random_file(FILE_NAME, FILE_SIZE)

    with open(FILE_NAME, "rb") as f:
        data = f.read()

    client_hash = sha256_hex(data)
    total_packets = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE

    print(f"Client SHA-256: {client_hash}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(ACK_TIMEOUT)
    sock.connect((host, port))

    control_pkt = struct.pack("!BII", 0, total_packets, len(data))

    while True:
        sock.send(control_pkt)
        if wait_control_ack(sock):
            break

    for seq in range(total_packets):
        off = seq * CHUNK_SIZE
        payload = data[off:off + CHUNK_SIZE]
        plen = len(payload)
        pkt = struct.pack("!BIH", 1, seq, plen) + payload

        while True:
            sock.send(pkt)
            if wait_data_ack(sock, seq):
                break

    sock.settimeout(0.5)
    end = time.time() + FIN_WAIT
    while time.time() < end:
        msg = recv_exact(sock, 16)
        if msg and len(msg) >= 2 and msg[0] == 3 and msg[1] == 1:
            break

    sock.close()


if __name__ == "__main__":
    main()
