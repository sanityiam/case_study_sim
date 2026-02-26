import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
import shap

from config import SIM_DIR, XAI_DIR, H_STEPS

# Paths
XAI_DIR.mkdir(parents=True, exist_ok=True)

IN_CSV = SIM_DIR / "sim_results.csv"
METRICS_TXT = XAI_DIR / "model_metrics.txt"
OUT_SHAP_BAR = XAI_DIR / "shap_summary_bar.png"
OUT_SHAP_BEE = XAI_DIR / "shap_beeswarm.png"

# Load data
df = (
    pd.read_csv(IN_CSV, parse_dates=["timestamp"])
      .sort_values("timestamp")
      .reset_index(drop=True)
)

# Early warning target
risk_event = df["risk_event"].astype(int).to_numpy()
y_next = np.zeros(len(df), dtype=int)

for i in range(len(df)):
    y_next[i] = int(risk_event[i:min(len(df), i + H_STEPS)].max())

df["risk_next_H"] = y_next

# Features
feature_cols = [
    "load_kw", "pv_kw", "net_kw",
    "soc_pre",
    "p_req_kw", "e_req_kwh",
    "p_dis_feasible_kw", "e_dis_avail_kwh",
    "reserve_deficit_p_kw", "reserve_deficit_e_kwh",
]

feature_cols = [c for c in feature_cols if c in df.columns]

X = df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
y = df["risk_next_H"].astype(int)

split = int(0.7 * len(df))
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

# Train model
clf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced",
)
clf.fit(X_train, y_train)

proba = clf.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, proba)
ap = average_precision_score(y_test, proba)
report = classification_report(y_test, (proba >= 0.5).astype(int))

# Save + print model metrics
with open(METRICS_TXT, "w", encoding="utf-8") as f:
    f.write("Early-warning model (predict risk within next H steps)\n")
    f.write(f"H_STEPS: {H_STEPS}\n")
    f.write(f"AUC: {auc:.3f}\n")
    f.write(f"AP : {ap:.3f}\n\n")
    f.write(report)

print("Early-warning model (predict risk within next H steps)")
print(f"H_STEPS: {H_STEPS}")
print(f"AUC: {auc:.3f}")
print(f"AP : {ap:.3f}")
print(report)

# SHAP
explainer = shap.TreeExplainer(clf)

X_explain = X_test.iloc[:5000]

shap_out = explainer.shap_values(X_explain)

if isinstance(shap_out, list):
    sv = shap_out[1]
else:
    sv = shap_out.values if hasattr(shap_out, "values") else shap_out
    if sv.ndim == 3:
        sv = sv[:, :, 1]

feature_labels = {
    "load_kw": "Load",
    "pv_kw": "PV",
    "net_kw": "Net deficit",
    "soc_pre": "BESS SoC",
    "p_req_kw": "Reserve power required",
    "e_req_kwh": "Reserve energy required",
    "p_dis_feasible_kw": "Feasible discharge power",
    "e_dis_avail_kwh": "Available discharge energy",
    "reserve_deficit_p_kw": "Reserve power deficit",
    "reserve_deficit_e_kwh": "Reserve energy deficit",
}

# horizontal view
OUT_SHAP_BAR = XAI_DIR / "fig5_shap_importance_horizontal.png"
TOP_N = 8 

mean_abs = np.abs(sv).mean(axis=0)
imp = (
    pd.Series(mean_abs, index=X_explain.columns)
      .sort_values(ascending=True)
      .tail(TOP_N)
)

imp.index = [feature_labels.get(c, c) for c in imp.index]

# save top drivers
TOP_DRIVERS_TXT = XAI_DIR / "top_drivers.txt"
top_drivers = list(imp.index)[::-1]
with open(TOP_DRIVERS_TXT, "w", encoding="utf-8") as f:
    for name in top_drivers[:5]:
        f.write(f"{name}\n")

print("Saved top drivers:", TOP_DRIVERS_TXT)

plt.figure(figsize=(9.0, 3.2))
plt.barh(imp.index, imp.values)
plt.xlabel("mean SHAP values")
plt.title("Primary drivers of predicted short-term risk (SHAP)")
plt.tight_layout()
plt.savefig(OUT_SHAP_BAR, dpi=600, bbox_inches="tight")
plt.close()

print("Saved compact SHAP figure:", OUT_SHAP_BAR)

# Beeswarm plot
OUT_SHAP_BEE = XAI_DIR / "shap_beeswarm_wide.png"
plt.figure(figsize=(9.0, 3.2))
shap.summary_plot(
    sv,
    X_explain,
    max_display=TOP_N,
    show=False,
    feature_names=[feature_labels.get(c, c) for c in X_explain.columns],
)
plt.tight_layout()
plt.savefig(OUT_SHAP_BEE, dpi=400, bbox_inches="tight")
plt.close()

print("Saved optional beeswarm:", OUT_SHAP_BEE)