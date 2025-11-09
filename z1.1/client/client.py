import socket, sys, time, statistics, csv

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2] if len(sys.argv) > 2 else 8000)

UDP_MAX = 65507
SIZES = []
s = 2
while s <= UDP_MAX:
    SIZES.append(s)
    s *= 2
if SIZES[-1] != UDP_MAX:
    SIZES.append(UDP_MAX)

def avg_rtt(size, trials=5, timeout=2.0):
    payload = b'a' * size
    rtts = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    for _ in range(trials):
        t0 = time.perf_counter_ns()
        sock.sendto(payload, (HOST, PORT))
        try:
            data, _ = sock.recvfrom(70000)
        except socket.timeout:
            sock.close(); return None
        t1 = time.perf_counter_ns()
        if data != payload:
            sock.close(); return None
        rtts.append((t1 - t0) / 1e6)
    sock.close()
    return statistics.mean(rtts)

print("size_B,avg_rtt_ms")
rows = []
max_ok = 0
for sz in SIZES:
    r = avg_rtt(sz)
    if r is None:
        print(f"{sz},FAIL")
        break
    print(f"{sz},{r:.3f}")
    rows.append({"size_B": sz, "avg_rtt_ms": f"{r:.3f}"})
    max_ok = sz

with open("rezults.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["size_B","avg_rtt_ms"])
    w.writeheader(); w.writerows(rows)

print(f"\nMAX poprawnie obsługiwany payload ≈ {max_ok} B")
print("Wyniki zapisane do rezults.csv")
