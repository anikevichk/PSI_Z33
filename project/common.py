import os
import base64
import hashlib
import hmac
import json
import secrets
import socket
import struct
from typing import Any, Dict, Tuple

DEBUG = os.getenv("MINITLS_DEBUG", "").lower() in ("1", "true", "yes", "on")

def _dbg(direction: str, message: Dict[str, Any]) -> None:
    if not DEBUG:
        return
    try:
        pretty = json.dumps(message, ensure_ascii=False, sort_keys=True)
    except Exception:
        pretty = str(message)
    print(f"{direction} {pretty}", flush=True)


# 2048-bit MODP Group
DH = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF"
)
P = int(DH, 16)
G = 2


def _receive_exactly(sock: socket.socket, bytes_needed: int) -> bytes:
    data = b""
    while len(data) < bytes_needed:
        chunk = sock.recv(bytes_needed - len(data))
        if not chunk:
            raise ConnectionError("Socket closed while receiving data")
        data += chunk
    return data


def send_frame(sock: socket.socket, message: Dict[str, Any]) -> None:
    _dbg(">>", message)  
    payload = json.dumps(message, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sock.sendall(struct.pack("!I", len(payload)) + payload)


def recv_frame(sock: socket.socket) -> Dict[str, Any]:
    (payload_length,) = struct.unpack("!I", _receive_exactly(sock, 4))
    payload = _receive_exactly(sock, payload_length)
    msg = json.loads(payload.decode("utf-8"))
    _dbg("<<", msg) 
    return msg


def _base64_encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _base64_decode(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


def _int_to_bytes(value: int) -> bytes:
    length = (value.bit_length() + 7) // 8
    return value.to_bytes(length, "big") if length else b"\x00"


def kdf(shared_secret_integer: int, label: bytes) -> Tuple[bytes, bytes]:
    shared_secret_bytes = _int_to_bytes(shared_secret_integer)
    master_key = hashlib.sha256(shared_secret_bytes + b"miniTLS-v1" + label).digest()
    encryption_key = hashlib.sha256(master_key + b"enc").digest()
    mac_key = hashlib.sha256(master_key + b"mac").digest()
    return encryption_key, mac_key


def dh_generate_keypair() -> Tuple[int, int]:
    private_key = secrets.randbelow(P - 2) + 2
    public_key = pow(G, private_key, P)
    return private_key, public_key


def _keystream_bytes(encryption_key: bytes, sequence_number: int, length: int) -> bytes:
    sequence_bytes = struct.pack("!Q", sequence_number)
    output = b""
    counter = 0
    while len(output) < length:
        counter_bytes = struct.pack("!I", counter)
        output += hashlib.sha256(encryption_key + sequence_bytes + counter_bytes).digest()
        counter += 1
    return output[:length]


def xor_encrypt_or_decrypt(encryption_key: bytes, sequence_number: int, data: bytes) -> bytes:
    keystream = _keystream_bytes(encryption_key, sequence_number, len(data))
    return bytes(a ^ b for a, b in zip(data, keystream))


def compute_mac_tag(mac_key: bytes, sequence_number: int, ciphertext: bytes) -> bytes:
    sequence_bytes = struct.pack("!Q", sequence_number)
    return hmac.new(mac_key, sequence_bytes + ciphertext, hashlib.sha256).digest()


def verify_mac_tag(mac_key: bytes, sequence_number: int, ciphertext: bytes, received_tag: bytes) -> bool:
    expected_tag = compute_mac_tag(mac_key, sequence_number, ciphertext)
    return hmac.compare_digest(expected_tag, received_tag)


def make_encrypted_record( encryption_key: bytes, mac_key: bytes, sequence_number: int, inner_message: Dict[str, Any]) -> Dict[str, Any]:

    plaintext_bytes = json.dumps(inner_message, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ciphertext_bytes = xor_encrypt_or_decrypt(encryption_key, sequence_number, plaintext_bytes)
    mac_bytes = compute_mac_tag(mac_key, sequence_number, ciphertext_bytes)
    return {
        "type": "EncryptedData",
        "seq": sequence_number,
        "ct": _base64_encode(ciphertext_bytes),
        "mac": _base64_encode(mac_bytes),
    }


def open_encrypted_record( encryption_key: bytes, mac_key: bytes, expected_seq: int, rec: Dict[str, Any]) -> Dict[str, Any]:
    if rec.get("type") != "EncryptedData":
        raise ValueError("Unexpected record type")
    received_seq = int(rec.get("seq"))
    if received_seq != expected_seq:
        raise ValueError(f"Bad sequence number: expected {expected_seq}, got {received_seq}")
    ciphertext_bytes = _base64_decode(rec["ct"])
    received_mac = _base64_decode(rec["mac"])
    if not verify_mac_tag(mac_key, received_seq, ciphertext_bytes, received_mac):
        raise ValueError("Bad MAC")
    plaintext_bytes = xor_encrypt_or_decrypt(encryption_key, received_seq, ciphertext_bytes)
    return json.loads(plaintext_bytes.decode("utf-8"))
