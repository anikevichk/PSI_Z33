import socket
import time
import statistics
import csv

HOST = "172.21.33.2"
PORT = 8000
UDP_MAX_PAYLOAD = 65507


def build_test_sizes(max_payload):
    sizes = []
    size = 2
    while size <= max_payload:
        sizes.append(size)
        size *= 2
    if sizes[-1] != max_payload:
        sizes.append(max_payload)
    return sizes


def measure_avg_rtt(payload_size, trials=1, timeout=5.0):
    payload = b"a" * payload_size
    rtts_ms = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    for _ in range(trials):
        t0 = time.perf_counter_ns()
        sock.sendto(payload, (HOST, PORT))
        try:
            data, _ = sock.recvfrom(65535)
            if data != payload:
                print(f"Received unexpected data for size {payload_size}")
                sock.close()
                return None
        except socket.timeout:
            print(f"Request timeout for packet size {payload_size} bytes")
            sock.close()
            return None
        t1 = time.perf_counter_ns()
        rtts_ms.append((t1 - t0) / 1e6)

    sock.close()
    return statistics.mean(rtts_ms)


def find_max_supported_size(test_sizes):
    print("size_B,avg_rtt_ms")
    results_rows = []

    last_ok_size = None
    first_fail_size = None

    for size in test_sizes:
        avg_rtt = measure_avg_rtt(size)
        if avg_rtt is None:
            print(f"{size},FAIL")
            first_fail_size = size
            break
        print(f"{size},{avg_rtt:.3f}")
        results_rows.append({"size_B": size, "avg_rtt_ms": f"{avg_rtt:.3f}"})
        last_ok_size = size

    if last_ok_size is None:
        print("No payload size was handled correctly.")
        return None, results_rows

    if first_fail_size is None:
        max_supported_size = last_ok_size
        return max_supported_size, results_rows

    print("=====BINARY SEARCH=====")
    low_ok = last_ok_size
    high_fail = first_fail_size

    while high_fail - low_ok > 1:
        mid = (low_ok + high_fail) // 2
        avg_rtt = measure_avg_rtt(mid)
        if avg_rtt is None:
            print(f"{mid},FAIL")
            high_fail = mid
        else:
            print(f"{mid},{avg_rtt:.3f}")
            results_rows.append(
                {"size_B": mid, "avg_rtt_ms": f"{avg_rtt:.3f}"}
            )
            low_ok = mid

    max_supported_size = low_ok
    return max_supported_size, results_rows


def save_results_to_csv(filename, results_rows):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["size_B", "avg_rtt_ms"])
        writer.writeheader()
        writer.writerows(results_rows)


def main():
    test_sizes = build_test_sizes(UDP_MAX_PAYLOAD)

    max_supported_size, results_rows = find_max_supported_size(test_sizes)
    if max_supported_size is None:
        return

    save_results_to_csv("results.csv", results_rows)

    print(f"\nMAX supported payload ≈ {max_supported_size} B")
    print("Results saved to results.csv")


if __name__ == "__main__":
    main()
