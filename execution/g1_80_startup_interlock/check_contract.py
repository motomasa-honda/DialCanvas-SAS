#!/usr/bin/env python3
"""Preflight entry: static physical boundary audit plus G1-80 14 test cases."""
from pathlib import Path
import subprocess
import sys
here = Path(__file__).resolve().parent
for cmd in [
    [sys.executable, str(here / "net_guard.py")],
    [sys.executable, "-m", "unittest", "discover", "-s", str(here), "-p", "test_controller.py", "-v"],
]:
    if subprocess.run(cmd, check=False).returncode:
        raise SystemExit("FAIL G1-80 review tests")
print("PASS G1-80 model review; NEVER hardware or manufacturing signoff")
