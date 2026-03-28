import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Paths
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from config import SIM_DIR, EVENTS_DIR

EVENTS_DIR.mkdir(parents=True, exist_ok=True)

IN_CSV = SIM_DIR / "sim_results.csv"
TOP_EVENTS_CSV = EVENTS_DIR / "top_events.csv"

# Load
df = pd.read_csv(IN_CSV, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

# Classify contiguous unserved-load events
TOP_K = 5

df["is_event"] = df["unserved_kw"] > 0
df["event_start"] = df["is_event"] & (~df["is_event"].shift(1, fill_value=False))
df["event_id"] = df["event_start"].cumsum()
df.loc[~df["is_event"], "event_id"] = pd.NA

event_rows = df.dropna(subset=["event_id"]).copy()
event_rows["event_id"] = event_rows["event_id"].astype(int)

event_summary = (
    event_rows.groupby("event_id")
    .agg(
        onset=("timestamp", "min"),
        peak_unserved=("unserved_kw", "max"),
        max_risk=("risk_index", "max"),
        min_soc=("soc_pre", "min"),
    )
    .reset_index()
    .sort_values("peak_unserved", ascending=False)
    .head(TOP_K)
)

event_summary.to_csv(TOP_EVENTS_CSV, index=False)

# Context for each event
WINDOW_BEFORE_HOURS = 2
WINDOW_AFTER_HOURS = 1
DT_MIN = 15

W_BEFORE = int((WINDOW_BEFORE_HOURS * 60) / DT_MIN)
W_AFTER = int((WINDOW_AFTER_HOURS * 60) / DT_MIN)

def plot_event(ts_onset: pd.Timestamp):
    idx_arr = df.index[df["timestamp"] == ts_onset]
    if len(idx_arr) == 0:
        return
    idx = int(idx_arr[0])

    a = max(0, idx - W_BEFORE)
    b = min(len(df), idx + W_AFTER + 1)
    w = df.iloc[a:b].copy()

    # Create event folder
    event_folder = EVENTS_DIR / f"event_{ts_onset.strftime('%Y-%m-%d_%H%M')}"
    event_folder.mkdir(parents=True, exist_ok=True)

    # net.png (load + pv + net)
    plt.figure(figsize=(10, 4))

    plt.plot(
        w["timestamp"],
        w["net_kw"],
        label="Net deficit (kW)",
        color="tab:green",
        linewidth=1.8,
        alpha=0.85,
        zorder=1,
    )

    plt.plot(
        w["timestamp"],
        w["pv_kw"],
        label="PV (kW)",
        color="tab:orange",
        linewidth=2.0,
        zorder=2,
    )

    plt.plot(
        w["timestamp"],
        w["load_kw"],
        label="Load (kW)",
        color="black",
        linewidth=2.2,
        linestyle="--",
        zorder=3,
    )

    plt.title("Event window: load / PV / net deficit")
    plt.axvline(ts_onset, linestyle="--", color="tab:blue")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "net.png", dpi=200)
    plt.close()

    # soc_unserved.png
    fig, ax1 = plt.subplots(figsize=(10, 4))

    ax1.plot(
        w["timestamp"],
        w["unserved_kw"],
        label="Unserved (kW)",
        color="tab:red",
        linewidth=2.0,
    )
    ax1.set_ylabel("Unserved load (kW)", color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.plot(
        w["timestamp"],
        w["soc_pre"],
        label="SoC (pre)",
        color="tab:blue",
        linewidth=2.0,
        linestyle="--",
    )
    ax2.set_ylabel("SoC", color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    ax1.set_title("Event window: SoC and unserved load")
    ax1.axvline(ts_onset, linestyle="--", color="tab:blue")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2)

    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "soc_unserved.png", dpi=200)
    plt.close()

    # reserve.png
    plt.figure(figsize=(10, 4))
    if "reserve_deficit_p_kw" in w.columns:
        plt.plot(w["timestamp"], w["reserve_deficit_p_kw"], label="ReserveDef_P (kW)")
    if "reserve_deficit_e_kwh" in w.columns:
        plt.plot(w["timestamp"], w["reserve_deficit_e_kwh"], label="ReserveDef_E (kWh)")
    plt.title("Event window: reserve deficits")
    plt.axvline(ts_onset, linestyle="--", color="tab:blue")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "reserve.png", dpi=200)
    plt.close()

    # risk.png
    plt.figure(figsize=(10, 4))
    plt.plot(w["timestamp"], w["risk_index"], label="Risk index")
    plt.title("Event window: risk index")
    plt.axvline(ts_onset, linestyle="--", color="tab:blue")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(event_folder / "risk.png", dpi=200)
    plt.close()

# Plotting top events
for row in event_summary.itertuples(index=False):
    plot_event(pd.Timestamp(row.onset))

print("Saved:")
print(f" - {TOP_EVENTS_CSV}")
print(f" - event folders in: {EVENTS_DIR}")