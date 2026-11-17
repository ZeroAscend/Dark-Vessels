import numpy as np
import matplotlib.pyplot as plt

from gaps import load_ais, find_gaps

df = load_ais("sample_ais.csv")

print("Gap counts by threshold:")
for m in (15, 30, 60, 120):
    print(f"  {m:>3} min: {len(find_gaps(df, m))} gaps")

gaps = find_gaps(df, 30)
gaps.to_csv("gaps.csv", index=False)

bins = np.logspace(np.log10(30), np.log10(gaps["gap_minutes"].max()), 40)
plt.hist(gaps["gap_minutes"], bins=bins)
plt.xscale("log")
plt.xlabel("Gap length (minutes, log scale)")
plt.ylabel("Number of gaps")
plt.title("AIS gap lengths, 2026-06-30, test region")
plt.savefig("gap_hist.png", dpi=150)
plt.show()