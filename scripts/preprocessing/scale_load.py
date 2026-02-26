# This script scales the prepared load profile to a target peak load (kW) (for operators: only change sections that are marked with ===CHANGE THESE===)

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# input file/path (===CHANGE THESE===)
inp = ROOT / "data" / "processed" / "load_15min_kw.csv"

# output file/path (===CHANGE THESE===)
out = ROOT / "data" / "processed" / "load_15min_kw_scaled.csv"

# target peak load in kW (===CHANGE THESE===)
TARGET_PEAK_KW = 400

out.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(inp)
peak = df["load_kw"].max()
scale = TARGET_PEAK_KW / peak

df["load_kw"] = df["load_kw"] * scale
df.to_csv(out, index=False)

print("Peak before:", peak)
print("Scale factor:", scale)
print("Peak after:", df["load_kw"].max())
print("Wrote:", out)