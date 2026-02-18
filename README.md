![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18649192.svg)

Python pipeline reproducing the methodology and figures from the IEEE conference paper on feasibility-based stability risk assessment

This repository provides:
- End-to-end simulation pipeline
- Reproduction of paper figures
- Explainability analysis
- Adjustable microgrid scenarios

The archived, citable version of this repository is available on Zenodo:
https://doi.org/10.5281/zenodo.18649192

Quick start:
git clone https://github.com/sanityiam/case_study_sim.git
cd case_study_sim
pip install -r requirements.txt
python run_pipeline.py

Expected output:
Running the pipeline automatically generates:
- Seasonal simulation graphs
- Risk curves
- SHAP explainability figures

Outputs are saved in:
results/sim/
results/risk_curves/
results/xai/

Project overview:
This project implements a predictive, explainable early-warning stability risk assessment for islanded AC PV+BESS microgrids, focusing on frequency stability, generation-load imbalance, and unserved load risk.

This executes:
- Data preparation
- Microgrid simulation
- Risk index calculation
- Extreme event detection
- Explainability analysis
- Plot generation

Requirements:
- Python 3.10
- macOS / Windows / Linux

Install dependencies:
pip install -r requirements.txt

Run the full pipeline:
python run_pipeline.py

Project Structure:
case_study_sim/
├── data/
├── results/
│   ├── events/
│   ├── risk_curves/
│   ├── sim/
│   └── xai/
├── scripts/
├── config.py
├── run_pipeline.py
└── README.md

Configuration:
All simulation parameters are defined in config.py:
- time step and forecast period
- PV parameters
- BESS parameters
- SoC limits
- Risk index weights

This is the main file that needs editing to reproduce alternative scenarios (and uploading relevant data into "data/" folder)

Reproduce Paper Figures:
After running run_pipeline.py, figures used in the paper are automatically generated in:
1. Seasonal time series (Fig.2):
- case_study_sim/results/sim/
1.1 load_pv_net_jan_2w.png
1.2 load_pv_net_jul_2w.png
1.3 soc_jan_2w.png
1.4 soc_jul_2w.png
1.5 unserved_jan_2w.png
1.6 unserved_jul_2w.png
  
2. Risk curves (Fig. 3):
- case_study_sim/results/risk_curves/
2.1 risk_index_cdf.png
2.2 risk_index_exceedance.png
2.3 unserved_cdf.png
2.4 unserved_exceedance.png
  
3. Explainability (Fig. 4):
- case_study_sim/results/xai/
3.1 shap_beeswarm.png
3.2 shap_summary_bar.png

Data Availability:
This repository contains the full simulation pipeline and example input configuration.

The dataset used for the conference paper reproduction are publicly available: 
- Load data: NREL End-Use Load Profiles (OEDI)
- PV generation: PVGIS

Due to size, datasets are excluded from this repository. The sources to access and download the data are provided in the paper under the references [25] for load and [27] for PV (the PV data was fetched from Utqiagvik, Alaska with coordinates 71.2906 N latitude and 156.7886 W longitude)

License:
This project is under the MIT License

Citation:
If you use this repository, please cite:
"S. Klyuyev and M. Nassereddine, “Predictive Stability Risk Assessment Pipeline for Islanded PV-BESS Microgrids (Version 1.0.0),” Zenodo, Feb. 15, 2026. [Online]. Available: https://doi.org/10.5281/zenodo.18649192"
