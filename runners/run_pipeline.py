# Run the full microgrid risk pipeline in the correct order by executing this script
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_module(module: str):
    print(f"\n=== Running: {module} ===")
    subprocess.run(
        [sys.executable, "-m", module],
        cwd=str(ROOT),
        check=True
    )

def clean_outputs():
    targets = [
        ROOT / "results" / "sim",
        ROOT / "results" / "risk_curves",
        ROOT / "results" / "events",
        ROOT / "results" / "xai",
        ROOT / "figures",
    ]
    for t in targets:
        if t.exists():
            shutil.rmtree(t)
            print(f"Deleted: {t}")

def main():
    parser = argparse.ArgumentParser(description="Run full microgrid risk pipeline.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing outputs (results/* and figures/) before running."
    )
    args = parser.parse_args()

    if not (ROOT / "config.py").exists():
        raise FileNotFoundError(f"config.py not found in project root: {ROOT}")

    if not (ROOT / "scripts" / "__init__.py").exists():
        raise FileNotFoundError(
            "scripts/__init__.py missing. Create an empty scripts/__init__.py so '-m scripts.xxx' works."
        )

    if not (ROOT / "scripts" / "pipeline" / "__init__.py").exists():
        raise FileNotFoundError(
            "scripts/pipeline/__init__.py missing. Create an empty scripts/pipeline/__init__.py so '-m scripts.pipeline.xxx' works."
        )

    if args.clean:
        clean_outputs()

    run_module("scripts.pipeline.simulate_microgrid")
    run_module("scripts.pipeline.risk_curves")
    run_module("scripts.pipeline.event_examples")
    run_module("scripts.pipeline.shap_explain")
    run_module("scripts.pipeline.predictive_vs_reactive")
    run_module("scripts.pipeline.make_report")

    print("Pipeline finished successfully")
    print("Check outputs in:")
    print(" - results/sim/")
    print(" - results/risk_curves/")
    print(" - results/events/")
    print(" - results/xai/")

if __name__ == "__main__":
    main()