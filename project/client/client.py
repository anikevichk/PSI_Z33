import socket
import sys

from common import *

PORT = 4444


def do_handshake(sock):
    client_priv, client_pub = dh_generate_keypair()

    send_frame(sock, {
        "type": "ClientHello",
        "dh_pub": client_pub,
    })

    msg = recv_frame(sock)
    if msg.get("type") != "ServerHello":
        raise RuntimeError("Expected ServerHello")

    server_pub = int(msg["dh_pub"])
    if not (2 <= server_pub <= P - 2):
        raise RuntimeError("Invalid server DH public key")

    shared_secret = pow(server_pub, client_priv, P)

    k_enc_out, k_mac_out = kdf(shared_secret, b"c2s")
    k_enc_in, k_mac_in = kdf(shared_secret, b"s2c")

    print("[i] Session established")

    return k_enc_out, k_mac_out, k_enc_in, k_mac_in


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <server-host>")
        sys.exit(1)

    host = sys.argv[1]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, PORT))

    connected = False
    k_enc_out = k_mac_out = None
    k_enc_in = k_mac_in = None
    send_seq = 0
    recv_seq = 0

    print("Type messages. Use /connect to start session, /quit to end session.")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break

        if line == "/connect":
            if connected:
                print("[!] Session already active")
                continue

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, PORT))

                k_enc_out, k_mac_out, k_enc_in, k_mac_in = do_handshake(s)
                send_seq = 0
                recv_seq = 0
                connected = True
            except Exception as e:
                print(f"[!] Handshake failed: {e}")
                if s:
                    s.close()
                    s = None
            continue


        if line == "/quit":
            if connected:
                try:
                    send_frame(s, make_encrypted_record(
                        k_enc_out,
                        k_mac_out,
                        send_seq,
                        {"type": "END_SESSION"}
                    ))
                except Exception:
                    pass

            print("[i] Session closed")

            s.close()
            connected = False
            s = None
            continue


        if not connected:
            print("[!] No active session. Use /connect.")
            continue

        try:
            send_frame(s, make_encrypted_record(
                k_enc_out,
                k_mac_out,
                send_seq,
                {"type": "DATA", "text": line}
            ))
            send_seq += 1

            record = recv_frame(s)
            inner = open_encrypted_record(
                k_enc_in,
                k_mac_in,
                recv_seq,
                record
            )
            recv_seq += 1

            print(f"Server: {inner.get('text', '')}")

        except Exception as e:
            print(f"[!] Communication error: {e}")
            connected = False
            k_enc_out = k_mac_out = None
            k_enc_in = k_mac_in = None
            print("[i] Session invalidated. Use /connect.")

    s.close()


if __name__ == "__main__":
    main()
