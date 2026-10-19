#!/usr/bin/env python3
"""Pre-commit fail-closed CI preflight. No hardware calls, no network, no build/power."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
checks = [
    "execution/guard.py",
    "execution/bom_reconciled_2026-10-16/check_contract.py",
    "execution/g6_02_7panel_2026-10-16/check_contract.py",
    "execution/g6_03_80_source_faces/check_contract.py",
    "execution/g6_06_build_service_sequence/check_contract.py",
    "execution/g5_05_access_core/check_contract.py",
    "execution/g5_05_https_api/check_contract.py",
    "execution/g5_05_hosted_network/check_contract.py",
    "execution/g5_05_secure_partition/check_partition.py",
    "execution/g5_06_signed_ota/check_contract.py",
    "execution/g5_frame_2026-10-16/check_contract.py",
    "execution/g5_fivepiece_2026-10-16/check_contract.py",
    "execution/g5_jig_g604_2026-10-16/check_contract.py",
    "execution/fan_full_thickness_2026-10-16/check_contract.py",
    "execution/g1_interlock_2026-10-16/check_contract.py",
    "execution/g1_phase77_140pins/check_contract.py",
    "execution/g1_28phase_disabled/check_contract.py",
    "execution/g1_79_output_low_screen/check_contract.py",
    "execution/g1_80_startup_interlock/check_contract.py",
    "execution/g1_81_rail_supervisor/check_contract.py",
    "execution/g1_82_integrated_review/check_integrated.py",
    "execution/g1_85_efuse_analog/check_contract.py",
    "execution/g4_03_passive_selection_2026-10-19/check_contract.py",
    "execution/g1_95_aon_regulator/check_efuse_accuracy_audit.py",
    "execution/g1_95_aon_regulator/check_motor_current_budget.py",
    "execution/g1_95_aon_regulator/check_usb_c_sink_candidate.py",
    "execution/g1_95_aon_regulator/test_input_power_consistency.py",
    "execution/g1_95_aon_regulator/test_motor_feasibility.py",
    "execution/g1_95_aon_regulator/test_wave_drive_product.py",
    "execution/g1_86_fault_latch/check_contract.py",
    "execution/g1_87_rearm_release/check_contract.py",
    "execution/cassettes/check_manifest.py",
    "execution/bracket_chassis_2026-10-16/check_contract.py",
    "execution/anchor_lock_2026-10-16/check_contract.py",
    "execution/bayonet_2026-10-16/check_motion.py",
    "execution/secondary_keeper_2026-10-16/check_motion.py",
]
for script in checks:
    target = root / script
    if not target.is_file():
        print(f"FAIL missing required test: {script}", file=sys.stderr)
        sys.exit(2)
    print(f">>> {script}", flush=True)
    result = subprocess.run([sys.executable, str(target)], cwd=root, check=False)
    if result.returncode:
        print(f"FAIL {script} (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)
print(f"PASS: {len(checks)} mandatory review preflight checks; not native KiCad ERC, DRC, or hardware safety acceptance")
