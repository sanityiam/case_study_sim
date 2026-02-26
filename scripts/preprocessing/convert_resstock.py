# This script converts the raw ResStock parquet file into a 15-minute load CSV (for operators: only change sections that are marked with ===CHANGE THESE===)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# raw load filename/path (===CHANGE THESE===)
inp = ROOT / "data" / "raw" / "resstock_building.parquet"

# processed output filename/path (===CHANGE THESE===)
out = ROOT / "data" / "processed" / "load_15min.csv"

out.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(inp)

print("Columns:", list(df.columns))
print(df.head())

candidate_cols = [c for c in df.columns if "electric" in c.lower() and ("total" in c.lower() or "site" in c.lower())]
print("Candidate cols:", candidate_cols)

load_col = candidate_cols[0]

if "timestamp" in df.columns:
    ts = pd.to_datetime(df["timestamp"])
else:
    ts = pd.to_datetime(df.index)

out_df = pd.DataFrame({"timestamp": ts, "load_kwh": df[load_col].astype(float)})
out_df.to_csv(out, index=False)
print("Wrote:", out)