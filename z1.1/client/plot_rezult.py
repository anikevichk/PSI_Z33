import csv
import os
import matplotlib.pyplot as plt


csv_path = "rezults.csv"
sizes = []
rtts = []

with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["avg_rtt_ms"].strip().upper() == "FAIL" or not row["avg_rtt_ms"].strip():
            continue
        sizes.append(int(row["size_B"]))
        rtts.append(float(row["avg_rtt_ms"]))


plt.figure(figsize=(8,5))
plt.plot(sizes, rtts, marker='o', label='Średni RTT')
plt.xscale('log', base=2)
plt.xlabel("Rozmiar datagramu [B]")
plt.ylabel("Średni RTT [ms]")
plt.title("Pomiar RTT w funkcji rozmiaru datagramu UDP")
plt.grid(True)
plt.legend()
plt.tight_layout()

out_name = "rezults_plot.png"
plt.savefig(out_name, dpi=150)
plt.show()
