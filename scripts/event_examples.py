import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from config import SIM_DIR, EVENTS_DIR

EVENTS_DIR.mkdir(parents=True, exist_ok=True)

IN_CSV = SIM_DIR / "sim_results.csv"
TOP_EVENTS_CSV = EVENTS_DIR / "top_events.csv"

# Load
df = pd.read_csv(IN_CSV, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

# Classify events
TOP_K = 5
events = df.nlargest(TOP_K, "unserved_kw")[["timestamp", "unserved_kw", "risk_index", "soc_pre"]].copy()
events.to_csv(TOP_EVENTS_CSV, index=False)

# Context for each event
WINDOW_HOURS = 6
DT_MIN = 15
W = int((WINDOW_HOURS * 60) / DT_MIN)

def plot_event(ts: pd.Timestamp):
    idx_arr = df.index[df["timestamp"] == ts]
    if len(idx_arr) == 0:
        return
    idx = int(idx_arr[0])

    a = max(0, idx - W)
    b = min(len(df), idx + W)
    w = df.iloc[a:b].copy()

    # Create event folder
    event_folder = EVENTS_DIR / f"event_{ts.strftime('%Y-%m-%d_%H%M')}"
    event_folder.mkdir(parents=True, exist_ok=True)

    # net.png (load + pv + net)
    plt.figure(figsize=(10, 4))
    plt.plot(w["timestamp"], w["load_kw"], label="Load (kW)")
    plt.plot(w["timestamp"], w["pv_kw"], label="PV (kW)")
    plt.plot(w["timestamp"], w["net_kw"], label="Net deficit (kW)")
    plt.axvline(ts, linestyle="--")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "net.png", dpi=200)
    plt.close()

    # soc_unserved.png
    plt.figure(figsize=(10, 4))
    plt.plot(w["timestamp"], w["soc_pre"], label="SoC (pre)")
    plt.plot(w["timestamp"], w["unserved_kw"], label="Unserved (kW)")
    plt.axvline(ts, linestyle="--")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "soc_unserved.png", dpi=200)
    plt.close()

    # reserve.png (reserve deficit)
    plt.figure(figsize=(10, 4))
    if "reserve_deficit_p_kw" in w.columns:
        plt.plot(w["timestamp"], w["reserve_deficit_p_kw"], label="ReserveDef_P (kW)")
    if "reserve_deficit_e_kwh" in w.columns:
        plt.plot(w["timestamp"], w["reserve_deficit_e_kwh"], label="ReserveDef_E (kWh)")
    plt.axvline(ts, linestyle="--")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "reserve.png", dpi=200)
    plt.close()

    # risk.png (risk index)
    plt.figure(figsize=(10, 4))
    plt.plot(w["timestamp"], w["risk_index"], label="Risk index")
    plt.axvline(ts, linestyle="--")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "risk.png", dpi=200)
    plt.close()

# Plotting main events
for row in events.itertuples(index=False):
    plot_event(pd.Timestamp(row.timestamp))

print("Saved:")
print(f" - {TOP_EVENTS_CSV}")
print(f" - event folders in: {EVENTS_DIR}")