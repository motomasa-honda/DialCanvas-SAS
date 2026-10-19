#!/usr/bin/env python3
"""Compile and simulate the exact SHA-pinned product wave-drive controller on host."""
import hashlib
import subprocess
import tarfile
import tempfile
from pathlib import Path

from motor_feasibility import PRODUCT_ARCHIVE, PRODUCT_ARCHIVE_SHA256, firmware_wave_drive_screen

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).with_name("wave_drive_product_host.c")
MEMBERS = ("firmware/main/control.c", "firmware/main/control.h")


def main():
    payload = PRODUCT_ARCHIVE.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == PRODUCT_ARCHIVE_SHA256
    screen = firmware_wave_drive_screen()
    assert screen["mode"] == "ONE_HOT_WAVE_DRIVE_ONE_PHASE_PER_AXIS"
    assert screen["period_us"] == [31250, 38462, 33333, 45455, 35714, 41667, 50000]
    assert screen["all_candidate_speeds_below_supplier_5v_guidance_6rpm"]

    with tempfile.TemporaryDirectory(prefix="fg-wave-drive-") as temp:
        root = Path(temp)
        with tarfile.open(PRODUCT_ARCHIVE, "r:gz") as archive:
            for member in MEMBERS:
                data = archive.extractfile(member)
                assert data is not None
                target = root / Path(member).name
                target.write_bytes(data.read())
        executable = root / "wave_drive_test"
        subprocess.run([
            "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(root), str(HARNESS), str(root / "control.c"),
            "-o", str(executable),
        ], check=True)
        result = subprocess.run([str(executable)], check=True, text=True, capture_output=True)
        print(result.stdout, end="")


if __name__ == "__main__":
    main()
