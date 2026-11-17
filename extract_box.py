import io
import pandas as pd
import zstandard as zstd

SRC = "ais-2026-06-30.csv.zst"
OUT = "sample_ais.csv"

LAT_MIN, LAT_MAX = 47.0, 49.5
LON_MIN, LON_MAX = -125.0, -122.0

total = kept = 0
first = True

with open(SRC, "rb") as f:
    text = io.TextIOWrapper(zstd.ZstdDecompressor().stream_reader(f), encoding="utf-8")
    for chunk in pd.read_csv(text, chunksize=500_000):
        total += len(chunk)
        sub = chunk[chunk["latitude"].between(LAT_MIN, LAT_MAX)
                    & chunk["longitude"].between(LON_MIN, LON_MAX)]
        kept += len(sub)
        sub.to_csv(OUT, mode="w" if first else "a", header=first, index=False)
        first = False
        print(f"read {total:,} rows, kept {kept:,}")

print("done:", kept, "rows saved to", OUT)