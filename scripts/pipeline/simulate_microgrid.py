import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import (
    LOAD_CSV, PV_CSV,
    RESULTS_DIR, SIM_DIR,
    DT_H, H_STEPS,
    PV_KWP,
    E_KWH, P_MAX_KW, SOC_MIN, SOC_MAX, SOC0, ETA_CH, ETA_DIS,
    ALPHA, BETA, GAMMA
)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SIM_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = SIM_DIR / "sim_results.csv"
METRICS_TXT = SIM_DIR / "metrics_summary.txt"

# Plot windows
WINDOWS = [
    ("2018-01-01", "2018-01-15", "jan_2w"),
    ("2018-07-01", "2018-07-15", "jul_2w"),
]

# Load + align data
load = pd.read_csv(LOAD_CSV, parse_dates=["timestamp"]).sort_values("timestamp")
pv   = pd.read_csv(PV_CSV,   parse_dates=["timestamp"]).sort_values("timestamp")

df = (
    pd.merge(load, pv, on="timestamp", how="inner")
      .sort_values("timestamp")
      .reset_index(drop=True)
)

df["net_kw"] = df["load_kw"] - df["pv_kw"]

net = df["net_kw"].to_numpy()
load_series = df["load_kw"].to_numpy()
pv_series   = df["pv_kw"].to_numpy()
N = len(df)

# Simulation main
soc = SOC0

soc_pre_list = []
soc_list = []
batt_p_list = []
unserved_list = []

p_req_list = []
e_req_list = []
p_dis_feasible_list = []
e_dis_avail_list = []
res_def_p_list = []
res_def_e_list = []

risk_event_list = []
risk_index_list = []

for i in range(N):
    net_kw = float(net[i])

    # SoC
    soc_pre = float(soc)
    soc_pre_list.append(soc_pre)

    # Energy margins
    e_avail_dis = max(0.0, (soc - SOC_MIN) * E_KWH)
    e_avail_chg = max(0.0, (SOC_MAX - soc) * E_KWH)

    # Feasible power this step
    p_dis_feasible = min(P_MAX_KW, e_avail_dis / DT_H)
    p_chg_feasible = min(P_MAX_KW, e_avail_chg / DT_H)

    # Rolling forecast
    h_eff = min(H_STEPS, N - i)
    load_hat = np.full(h_eff, load_series[i], dtype=float)
    pv_hat   = np.full(h_eff, pv_series[i], dtype=float)
    net_hat  = load_hat - pv_hat

    # Required reserve over horizon
    p_req = float(np.max(np.maximum(net_hat, 0.0)))
    e_req = float(np.sum(np.maximum(net_hat, 0.0)) * DT_H)

    res_def_p = float(max(0.0, p_req - p_dis_feasible))
    res_def_e = float(max(0.0, e_req - e_avail_dis))

    p_req_list.append(p_req)
    e_req_list.append(e_req)
    p_dis_feasible_list.append(float(p_dis_feasible))
    e_dis_avail_list.append(float(e_avail_dis))
    res_def_p_list.append(res_def_p)
    res_def_e_list.append(res_def_e)

    # Reactive BESS action
    batt_p = 0.0
    unserved = 0.0

    if net_kw > 0.0:
        batt_p = min(net_kw, p_dis_feasible)
        soc -= (batt_p * DT_H) / (ETA_DIS * E_KWH)
        unserved = max(0.0, net_kw - batt_p)

    elif net_kw < 0.0:
        batt_p = -min(-net_kw, p_chg_feasible)
        soc += (-batt_p * DT_H * ETA_CH) / E_KWH

    soc = min(SOC_MAX, max(SOC_MIN, soc))

    soc_list.append(float(soc))
    batt_p_list.append(float(batt_p))
    unserved_list.append(float(unserved))

    # Frequency-risk
    risk_event = (unserved > 0.0) or (res_def_p > 0.0) or (res_def_e > 0.0)
    risk_index = ALPHA * unserved + BETA * res_def_p + GAMMA * res_def_e

    risk_event_list.append(bool(risk_event))
    risk_index_list.append(float(risk_index))

df["soc_pre"] = soc_pre_list
df["soc"] = soc_list
df["batt_p_kw"] = batt_p_list
df["unserved_kw"] = unserved_list

df["p_req_kw"] = p_req_list
df["e_req_kwh"] = e_req_list
df["p_dis_feasible_kw"] = p_dis_feasible_list
df["e_dis_avail_kwh"] = e_dis_avail_list
df["reserve_deficit_p_kw"] = res_def_p_list
df["reserve_deficit_e_kwh"] = res_def_e_list

df["risk_event"] = risk_event_list
df["risk_index"] = risk_index_list

df.to_csv(OUT_CSV, index=False)
print(f"Saved results: {OUT_CSV} ({len(df)} rows)")

# Quiucklooks
QUICKLOOK_DIR = SIM_DIR / "quicklooks"
QUICKLOOK_DIR.mkdir(parents=True, exist_ok=True)

# daily summaries
dff = df.copy()
dff = dff.set_index("timestamp").sort_index()

daily = pd.DataFrame(index=dff.resample("D").mean().index)
daily["load_mean_kw"] = dff["load_kw"].resample("D").mean()
daily["pv_mean_kw"] = dff["pv_kw"].resample("D").mean()
daily["net_mean_kw"] = dff["net_kw"].resample("D").mean()

daily["soc_min"] = dff["soc"].resample("D").min()
daily["soc_med"] = dff["soc"].resample("D").median()
daily["soc_max"] = dff["soc"].resample("D").max()

daily["unserved_max_kw"] = dff["unserved_kw"].resample("D").max()
daily["risk_max"] = dff["risk_index"].resample("D").max()

W = 7
daily["load_mean_kw_roll7"] = daily["load_mean_kw"].rolling(W, min_periods=1).mean()
daily["pv_mean_kw_roll7"] = daily["pv_mean_kw"].rolling(W, min_periods=1).mean()
daily["net_mean_kw_roll7"] = daily["net_mean_kw"].rolling(W, min_periods=1).mean()

daily["soc_med_roll7"] = daily["soc_med"].rolling(W, min_periods=1).median()
daily["unserved_max_kw_roll7"] = daily["unserved_max_kw"].rolling(W, min_periods=1).mean()
daily["risk_max_roll7"] = daily["risk_max"].rolling(W, min_periods=1).mean()

plt.figure(figsize=(12, 4))
plt.plot(daily.index, daily["load_mean_kw"], label="Daily mean load (kW)", alpha=0.6)
plt.plot(daily.index, daily["load_mean_kw_roll7"], label="7d avg load", linestyle="--", linewidth=2.0)

plt.plot(daily.index, daily["pv_mean_kw"], label="Daily mean pv (kW)", alpha=0.6)
plt.plot(daily.index, daily["pv_mean_kw_roll7"], label="7d avg pv", linestyle="--", linewidth=2.0)

plt.plot(daily.index, daily["net_mean_kw"], label="Daily mean net deficit (kW)", alpha=0.6)
plt.plot(daily.index, daily["net_mean_kw_roll7"], label="7d avg net deficit", linestyle="--", linewidth=2.0)

plt.legend()
plt.title("Daily mean load / pv / net (full year)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(QUICKLOOK_DIR / "load_pv_net_full.png", dpi=200)
plt.close()

plt.figure(figsize=(12, 3))
plt.fill_between(daily.index, daily["soc_min"], daily["soc_max"], alpha=0.20, label="Daily soc min-max")
plt.plot(daily.index, daily["soc_med"], label="Daily soc median", alpha=0.65)
plt.plot(daily.index, daily["soc_med_roll7"], label="7d median soc", linestyle="--", linewidth=2.0)

plt.ylim(0, 1)
plt.legend()
plt.title("Daily battery soc band (full year)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(QUICKLOOK_DIR / "soc_full.png", dpi=200)
plt.close()

plt.figure(figsize=(12, 3))
plt.plot(daily.index, daily["unserved_max_kw"], label="Daily max unserved (kW)", alpha=0.65)
plt.plot(daily.index, daily["unserved_max_kw_roll7"], label="7d avg daily max", linestyle="--", linewidth=2.0)

plt.ylabel("Daily max unserved (kW)")
plt.legend()
plt.title("Daily max unserved load (full year)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(QUICKLOOK_DIR / "unserved_full.png", dpi=200)
plt.close()

plt.figure(figsize=(12, 3))
plt.plot(daily.index, daily["risk_max"], label="Daily max risk index", alpha=0.65)
plt.plot(daily.index, daily["risk_max_roll7"], label="7d avg daily max", linestyle="--", linewidth=2.0)

plt.ylabel("Daily max risk index")
plt.legend()
plt.title("Daily max risk index (full year)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(QUICKLOOK_DIR / "risk_index_full.png", dpi=200)
plt.close()

print(f"Saved quicklooks: {QUICKLOOK_DIR}")

# Metrics
total_unserved_kwh = float((df["unserved_kw"] * DT_H).sum())
pct_unserved_steps = float(100.0 * (df["unserved_kw"] > 0).mean())
max_unserved_kw = float(df["unserved_kw"].max())
pct_risk_steps = float(100.0 * df["risk_event"].mean())
max_risk_index = float(df["risk_index"].max())

# Write metrics
with open(METRICS_TXT, "w") as f:
    f.write("=== Key Metrics ===\n")
    f.write(f"PV_kWp: {PV_KWP}\n")
    f.write(f"H_STEPS: {H_STEPS}\n")
    f.write(f"DT_H: {DT_H}\n")
    f.write(f"BESS_E_kWh: {E_KWH}\n")
    f.write(f"BESS_Pmax_kW: {P_MAX_KW}\n")
    f.write(f"SoC_window: [{SOC_MIN}, {SOC_MAX}]\n")
    f.write(f"eta_ch: {ETA_CH}\n")
    f.write(f"eta_dis: {ETA_DIS}\n")
    f.write(f"Total unserved energy (kWh): {total_unserved_kwh:.2f}\n")
    f.write(f"Timesteps with unserved load (%): {pct_unserved_steps:.2f}\n")
    f.write(f"Max unserved power (kW): {max_unserved_kw:.2f}\n")
    f.write(f"Timesteps flagged as risk events (%): {pct_risk_steps:.2f}\n")
    f.write(f"Max risk index: {max_risk_index:.2f}\n")

print(f"Saved metrics: {METRICS_TXT}")

def plot_window(df_in, start, end, tag):
    start_ts = pd.Timestamp(start)
    end_ts   = pd.Timestamp(end)
    w = df_in[(df_in["timestamp"] >= start_ts) & (df_in["timestamp"] < end_ts)].copy()

    if w.empty:
        print(f"Empty window: {tag} ({start} -> {end})")
        return

    # Load + PV + Net
    plt.figure(figsize=(10, 4))
    plt.plot(w["timestamp"], w["load_kw"], label="Load (kW)")
    plt.plot(w["timestamp"], w["pv_kw"], label="PV (kW)")
    plt.plot(w["timestamp"], w["net_kw"], label="Net deficit (kW)")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(SIM_DIR / f"load_pv_net_{tag}.png", dpi=200)
    plt.close()

    # SoC
    plt.figure(figsize=(10, 3))
    plt.plot(w["timestamp"], w["soc"], label="SoC")
    plt.ylim(0, 1)
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(SIM_DIR / f"soc_{tag}.png", dpi=200)
    plt.close()

    # Unserved
    plt.figure(figsize=(10, 3))
    plt.plot(w["timestamp"], w["unserved_kw"])
    plt.ylabel("Unserved (kW)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(SIM_DIR / f"unserved_{tag}.png", dpi=200)
    plt.close()

    # Risk index
    plt.figure(figsize=(10, 3))
    plt.plot(w["timestamp"], w["risk_index"])
    plt.ylabel("Risk index")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(SIM_DIR / f"risk_index_{tag}.png", dpi=200)
    plt.close()

    print(f"Saved window plots to {SIM_DIR} for {tag}")

for s, e, tag in WINDOWS:
    plot_window(df, s, e, tag)

print("Simulation completed successfully")