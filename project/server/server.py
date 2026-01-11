import socket
from common import *

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 4444


def run_server() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listening_socket:
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listening_socket.bind((SERVER_HOST, SERVER_PORT))
        listening_socket.listen(1)
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

        client_socket, client_address = listening_socket.accept()
        with client_socket:
            print(f"Connected: {client_address}")

            client_hello_message = recv_frame(client_socket)
            if client_hello_message.get("type") != "ClientHello":
                raise RuntimeError("Handshake error: expected ClientHello")

            client_public_key = int(client_hello_message["ClientPublicKey"])
            if not (2 <= client_public_key <= P - 2):
                raise RuntimeError("Handshake error: invalid client public key")

            server_private_key, server_public_key = dh_generate_keypair()

            server_hello_message = {
                "type": "ServerHello",
                "ServerPublicKey": str(server_public_key),
            }
            send_frame(client_socket, server_hello_message)

            shared_secret = pow(client_public_key, server_private_key, P)
            k_enc_in,  k_mac_in  = kdf(shared_secret, b"c2s")  
            k_enc_out, k_mac_out = kdf(shared_secret, b"s2c")  
            print("Session keys derived")

            next_outgoing_sequence_number = 0
            next_expected_incoming_sequence_number = 0

            while True:
                encrypted_record = recv_frame(client_socket)

                decrypted_payload = open_encrypted_record(
                    encryption_key=k_enc_in, mac_key=k_mac_in,
                    expected_seq=next_expected_incoming_sequence_number,
                    rec=encrypted_record,
                )
                next_expected_incoming_sequence_number += 1

                inner_message_type = decrypted_payload.get("innerType")

                if inner_message_type == "Data":
                    received_text = decrypted_payload.get("text", "")
                    print(f"Client says: {received_text}")

                    response_payload = {
                        "innerType": "Data",
                        "text": f"{received_text}",
                    }
                    encrypted_response_record = make_encrypted_record(
                        k_enc_out, k_mac_out,
                        next_outgoing_sequence_number,
                        response_payload,
                    )
                    send_frame(client_socket, encrypted_response_record)
                    next_outgoing_sequence_number += 1

                elif inner_message_type == "EndSession":
                    print("EndSession received, closing connection.")
                    break

                else:
                    print(f"Unknown innerType: {inner_message_type}")


if __name__ == "__main__":
    run_server()
