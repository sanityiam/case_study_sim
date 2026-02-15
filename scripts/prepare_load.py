import pandas as pd

inp = "data/load_15min.csv"
out = "data/load_15min_kw.csv"

df = pd.read_csv(inp)
df["timestamp"] = pd.to_datetime(df["timestamp"])

df["load_kw"] = df["load_kwh"] / 0.25

df[["timestamp", "load_kw"]].to_csv(out, index=False)
print("Wrote:", out)
print(df[["timestamp", "load_kw"]].head())