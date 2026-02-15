import pandas as pd

inp = "data/load_15min_kw.csv"
out = "data/load_15min_kw_scaled.csv"

TARGET_PEAK_KW = 400

df = pd.read_csv(inp)
peak = df["load_kw"].max()
scale = TARGET_PEAK_KW / peak

df["load_kw"] = df["load_kw"] * scale
df.to_csv(out, index=False)

print("Peak before:", peak)
print("Scale factor:", scale)
print("Peak after:", df["load_kw"].max())
print("Wrote:", out)