#!/usr/bin/env python3
"""Preflight registered G1-79 checks, not physical safety certification."""
from pathlib import Path
import subprocess
import sys
here = Path(__file__).resolve().parent
for cmd in [
    [sys.executable, str(here / "screen.py")],
    [sys.executable, "-m", "unittest", "discover", "-s", str(here), "-p", "test_screen.py", "-v"],
]:
    if subprocess.run(cmd, check=False).returncode:
        raise SystemExit("FAIL G1-79 quantitative hold screen")
print("PASS G1-79 review, HOLD real motor module VIL/leakage/HIL")
