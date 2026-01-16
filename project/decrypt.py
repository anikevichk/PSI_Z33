import base64
import hashlib
import struct
import json

ct_b64 = "f4Ea2igvlvqgy0ZP06QuUAPls92Tj1Kd1XNApQ=="
seq = 0

with open("PSI_Z33/project/session_keys_client_1.bin", "rb") as f:
    for line in f:
        if line.startswith(b"c2s_enc="):   # or c2s_enc
            key = line[len(b"c2s_enc="):].strip()

ct = base64.b64decode(ct_b64)

def keystream(enc_key, seq, length):
    seq_bytes = struct.pack("!Q", seq)   
    out = b""
    counter = 0
    while len(out) < length:
        ctr_bytes = struct.pack("!I", counter)  
        out += hashlib.sha256(enc_key + seq_bytes + ctr_bytes).digest()
        counter += 1
    return out[:length]
ks = keystream(key, seq, len(ct))
pt = bytes(c ^ k for c, k in zip(ct, ks))

print("PT HEX :", pt.hex())
print("PT RAW :", pt)

if pt.startswith(b"{"):
    print("JSON:", json.loads(pt.decode("utf-8")))
else:
    print("NOT JSON — wrong key / seq / direction")
