#!/usr/bin/env python3
"""Evidence-gated 7-axis motor current feasibility, WITHOUT manufacturing permission.

This outputs a set of hypothetical screening envelopes, NOT measured current,
a proven eFuse minimum, a resolved SKU or permission to enable any motor.
"""
import argparse
import hashlib
import json
import math
import re
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CURRENT = HERE / "motor_current_acceptance.json"
SOURCE = ROOT / "execution/bom_reconciled_2026-10-16/source_contract.json"
PRODUCT_ARCHIVE = ROOT / "phase67-source/firmware.tar.gz"
PRODUCT_ARCHIVE_SHA256 = "a245ac0da5ad690509a651b2872cc9eb163f0718875a8f238527246f5fdccba3"
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


def firmware_wave_drive_screen():
    """Extract the SHA-pinned product controller's phase cadence, never execute hardware."""
    digest = hashlib.sha256(PRODUCT_ARCHIVE.read_bytes()).hexdigest()
    if digest != PRODUCT_ARCHIVE_SHA256:
        raise ValueError("ESP32-P4 product firmware archive SHA changed; review the new source before screening")
    with tarfile.open(PRODUCT_ARCHIVE, "r:gz") as archive:
        source = archive.extractfile("firmware/main/control.c")
        if source is None:
            raise ValueError("pinned product archive lacks firmware/main/control.c")
        control = source.read().decode("utf-8")
    period_match = re.search(r"period_us\[7\]\s*=\s*\{([^}]+)\}", control)
    direction_match = re.search(r"direction\[7\]\s*=\s*\{([^}]+)\}", control)
    if not period_match or not direction_match:
        raise ValueError("cannot derive seven-axis timing/direction from product controller")
    periods = [int(x.strip()) for x in period_match.group(1).split(",") if x.strip()]
    directions = [int(x.strip()) for x in direction_match.group(1).split(",") if x.strip()]
    one_hot = "c->phase[i]=(uint8_t)(1u<<c->phase_index[i])" in control
    if len(periods) != 7 or len(directions) != 7 or not one_hot:
        raise ValueError("product controller is no longer the expected seven-axis one-hot sequencer")
    steps_s = [round(1_000_000 / period, 6) for period in periods]
    output_rpm = [round(rate * 60 / 516, 6) for rate in steps_s]
    return {
        "source_archive_sha256": digest,
        "mode": "ONE_HOT_WAVE_DRIVE_ONE_PHASE_PER_AXIS",
        "period_us": periods,
        "direction_sign_by_axis": directions,
        "steps_per_second_by_axis": steps_s,
        "candidate_516_step_output_rpm_by_axis": output_rpm,
        "all_candidate_speeds_below_supplier_5v_guidance_6rpm": max(output_rpm) < 6,
        "logical_28_phase_interface_review": "ONE_PHASE_LINE_PER_AXIS_IS_COMPATIBLE; DRIVER_BOARD_INPUT_AND_COMMON_PIN_SAMPLE_UNVERIFIED",
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
    wave_drive = firmware_wave_drive_screen()
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
        "conditional_supplier_motor_candidate": {
            "status": "SHORTLIST_FOR_SAMPLE_QUALIFICATION_ONLY",
            "supplier": "Adafruit",
            "supplier_product_id": "858",
            "source": "https://www.adafruit.com/product/858",
            "source_class": "SELLER_CATALOG; OEM_MANUFACTURER_NOT_IDENTIFIED",
            "listed_supply_v": 5,
            "listed_connection": "5-pin unipolar",
            "listed_reduction_ratio": 16.128,
            "listed_steps_per_output_revolution": 516,
            "listed_speed_guidance_rpm": "under 6 at 5V",
            "listed_envelope_mm": {"diameter": 28, "body_height": 20, "shaft_length": 9, "shaft_diameter": 5},
            "listed_holding_torque_nmm": 15,
            "approx_winding_resistance_ohm": 42,
            "winding_resistance_tolerance": "NOT_PUBLISHED",
            "one_phase_ohmic_current_estimate_per_axis_a": round(5 / 42, 6),
            "seven_axis_one_phase_ohmic_current_estimate_a": round(7 * 5 / 42, 6),
            "one_phase_required_guaranteed_efuse_min_a_exclusive_for_20pct_reserve": round((7 * 5 / 42) / (1 - RESERVE), 6),
            "seven_axis_two_phase_ohmic_current_estimate_a": round(7 * 2 * 5 / 42, 6),
            "two_phase_result_vs_current_efuse_typical": "EXCEEDS_1.509A_TYPICAL_BEFORE_MARGIN",
            "one_phase_result_vs_current_efuse_typical": "WITHIN_20PCT_TYPICAL_SCREEN_ONLY; GUARANTEED_MIN_UNKNOWN",
            "firmware_wave_drive_screen": wave_drive,
            "selected_for_production": False,
            "hardware_release": False,
            "remaining_qualification": [
                "Confirm current product revision, OEM identity, and orderable supply continuity",
                "Measure winding resistance and energized current on received samples across coil sequence and supply tolerance",
                "Prove one-phase stepping has adequate torque/start reliability for the actual seven gear trains",
                "Verify enclosure fit, mounting holes, shaft coupling, backlash, noise, and thermal rise",
                "Obtain applicable guaranteed minimum eFuse limit and run instrumented startup/stall/STOP HIL",
            ],
        },
        "audited_manufacturer_motor_candidate": {
            "status": "REJECTED_FOR_CURRENT_M1_DRIVER_AND_POWER_ENVELOPE",
            "manufacturer": "Oriental Motor",
            "exact_order_code": "PKP223U09A2",
            "source": "https://catalog.orientalmotor.com/item/2-phase-unipolar-stepper-motors/shop-pkp-series-2-phase-unipolar-stepper-motors/pkp223u09a2",
            "listed_frame_mm": 28,
            "listed_motor_length_mm": 32,
            "listed_leads": 6,
            "listed_winding_current_a_per_phase": 0.95,
            "listed_winding_resistance_ohm_per_phase": 3.11,
            "listed_motor_voltage_v": 2.95,
            "gearhead": "NONE",
            "seven_axes_two_phases_theoretical_current_a": round(AXES * 2 * 0.95, 2),
            "rejection_reasons": [
                "0.95A/phase exceeds the ULN2003A 0.5A/channel rating used by the candidate driver topology",
                "13.3A for seven axes at two phases each exceeds the current eFuse typical 1.509A by a wide margin",
                "Exact SKU has no gearhead and is not a drop-in mechanical replacement",
            ],
            "selected": False,
            "source_is_manufacturer_sales_catalog_not_independent_measurement": True,
        },
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
