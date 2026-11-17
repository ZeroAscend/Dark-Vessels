import io
import pandas as pd
import zstandard as zstd

SRC = "ais-2026-06-30.csv.zst"

with open(SRC, "rb") as f:
    text = io.TextIOWrapper(zstd.ZstdDecompressor().stream_reader(f), encoding="utf-8")
    df = pd.read_csv(text, nrows=5)

print(df.columns.tolist())
print(df)