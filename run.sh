#!/usr/bin/env bash
set -euo pipefail

# move to the project root
cd "$(dirname "$0")"

# prefer python3, fallback to python
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Error: Python is not installed or not in PATH."
  echo "Please install Python 3 and try again."
  exit 1
fi

echo "Using: $PYTHON_CMD"
echo "Forwarding args to runners/bootstrap_and_run.py: $*"

# forward all arguments exactly as provided
"$PYTHON_CMD" runners/bootstrap_and_run.py "$@"