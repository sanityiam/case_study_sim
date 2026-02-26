# This script converts 15-minute load energy (kWh per interval) into load power (kW) (for operators: only change sections that are marked with ===CHANGE THESE===)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# input file/path (===CHANGE THESE===)
inp = ROOT / "data" / "processed" / "load_15min.csv"

# output file/path (===CHANGE THESE===)
out = ROOT / "data" / "processed" / "load_15min_kw.csv"

out.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(inp)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# interval duration in hours (===CHANGE THESE===)
df["load_kw"] = df["load_kwh"] / 0.25

df[["timestamp", "load_kw"]].to_csv(out, index=False)
print("Wrote:", out)
print(df[["timestamp", "load_kw"]].head())