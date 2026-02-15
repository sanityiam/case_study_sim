import pandas as pd

inp = "data/resstock_building.parquet"
out = "data/load_15min.csv"

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