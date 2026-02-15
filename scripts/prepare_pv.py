import pandas as pd
from io import StringIO

INP = "data/pvgis_hourly.csv"
OUT = "data/pv_15min_kw.csv"

with open(INP, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = None
for i, line in enumerate(lines):
    if line.strip().lower().startswith("time,"):
        start_idx = i
        break
if start_idx is None:
    raise RuntimeError("Could not find PVGIS table header line starting with 'time,'")

header = lines[start_idx].strip()
data_lines = [header]

for line in lines[start_idx + 1:]:
    s = line.strip()
    if not s:
        continue
    if len(s) >= 13 and s[0:8].isdigit() and s[8] == ":" and s[9:13].isdigit():
        data_lines.append(s)
    else:
        pass

csv_text = "\n".join(data_lines)
df = pd.read_csv(StringIO(csv_text))

df["timestamp"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M", errors="raise")
df = df.sort_values("timestamp").set_index("timestamp")

P = df["P"].astype(float)

if P.max() > 5000:
    df["pv_kw_hourly"] = P / 1000.0
else:
    df["pv_kw_hourly"] = P

pv_15 = df[["pv_kw_hourly"]].resample("15min").interpolate("time")
pv_15 = pv_15.rename(columns={"pv_kw_hourly": "pv_kw"}).reset_index()

pv_15.to_csv(OUT, index=False)
print("Wrote:", OUT, "rows:", len(pv_15), "pv_kw max:", pv_15["pv_kw"].max())