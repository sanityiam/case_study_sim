import argparse
import subprocess
import sys
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = ROOT / "data" / "raw"

LOAD_RAW_FILE = DATA_RAW_DIR / "resstock_building.parquet"
PV_RAW_FILE = DATA_RAW_DIR / "pvgis_seriescalc_utqiagvik_2018.csv"

LOAD_URL = (
    "https://oedi-data-lake.s3.amazonaws.com/"
    "nrel-pds-building-stock/"
    "end-use-load-profiles-for-us-building-stock/2022/"
    "resstock_amy2018_release_1.1/"
    "timeseries_individual_buildings/by_state/upgrade=2/state=WA/100025-2.parquet"
)

PV_URL = (
    "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
    "?lat=71.290556"
    "&lon=-156.788611"
    "&startyear=2018"
    "&endyear=2018"
    "&raddatabase=PVGIS-ERA5"
    "&pvcalculation=1"
    "&peakpower=1"
    "&loss=14"
    "&outputformat=csv"
    "&browser=1"
)

def run_cmd(cmd, title: str) -> None:
    print(f"{title}")
    print(f"command: {' '.join(map(str, cmd))}")
    subprocess.run(cmd, cwd=str(ROOT), check=True)

def ensure_dirs() -> None:
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, out_path: Path, force: bool = False) -> None:
    if out_path.exists() and not force:
        print(f"already exists: {out_path}")
        return
    print(f"download {url}")
    print(f"         -> {out_path}")
    urlretrieve(url, out_path)
    print(f"completed download: {out_path}")

def install_requirements() -> None:
    req = ROOT / "requirements.txt"
    if not req.exists():
        raise FileNotFoundError(f"requirements.txt not found: {req}")

    run_cmd(
        [sys.executable, "-m", "pip", "install", "-r", str(req)],
        "installing requirements",
    )

def main() -> None:
    parser = argparse.ArgumentParser(
        description="install deps, download data, preprocess, and run pipeline"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip pip install -r requirements.txt",
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
        help="Pass --clean to run_pipeline.py to delete previous outputs first",
    )

    args = parser.parse_args()

    print(f"project root: {ROOT}")
    print(f"python executable: {sys.executable}")

    ensure_dirs()

    if not args.skip_install:
        install_requirements()
    else:
        print("dependency installation skipped (--skip-install)")

    if not args.skip_download:
        download_file(LOAD_URL, LOAD_RAW_FILE, force=args.force_download)
        download_file(PV_URL, PV_RAW_FILE, force=args.force_download)
    else:
        print("data download skipped (--skip-download)")

    if not args.skip_preprocessing:
        run_cmd([sys.executable, str(ROOT / "runners" / "run_preprocessing.py")], "Running preprocessing")
    else:
        print("preprocessing skipped (--skip-preprocessing)")

    pipeline_cmd = [sys.executable, str(ROOT / "runners" / "run_pipeline.py")]
    if args.clean:
        pipeline_cmd.append("--clean")
    run_cmd(pipeline_cmd, "running simulation pipeline")

    print("done!")
    print("outputs:")
    print("results/sim/")
    print("results/risk_curves/")
    print("results/events/")
    print("results/xai/")

if __name__ == "__main__":
    main()