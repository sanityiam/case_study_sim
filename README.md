![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18649192.svg)

**This repository provides:**
- End-to-end simulation pipeline
- Full PDF operator report
- Conference paper reproduction
- Predictive vs reactive comparison
- Top stress event plots
- SHAP Explainability
- Simple adjustable scenarios

The archived, citable version of this repository is available on Zenodo:
https://doi.org/10.5281/zenodo.18649192

**Requirements**
- Python 3.10
- macOS / Windows / Linux

**Two usage paths**
This repo supports two usage paths:

1. **Reproduce the conference paper results**
   - download raw public datasets
   - preprocess/convert them
   - run the full pipeline
   - get the same results

2. **Operator / custom scenario use**
   - provide your own input data in data/ folder
   - optionally adjust preprocessing scripts (only if your raw data needs it)
   - run the full pipeline
   - get an operator report + outputs for your scenario

**QUICK START (conference paper reproduction)**

**1. macOS / Linux**
*Run the following commands in your bash terminal one by one:*

git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
bash run.sh --clean

**2. Windows**
*Run the following commands in your bash terminal one by one:*

git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
run.bat --clean

**The pipeline will:**
- automatically create a local virtual environment
- automatically install dependencies from requirements.txt
- automatically download the public raw datasets into data/raw/
- preprocess
- simulate
- generate plots
- generate events + summaries
- generate explainability
- generate the final PDF report

**QUICK START (operator / custom scenario use)**

*Please chose one of the following options depending on your needs and present configuration:*

**Option 1 - you already have clean input CSV**

Put your ready input files here:
- data/processed/

**Then run the following commands in your bash terminal one by one:**

**macOS / Linux**

git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
bash run.sh --skip-download --skip-preprocessing --clean

**Windows**

git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
run.bat --skip-download --skip-preprocessing --clean

**Option 2 — you have raw datasets and you want preprocessing**

Put raw files into:
- data/raw/

Then go to:
- scripts/preprocessing/

Open these scripts and change the values marked as:
===CHANGE THESE===

Typical ones:
- prepare_load.py
- prepare_pv.py
- scale_load.py

*Then run the pipeline:*

**macOS / Linux**

git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
bash run.sh --skip-download --clean

**Windows**

git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
run.bat --skip-download --clean

**Expected output**

After a successful run, you will see outputs in results/

**Main final output**
- results/report/microgrid_stability_report.pdf

*This PDF includes:*
- run settings
- key metrics
- main figures
- top stress events
- predictive vs reactive comparison check
- automated operator notes based on the final results

*Also generated in separate folders:*
- results/compare/
- lead_time_minutes_hist.png
- predictive_vs_reactive_summary.txt
- warning_vs_event_timeline_sample.png

- results/events/
- top_events.csv
- event_YYYY-MM-DD_HHMM/ folders with:
- net.png
- soc_unserved.png
- reserve.png
- risk.png

- results/report/
- microgrid_stability_report.pdf

- results/risk_curves/
- risk_index_cdf.png
- risk_index_exceedance.png
- unserved_cdf.png
- unserved_exceedance.png

- results/sim/
- sim_results.csv
- metrics_summary.txt
- seasonal window plots (2-week windows):
- load_pv_net_jan_2w.png
- load_pv_net_jul_2w.png
- soc_jan_2w.png
- soc_jul_2w.png
- unserved_jan_2w.png
- unserved_jul_2w.png
- risk_index_jan_2w.png
- risk_index_jul_2w.png
- quicklooks/ (full-year summary):
- load_pv_net_full.png
- soc_full.png
- unserved_full.png
- risk_index_full.png

- results/xai/
- fig5_shap_importance_horizontal.png
- shap_beeswarm_wide.png
- model_metrics.txt
- top_drivers.txt

**Configuration**

All simulation/scenario parameters are defined in:
- config.py

This is the main file you edit to change the scenario:
- time step + forecast horizon
- PV size/label
- BESS energy/power
- SoC limits + SOC0
- efficiencies
- risk weights (alpha/beta/gamma)
- paths for data + results

Please only change the values marked as:
===CHANGE THESE===

*If you change scenario parameters - rerun:*

python3 runners/run_pipeline.py --clean

**Project overview**

This project implements a predictive, explainable stability risk assessment for islanded PV + BESS microgrids

*The core logic is:*
- calculate net imbalance (load - PV)
- check if BESS can support the next horizon under SoC-based limits
- flag risk and calculate risk index
- retrieve top extreme-events
- compare predictive vs reactive
- explain the risk drivers with SHAP
- generate an operator report - PDF

**What the pipeline does?**

*Running the pipeline executes:*
- data preparation
- microgrid simulation
- reserve feasibility checks over horizon
- risk event + risk index calculation
- daily summary figures
- top extreme-event detection -> event folders
- predictive vs reactive comparison
- SHAP explainability
- final PDF report

**Project structure**

case_study_sim/
  config.py
  README.md
  requirements.txt
  run.bat
  run.sh
  
  data/
    processed/
    raw/

  results/
    compare/
    events/
    report/
    risk_curves/
    sim/
    xai/

  runners/

  scripts/
    pipeline/
    preprocessing/

**Data availability**

*The datasets used for conference paper reproduction are publicly available:*
- Load data: NREL End-Use Load Profiles (OEDI)
- PV generation: PVGIS

Due to size, datasets are excluded from this repository

For the conference paper reproduction path, the public raw datasets are automatically downloaded into data/raw/ when you run:
(For Mac / Linux)
- bash run.sh --clean
(For Windows)
- run.bat --clean

The automated reproduction flow then:
- downloads the public raw datasets
- runs preprocessing
- stores processed inputs in data/processed/
- runs the simulation pipeline
- generates the final outputs in results/

If you are using the operator/custom scenario path, you can:
- provide your own already processed input files directly in data/processed/
- or place your own raw files into data/raw/, change the preprocessing scripts if needed and then run the *2. Operator / custom scenario use: QUICK START*

*(PV data in the example setup is fetched for Utqiagvik, Alaska: 71.2906 N, 156.7886 W.)*

**License**

This project is under the MIT License

**Citation**

If you use this repository, please cite:
“S. Klyuyev and M. Nassereddine, “Predictive Stability Risk Assessment Pipeline for Islanded PV-BESS Microgrids (Version 1.0.2),” Zenodo, Feb. 15, 2026. [Online]. Available: https://doi.org/10.5281/zenodo.18649191”