import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"

if os.name == "nt":
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"

def run(cmd, cwd=ROOT, title=None):
    if title:
        print(title)
    print(">", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=str(cwd), check=True)

def ensure_venv():
    if VENV_PYTHON.exists():
        print(f"virtual environment already exists: {VENV_DIR}")
        return

    print(f"creating virtual environment at: {VENV_DIR}")
    run([sys.executable, "-m", "venv", str(VENV_DIR)], title="creating virtual environment")

def install_requirements():
    req = ROOT / "requirements.txt"
    if not req.exists():
        raise FileNotFoundError(f"requirements.txt not found: {req}")

    # upgrade pip inside venv
    run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"], title="upgrading pip in venv")

    # install dependencies
    run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req)], title="installing requirements")

def run_all(
    clean: bool,
    skip_install: bool,
    skip_download: bool,
    force_download: bool,
    skip_preprocessing: bool,
):
    cmd = [str(VENV_PYTHON), str(ROOT / "runners" / "run_all.py")]

    if skip_install:
        cmd.append("--skip-install")
    if skip_download:
        cmd.append("--skip-download")
    if force_download:
        cmd.append("--force-download")
    if skip_preprocessing:
        cmd.append("--skip-preprocessing")
    if clean:
        cmd.append("--clean")

    run(cmd, title="running full pipeline (download + preprocess + simulation)")

def main():
    parser = argparse.ArgumentParser(description="Create venv, install requirements, and run the full pipeline.")
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip pip install -r requirements.txt inside the venv",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip downloading raw datasets",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Re-download raw datasets even if files already exist",
    )
    parser.add_argument(
        "--skip-preprocessing",
        action="store_true",
        help="Skip running preprocessing and go directly to the pipeline",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete previous outputs before running the pipeline",
    )
    args = parser.parse_args()

    print(f"Project root: {ROOT}")
    print(f"Bootstrap interpreter: {sys.executable}")

    ensure_venv()

    if not args.skip_install:
        install_requirements()
    else:
        print("dependency installation skipped (--skip-install)")

    run_all(
        clean=args.clean,
        skip_install=args.skip_install,
        skip_download=args.skip_download,
        force_download=args.force_download,
        skip_preprocessing=args.skip_preprocessing,
    )

    print("completed!")
    print("To manually use the environment later:")
    if os.name == "nt":
        print(r"  .venv\Scripts\activate")
    else:
        print("  source .venv/bin/activate")
    print("outputs:")
    print("results/sim/")
    print("results/risk_curves/")
    print("results/events/")
    print("results/xai/")

if __name__ == "__main__":
    main()