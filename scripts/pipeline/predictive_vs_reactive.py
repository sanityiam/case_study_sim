# Predictive vs Reactive evaluation
# Reactive detection: event occurs when unserved_kw > 0
# Predictive early warning: warning signal when reserve_deficit_p_kw > 0 OR reserve_deficit_e_kwh > 0

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import project config paths
from config import SIM_DIR, COMPARE_DIR, DT_MIN, H_STEPS

EVAL_DIR = COMPARE_DIR
EVAL_DIR.mkdir(parents=True, exist_ok=True)

IN_CSV = SIM_DIR / "sim_results.csv"
OUT_TXT = EVAL_DIR / "predictive_vs_reactive_summary.txt"
OUT_OP_TXT = EVAL_DIR / "predictive_vs_reactive_operator.txt"
OUT_CDF = EVAL_DIR / "lead_time_cdf.png"
OUT_HIST = EVAL_DIR / "lead_time_minutes_hist.png"
OUT_TIMELINE = EVAL_DIR / "warning_vs_event_timeline_sample.png"


def compute_future_event(y_event: np.ndarray, h_steps: int) -> np.ndarray:
    """
    y_future[t] = 1 if an event occurs at any time in [t, t+h_steps)
    """
    n = len(y_event)
    y_future = np.zeros(n, dtype=int)
    for t in range(n):
        y_future[t] = int(y_event[t:min(n, t + h_steps)].max())
    return y_future


def find_event_onsets(event: np.ndarray) -> np.ndarray:
    """
    Return indices where event transitions 0 -> 1
    """
    event = event.astype(int)
    prev = np.r_[0, event[:-1]]
    onsets = np.where((prev == 0) & (event == 1))[0]
    return onsets

def plot_lead_time_cdf(lead_minutes: np.ndarray, out_path: Path):
    if len(lead_minutes) == 0:
        return
    x = np.sort(lead_minutes)
    y = np.arange(1, len(x) + 1) / float(len(x))

    plt.figure(figsize=(7, 4))
    plt.plot(x, y)
    plt.xlabel("Warning time before outage onset (minutes)")
    plt.ylabel("Fraction of outage onsets covered")
    plt.title("How early warnings arrive (CDF)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()

def build_operator_summary(coverage, median_lead, p90_lead, missed, precision, horizon_minutes):
    false_alarm_pct = (1.0 - float(precision)) * 100.0 if precision is not None else 0.0
    cov_pct = float(coverage) * 100.0

    lines = []
    lines.append("Early-warning vs reactive")
    lines.append(f"- Coverage: This model warns before {cov_pct:.1f}% of outages onsets")
    lines.append(f"- Typical warning time: median {median_lead:.0f} min (90% of the time < {p90_lead:.0f} min)")
    lines.append(f"- Missed events: {missed} events had no warning inside the horizon ({horizon_minutes:.0f} min)")
    lines.append(f"- False alarms: about {false_alarm_pct:.1f}% of warnings do not lead to an outage (precision {precision*100.0:.1f}%)")
    lines.append("")
    lines.append("Operator takeaway")
    lines.append("- If warning is appears: you usually have 1–2 hours to respond")
    lines.append("- Main goal: keep SoC higher / reduce net deficit peaks during warning periods")
    return "\n".join(lines) + "\n"

def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"missing {IN_CSV} - run simulation first")

    df = pd.read_csv(IN_CSV, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    # reactive event definition
    if "unserved_kw" not in df.columns:
        raise RuntimeError("sim_results.csv missing column 'unserved_kw'")

    reactive_event = (df["unserved_kw"].to_numpy() > 0.0).astype(int)

    # predictive warning signal definition
    required_cols = ["reserve_deficit_p_kw", "reserve_deficit_e_kwh"]
    for c in required_cols:
        if c not in df.columns:
            raise RuntimeError(f"sim_results.csv missing column '{c}' (needed for predictive warning)")

    warn = (
        (df["reserve_deficit_p_kw"].to_numpy() > 0.0)
        | (df["reserve_deficit_e_kwh"].to_numpy() > 0.0)
    ).astype(int)

    # evaluation target definition
    y_future = compute_future_event(reactive_event, H_STEPS)

    tp = int(((warn == 1) & (y_future == 1)).sum())
    fp = int(((warn == 1) & (y_future == 0)).sum())
    tn = int(((warn == 0) & (y_future == 0)).sum())
    fn = int(((warn == 0) & (y_future == 1)).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # lead-time analysis
    onsets = find_event_onsets(reactive_event)
    lead_steps = []
    missed = 0

    for idx in onsets:
        a = max(0, idx - H_STEPS)
        window = warn[a:idx]
        if window.sum() == 0:
            missed += 1
            continue
        # earliest warning in that window
        first_warn_idx = a + int(np.where(window == 1)[0][0])
        lead = idx - first_warn_idx
        lead_steps.append(lead)

    lead_steps = np.array(lead_steps, dtype=float) if len(lead_steps) else np.array([], dtype=float)
    lead_minutes = lead_steps * float(DT_MIN)

    coverage = 1.0 - (missed / len(onsets)) if len(onsets) > 0 else 0.0
    median_lead = float(np.median(lead_minutes)) if len(lead_minutes) else 0.0
    p90_lead = float(np.quantile(lead_minutes, 0.90)) if len(lead_minutes) else 0.0

    horizon_minutes = float(H_STEPS) * float(DT_MIN)

    # summary
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("Detailed Predictive vs Reactive Evaluation\n")
        f.write("reactive event: outage happens when unserved_kw > 0\n")
        f.write("early-warning: warnings appear when reserve_deficit_p_kw > 0 OR reserve_deficit_e_kwh > 0\n")
        f.write(f"horizon: {horizon_minutes:.0f} minutes (H_STEPS={H_STEPS}, DT_MIN={DT_MIN})\n\n")

        f.write("1. Warning as predictor of outage within the next horizon\n")
        f.write(f"TP={tp}  FP={fp}  TN={tn}  FN={fn}\n")
        f.write(f"precision={precision:.3f}\n")
        f.write(f"recall   ={recall:.3f}\n\n")

        f.write("2. Warning time before outage onset (0->1 transitions)\n")
        f.write(f"number of outage onsets: {len(onsets)}\n")
        f.write(f"coverage of onsets: {coverage*100:.2f}%\n")
        f.write(f"median warning time (min): {median_lead:.1f}\n")
        f.write(f"90th percentile warning time (min): {p90_lead:.1f}\n")
        f.write(f"missed onsets (no warning): {missed}\n")

    print(f"Saved: {OUT_TXT}")

    # operator summary
    op_text = build_operator_summary(
        coverage=coverage,
        median_lead=median_lead,
        p90_lead=p90_lead,
        missed=missed,
        precision=precision,
        horizon_minutes=horizon_minutes,
    )
    with open(OUT_OP_TXT, "w", encoding="utf-8") as f:
        f.write(op_text)
    print(f"Saved: {OUT_OP_TXT}")

    # plot
    if len(lead_minutes) > 0:
        plot_lead_time_cdf(lead_minutes, OUT_CDF)
        print(f"Saved: {OUT_CDF}")

        # histogram
        plt.figure(figsize=(7, 4))
        plt.hist(lead_minutes, bins=min(20, max(5, len(lead_minutes)//2)))
        plt.xlabel("warning time before outage onset (min)")
        plt.ylabel("count")
        plt.title("warning time distribution (histogram)")
        plt.tight_layout()
        plt.savefig(OUT_HIST, dpi=200)
        plt.close()
        print(f"Saved: {OUT_HIST}")

    if len(onsets) > 0:
        center = int(onsets[0])
        W = 24 * 4  # 24 hours at 15min steps
        a = max(0, center - W)
        b = min(len(df), center + W)
        w = df.iloc[a:b].copy()

        plt.figure(figsize=(10, 3.5))
        plt.plot(w["timestamp"], (w["unserved_kw"] > 0).astype(int), label="Reactive event (unserved>0)")
        plt.plot(w["timestamp"], (
            (w["reserve_deficit_p_kw"] > 0) | (w["reserve_deficit_e_kwh"] > 0)
        ).astype(int), label="Predictive warning (reserve deficit)")
        plt.ylim(-0.1, 1.1)
        plt.legend()
        plt.xticks(rotation=25)
        plt.title("Predictive warning vs reactive detection")
        plt.tight_layout()
        plt.savefig(OUT_TIMELINE, dpi=200)
        plt.close()
        print(f"Saved: {OUT_TIMELINE}")

if __name__ == "__main__":
    main()