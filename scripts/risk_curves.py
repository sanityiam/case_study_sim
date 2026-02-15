import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import SIM_DIR, RISK_DIR

# Paths
RISK_DIR.mkdir(parents=True, exist_ok=True)
IN_CSV = SIM_DIR / "sim_results.csv"

# Data
df = pd.read_csv(IN_CSV, parse_dates=["timestamp"]).sort_values("timestamp")

# Helpers
def plot_cdf(series, title, out_png):
    x = series.dropna().to_numpy()
    x = np.sort(x)
    y = np.arange(1, len(x) + 1) / len(x)

    plt.figure(figsize=(7, 4))
    plt.plot(x, y)
    plt.xlabel(series.name)
    plt.ylabel("CDF  P(X ≤ x)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def plot_exceedance(series, title, out_png):
    x = series.dropna().to_numpy()
    x = np.sort(x)
    y = 1.0 - (np.arange(1, len(x) + 1) / len(x))

    plt.figure(figsize=(7, 4))
    plt.plot(x, y)
    plt.yscale("log")
    plt.xlabel(series.name)
    plt.ylabel("Exceedance  P(X > x)  (log scale)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

# Risk curves
plot_cdf(df["risk_index"], "Risk index CDF", RISK_DIR / "risk_index_cdf.png")
plot_exceedance(df["risk_index"], "Risk index exceedance", RISK_DIR / "risk_index_exceedance.png")

plot_cdf(df["unserved_kw"], "Unserved power CDF", RISK_DIR / "unserved_cdf.png")
plot_exceedance(df["unserved_kw"], "Unserved power exceedance", RISK_DIR / "unserved_exceedance.png")

print("Saved risk curves in:", RISK_DIR)
print(" - risk_index_cdf.png")
print(" - risk_index_exceedance.png")
print(" - unserved_cdf.png")
print(" - unserved_exceedance.png")