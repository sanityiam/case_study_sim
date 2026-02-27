# Main operator settings (change all parameters here and only change the ones that are marked as ===CHANGE THESE===)
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR    = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

RESULTS_DIR = PROJECT_ROOT / "results"
SIM_DIR     = RESULTS_DIR / "sim"
RISK_DIR    = RESULTS_DIR / "risk_curves"
EVENTS_DIR  = RESULTS_DIR / "events"
XAI_DIR     = RESULTS_DIR / "xai"
COMPARE_DIR = RESULTS_DIR / "compare"
REPORT_DIR = RESULTS_DIR / "report"

FIG_DIR     = PROJECT_ROOT / "figures"
QUICKLOOKS_DIR = FIG_DIR / "quicklooks"

# Input files (===CHANGE THESE===)
LOAD_CSV = DATA_DIR / "processed" / "load_15min_kw_scaled.csv"
PV_CSV   = DATA_DIR / "processed" / "pv_15min_kw.csv"

# Time base (===CHANGE THESE===)
DT_MIN = 15
DT_H   = DT_MIN / 60.0

# Forecast horizon (===CHANGE THESE===)
H_STEPS = 8
H_HOURS = H_STEPS * DT_H

# PV system size label (PVGIS peak power) (===CHANGE THESE===)
PV_KWP = 300.0

# Battery parameters (===CHANGE THESE===)
E_KWH     = 500.0
P_MAX_KW  = 250.0
SOC_MIN   = 0.20
SOC_MAX   = 0.80
SOC0      = 0.50
ETA_CH    = 0.95
ETA_DIS   = 0.95

# Risk proxy weights = ALPHA - unserved power weight (kW); BETA - reserve deficit power weight (kW); GAMMA - reserve deficit energy weight (kWh) (===CHANGE THESE===)
ALPHA = 1.0
BETA  = 1.0
GAMMA = 1.0