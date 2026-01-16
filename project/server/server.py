import socket
import threading
import argparse
import sys

from common import (
    send_frame,
    recv_frame,
    dh_generate_keypair,
    kdf,
    make_encrypted_record,
    open_encrypted_record,
    P,
)

HOST = "0.0.0.0"
PORT = 4444

clients = {}          
clients_lock = threading.Lock()
client_id_counter = 0


def handle_client(client_id: int, conn: socket.socket, addr):
    print(f"[+] Client {client_id} connected from {addr}")

    encryption_key = None
    mac_key = None
    send_seq = 0
    recv_seq = 0

    try:
        msg = recv_frame(conn)
        if msg.get("type") != "ClientHello":
            raise ValueError("Expected ClientHello")

        client_pub = int(msg["dh_pub"])
        if not (2 <= client_pub <= P - 2):
            raise ValueError("Invalid DH public key")

        server_priv, server_pub = dh_generate_keypair()

        send_frame(conn, {
            "type": "ServerHello",
            "dh_pub": server_pub,
        })

        shared_secret = pow(client_pub, server_priv, P)
        k_enc_in,  k_mac_in  = kdf(shared_secret, b"c2s")  
        k_enc_out, k_mac_out = kdf(shared_secret, b"s2c") 
        
        with open(f"session_keys_client_{client_id}.bin", "wb") as f:
            f.write(b"c2s_enc=" + k_enc_in + b"\n")
            f.write(b"s2c_enc=" + k_enc_out + b"\n")
            f.write(b"c2s_mac=" + k_mac_in + b"\n")
            f.write(b"s2c_mac=" + k_mac_out + b"\n")

        print(f"[i] Handshake completed with client {client_id}")

        while True:
            record = recv_frame(conn)

            inner = open_encrypted_record(
                k_enc_in,
                k_mac_in,
                recv_seq,
                record
            )

            recv_seq += 1

            msg_type = inner.get("type")

            if msg_type == "END_SESSION":
                print(f"[i] Client {client_id} ended session")
                break

            print(f"[MSG][Client {client_id}]: {inner}")

            reply = {
                "type": "DATA",
                "text": inner.get("text", "")
            }

            send_frame(conn, make_encrypted_record(
                k_enc_out,
                k_mac_out,
                send_seq,
                reply
            ))

            send_seq += 1


    except Exception as e:
        print(f"[!] Error with client {client_id}: {e}")

    finally:
        with clients_lock:
            clients.pop(client_id, None)
        conn.close()
        print(f"[-] Client {client_id} disconnected")


def accept_clients(server_socket, max_clients):
    global client_id_counter

    while True:
        conn, addr = server_socket.accept()

        with clients_lock:
            if len(clients) >= max_clients:
                print("[!] Max clients reached, rejecting connection")
                conn.close()
                continue

            client_id_counter += 1
            client_id = client_id_counter
            clients[client_id] = conn

        threading.Thread(
            target=handle_client,
            args=(client_id, conn, addr),
            daemon=True
        ).start()


def server_cli():
    while True:
        try:
            cmd = input("> ").strip()
        except EOFError:
            return

        if cmd == "list":
            with clients_lock:
                if not clients:
                    print("No connected clients")
                for cid in clients:
                    print(f"Client {cid}")

        elif cmd.startswith("close"):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: close <client_id>")
                continue

            try:
                cid = int(parts[1])
            except ValueError:
                print("Client ID must be an integer")
                continue

            with clients_lock:
                conn = clients.get(cid)

            if conn:
                try:
                    conn.close()
                    print(f"[i] Closed connection for client {cid}")
                except Exception as e:
                    print(f"[!] Error closing client {cid}: {e}")
            else:
                print("No such client")

        elif cmd in ("exit", "quit"):
            print("Shutting down server")
            sys.exit(0)

        else:
            print("Commands: list | close <id> | exit")


def main():
    parser = argparse.ArgumentParser(description="MiniTLS Server")
    parser.add_argument("--max-clients", type=int, default=5)
    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"[+] Server listening on {HOST}:{PORT}")
    print(f"[+] Max clients: {args.max_clients}")

    threading.Thread(target=server_cli, daemon=True).start()
    accept_clients(server_socket, args.max_clients)


if __name__ == "__main__":
    main()
