import subprocess
import sys
from pathlib import Path

SCRIPT_ORDER = [
    "convert_resstock.py",
    "prepare_load.py",
    "prepare_pv.py",
    "scale_load.py",
]

def run_step(script_path: Path) -> None:
    print(f"Running: {script_path.name}")
    subprocess.run([sys.executable, str(script_path)], check=True)
    print(f"Completed: {script_path.name}")

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    preprocessing_dir = project_root / "scripts" / "preprocessing"

    if not preprocessing_dir.exists():
        raise FileNotFoundError(f"Preprocessing folder not found: {preprocessing_dir}")

    for script_name in SCRIPT_ORDER:
        script_path = preprocessing_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Missing preprocessing script: {script_path}")
        run_step(script_path)

    print("All preprocessing steps finished!")
    print(f"Processed outputs are now in: {project_root / 'data' / 'processed'}")

if __name__ == "__main__":
    main()