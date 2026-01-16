import socket
import sys
from common import *

PORT = 4444

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, PORT))
        print(f"Connected to {host}:{PORT}")

        cli_priv, cli_pub = dh_generate_keypair()
        send_frame(s, {
            "type": "ClientHello",
            "dh_pub": cli_pub
        })

        msg = recv_frame(s)
        if msg.get("type") != "ServerHello":
            raise RuntimeError("Expected ServerHello")
        srv_pub = int(msg["dh_pub"])
        if not (2 <= srv_pub <= P - 2):
            raise RuntimeError("Bad server public key")

        shared = pow(srv_pub, cli_priv, P)

        k_enc_out, k_mac_out = kdf(shared, b"c2s")
        k_enc_in,  k_mac_in  = kdf(shared, b"s2c")
        print("Session keys derived")
        print("Type messages. Use /quit to end.\n")

        send_seq = 0
        recv_seq = 0

        while True:
            line = input("> ").strip()
            if not line:
                continue

            if line == "/quit":
                inner = {"type": "END_SESSION"}
                send_frame(s, make_encrypted_record(k_enc_out, k_mac_out, send_seq, inner))
                send_seq += 1
                print("Sent EndSession")
                break

            inner = {
                "type": "DATA",
                "text": line
            }
            send_frame(s, make_encrypted_record(k_enc_out, k_mac_out, send_seq, inner))
            send_seq += 1

            rec = recv_frame(s)
            inner_reply = open_encrypted_record(k_enc_in, k_mac_in, recv_seq, rec)
            recv_seq += 1
            if inner_reply.get("type") == "DATA":
                print(f"Server: {inner_reply.get('text','')}")
            else:
                print("Server sent:", inner_reply)


if __name__ == "__main__":
    main()
