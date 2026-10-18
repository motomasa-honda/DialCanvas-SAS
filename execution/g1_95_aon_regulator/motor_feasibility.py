#!/usr/bin/env python3
"""Evidence-gated 7-axis motor current feasibility, WITHOUT manufacturing permission.

This outputs a set of hypothetical screening envelopes, NOT measured current,
a proven eFuse minimum, a resolved SKU or permission to enable any motor.
"""
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CURRENT = HERE / "motor_current_acceptance.json"
SOURCE = ROOT / "execution/bom_reconciled_2026-10-16/source_contract.json"
AXES = 7
RESERVE = .20
CASES_MA = (60, 80, 100, 160)
PHASES = (1, 2, 3, 4)


def positive_number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return float(value)


def size_candidate(phase_ma, simultaneous_phases, nominal_limit_a, manufacturer_min_a=None):
    """Never infer manufacturer minimum from nominal 3334/R.

    A manufacturer minimum may be supplied for CONDITIONAL screening, but
    physical-test evidence is checked elsewhere and remains indispensable.
    """
    phase = positive_number(phase_ma, "phase_ma")
    limit = positive_number(nominal_limit_a, "nominal_limit_a")
    if type(simultaneous_phases) is not int or simultaneous_phases not in PHASES:
        raise ValueError("simultaneous_phases must be integer in [1,4]")
    min_verified = None
    if manufacturer_min_a is not None:
        min_verified = positive_number(manufacturer_min_a, "manufacturer_min_a")
    total = AXES * simultaneous_phases * phase / 1000.0
    required_min = total / (1.0 - RESERVE)
    max_nominal_phase = limit * (1.0 - RESERVE) * 1000 / (AXES * simultaneous_phases)
    if total >= limit:
        verdict = "FAIL_EVEN_TYPICAL_EFUSE"
    elif total >= limit * (1.0 - RESERVE):
        verdict = "FAIL_NOMINAL_20PCT_MARGIN"
    elif min_verified is None:
        verdict = "HOLD_MANUFACTURER_MIN_UNVERIFIED"
    elif required_min >= min_verified:
        verdict = "FAIL_GUARANTEED_MIN_LIMIT_MARGIN"
    else:
        verdict = "CONDITIONAL_REQUIRES_PROVENANCE_AND_PHYSICAL_HIL"
    return {
        "axes": AXES,
        "simultaneous_phases_per_axis": simultaneous_phases,
        "hypothetical_phase_current_ma": phase,
        "total_motor_current_a": round(total, 6),
        "manufacturer_efuse_min_required_a_exclusive": round(required_min, 6),
        "current_efuse_nominal_limit_a_not_guaranteed": round(limit, 6),
        "max_phase_ma_from_typical_only_not_approved": round(max_nominal_phase, 4),
        "verdict": verdict,
        "hardware_release": False,
    }


def evaluate_report(current, source):
    assumed = current["assumptions"]
    if assumed["motor_axes"] != AXES or assumed["headroom_target_fraction"] != RESERVE:
        raise ValueError("Assumptions differ from approved G1-05 review baseline")
    assert current["hardware_release"] is False
    assert current["manufacturer_release_gates_closed"] == 0
    board = source["stepper_driver_boards"]
    skus = sorted([board["selected_candidate_sku"], board["other_candidate_sku"]])
    if skus != ["MTR-09-004", "MTR-09-024"] or board["category"].find("NOT a motor SKU") < 0:
        raise ValueError("Driver-board variant identity contract changed")
    if board["motor_model"] is not None or board["motor_electrical_values_verified"]:
        raise ValueError("A reseller board listing cannot fabricate motor identity/electrical acceptance")
    seller_motor = board["separate_seller_motor_listing"]
    if seller_motor["selected"] or seller_motor["listed_voltage_values_v"] != [5, 12] or seller_motor["listed_dc_resistance_ohm_values"] != [50, 200]:
        raise ValueError("Conflicting seller motor variants must remain unselected and electrically unqualified")
    r_ilm = positive_number(assumed["r_ilm_ohm"], "r_ilm_ohm")
    # 3334/R is only a typical and must not be adopted as a guaranteed limit.
    typical = 3334.0 / r_ilm
    measured = current["unverified_field_values"]
    min_a = measured.get("efuse_min_current_limit_a")
    if min_a is not None:
        positive_number(min_a, "efuse_min_current_limit_a")
    table = [size_candidate(i, p, typical, min_a) for p in PHASES for i in CASES_MA]
    missing = sorted(k for k, v in measured.items() if v is None)
    report = {
        "scope": "ENGINEERING_CANDIDATE_SCREEN_ONLY",
        "motor_identity_review": {
            "status": "HOLD_MOTOR_MODEL_AND_MANUFACTURER_UNIDENTIFIED",
            "candidate_motor_model_from_board_compatibility_only": "28BYJ-48",
            "candidate_is_selected": False,
            "motor_part_sku": None,
            "motor_electrical_rating": "UNVERIFIED",
            "action": "Identify one exact motor manufacturer/order code and qualify its voltage, winding/current, mechanical and supplier-lot data",
        },
        "driver_board_review": {
            "status": "SELLER_VARIANTS_IDENTIFIED_NOT_PHYSICALLY_QUALIFIED",
            "source": "execution/bom_reconciled_2026-10-16/source_contract.json",
            "seller_skus": skus,
            "m1_candidate_sku": board["selected_candidate_sku"],
            "listed_board_dimensions_mm": {"MTR-09-024": board["listed_mm"], "MTR-09-004": board["other_listed_mm"]},
            "physical_dimensions_verified": False,
            "action": "Treat MTR-09-024 and MTR-09-004 as different ULN2003 board variants; verify sample, connector, pinout and exact mounted envelope before BOM/CAD freeze",
        },
        "seller_motor_listing_review": {
            "status": "REJECTED_AS_ELECTRICAL_SOURCE_UNTIL_VARIANT_RESOLVED",
            "seller_sku": seller_motor["seller_sku"],
            "model_claim": seller_motor["model_claim"],
            "listed_voltage_values_v": seller_motor["listed_voltage_values_v"],
            "listed_dc_resistance_ohm_values": seller_motor["listed_dc_resistance_ohm_values"],
            "selected": False,
            "source": seller_motor["source"],
        },
        "current_model": {
            "efuse_r_ilm_ohm": r_ilm,
            "efuse_typical_a_NOT_manufacturer_min": round(typical, 6),
            "headroom_fraction": RESERVE,
            "axes": AXES,
            "rated_efuse_min_available": min_a is not None,
            "physical_evidence_missing_fields": missing,
        },
        "hypothetical_combinations": table,
        "decision": "HOLD_MOTOR_IDENTITY_AND_EFUSE_MIN_AND_PHYSICAL_ACCEPTANCE",
        "hardware_release": False,
        "manufacturer_release_gates_closed": 0,
        "notes": "Never infer measured or guaranteed currents from demo phase currents or eFuse typical formula; do not change EN/OE pull-down/disable circuits",
    }
    assert report["hardware_release"] is False
    assert len(table) == 16 and len(skus) == 2
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional path to write review JSON; no evidence fields changed")
    parser.add_argument("--phase-ma", type=float, help="Optional HYPOTHETICAL phase-current assumption")
    parser.add_argument("--phases", type=int, default=2, help="1-4 simultaneous phases per axis")
    args = parser.parse_args()
    if args.phase_ma is None and args.phases != 2:
        parser.error("--phases requires --phase-ma")
    current = json.loads(CURRENT.read_text())
    source = json.loads(SOURCE.read_text())
    report = evaluate_report(current, source)
    if args.phase_ma is not None:
        # CLI inputs are never accepted as measurements, SKU facts or release.
        m = report["current_model"]
        rated = current["unverified_field_values"]["efuse_min_current_limit_a"]
        report["one_hypothetical_input"] = size_candidate(
            args.phase_ma, args.phases, m["efuse_typical_a_NOT_manufacturer_min"], rated)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        print(f"WROTE conditional candidate matrix {p} (16 scenarios; NO HW RELEASE)")
    else:
        print(text)
    print("HOLD: motor part/electrical identity unresolved; driver-board samples unverified; eFuse minimum and 6 physical tests outstanding.")


if __name__ == "__main__":
    main()
