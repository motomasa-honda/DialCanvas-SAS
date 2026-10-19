#!/usr/bin/env python3
"""Complete load accounting for a module-first candidate; never an enable path."""
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def positive(value, name, allow_zero=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name}: finite number required")
    if value < 0 or (not allow_zero and value == 0):
        raise ValueError(f"{name}: invalid sign")
    return value


def estimate(data):
    """Catalog arithmetic is separated from guaranteed/physical acceptance."""
    s = data["screening"]
    reserve = positive(s["reserve_fraction"], "reserve")
    if reserve >= 1:
        raise ValueError("reserve must be below one")
    for k in ("motor_axes", "phases_per_axis", "led_count", "leds_per_metre"):
        if type(s[k]) is not int or s[k] <= 0:
            raise ValueError(f"{k}: positive integer required")
    if s["motor_axes"] != 7 or s["phases_per_axis"] != 1:
        raise ValueError("Candidate is seven-axis one-hot; other modes need a separate review")
    winding = positive(s["motor_winding_resistance_ohm"], "winding")
    winding_tol = positive(s["motor_winding_resistance_tolerance_fraction"], "winding tolerance", allow_zero=True)
    if winding_tol >= 1:
        raise ValueError("winding tolerance must be below one")
    motor_phase_nominal_a = s["motor_nominal_v"] / winding
    motor = s["motor_axes"] * s["phases_per_axis"] * motor_phase_nominal_a
    motor_voltage_upper_v = (positive(s["motor_nominal_v"], "motor nominal voltage")
                             * (1 + positive(data["adapter"]["voltage_tolerance_fraction"], "source voltage tolerance", allow_zero=True)))
    motor_phase_upper_a = (motor_voltage_upper_v
                           / (winding * (1 - winding_tol)))
    motor_upper_by_phase_count = {
        str(phases): s["motor_axes"] * phases * motor_phase_upper_a
        for phases in (1, 2)
    }
    led_metres = s["led_count"] / s["leds_per_metre"]
    led_w = led_metres * positive(s["led_catalog_max_w_per_metre_at_5v"], "led power")
    led_a = led_w / 5.0
    fan = positive(s["fan_rated_a_not_peak"], "fan")
    subtotal = motor + led_a + fan
    converter = data["converter"]
    v = positive(converter["rated_v"], "aon rated voltage")
    accuracy = positive(converter["output_accuracy_fraction"], "aon accuracy")
    return {
        "basis": "5V_CATALOG_SCREEN_NOT_MEASURED_NOT_WORST_CASE",
        "motor_coil_ohmic_estimate_a": motor,
        "motor_phase_current_nominal_a": motor_phase_nominal_a,
        "motor_voltage_upper_v_from_adapter_tolerance": motor_voltage_upper_v,
        "motor_phase_current_upper_bound_a": motor_phase_upper_a,
        "motor_all_axes_upper_bound_by_phases_a": motor_upper_by_phase_count,
        "led_length_total_m": led_metres,
        "led_power_length_estimate_w": led_w,
        "led_current_length_estimate_a": led_a,
        "fan_rated_a_not_peak": fan,
        "partial_catalog_subtotal_a": subtotal,
        "source_comparison": [
            {"source_rated_a": positive(a, "source current"),
             "load_ceiling_with_reserve_a": a * (1 - reserve),
             "remaining_for_all_unknowns_a": a * (1 - reserve) - subtotal,
             "status": "HEADROOM_ARITHMETIC_ONLY_NO_SOURCE_ACCEPTANCE"}
            for a in s["source_alternatives_a"]
        ],
        "aon_voltage_accuracy_interval_v": [v * (1 - accuracy), v * (1 + accuracy)],
        "aon_catalog_20pct_screen_ceiling_a_not_guaranteed": converter["catalog_max_continuous_a_thermal_dependent"] * (1 - reserve),
        "missing": sorted(k for k, v in data["unmeasured"].items() if v is None),
        "decision": "HOLD_UNMEASURED_LOADS_AND_INPUT_PATH",
        "hardware_release": False
    }


def evaluate_bounds(data, *, source_min_a, raw_min_v, aon_max_v,
                    aon_qualified_a, efuse_min_a, bounds):
    """Numeric review for independently supplied bounds, NOT evidence intake.

    CLI does not expose this function as a measurement-entry route. Provenance,
    real protection ratings and physical acceptance must be reviewed separately.
    """
    expected = set(data["unmeasured"])
    if set(bounds) != expected:
        raise ValueError("all load and transient bounds must be supplied explicitly")
    missing = sorted(k for k, v in bounds.items() if v is None)
    if missing:
        return {"decision": "HOLD_MISSING_BOUNDS", "missing": missing, "hardware_release": False}
    for k, v in bounds.items():
        positive(v, k, allow_zero=k in {"seven_driver_board_overhead_5v_peak_a", "other_raw_5v_peak_a"})
    for k, v in dict(source_min_a=source_min_a, raw_min_v=raw_min_v, aon_max_v=aon_max_v,
                     aon_qualified_a=aon_qualified_a, efuse_min_a=efuse_min_a).items():
        positive(v, k)
    eta = bounds["aon_min_efficiency"]
    if eta > 1:
        raise ValueError("efficiency cannot exceed one")
    # Use the smaller independently applicable path/part limit. The caller's
    # source bound may never override a known smaller jack/harness limit.
    path_limit = data["adapter"]["qualified_harness_current_a"]
    if path_limit is None or data["adapter"]["jack_part"] is None:
        return {"decision": "HOLD_INPUT_PATH_UNQUALIFIED", "hardware_release": False}
    capacity = min(source_min_a, positive(path_limit, "path limit"), data["adapter"]["rated_a"])
    raw_window = data["qualified_raw_voltage_window_v"]
    aon_window = data["converter"]["qualified_output_window_v"]
    converter_min_v = data["converter"]["qualified_input_min_v"]
    if raw_window is None or aon_window is None or converter_min_v is None:
        return {"decision": "HOLD_VOLTAGE_COMPATIBILITY_UNQUALIFIED", "hardware_release": False}
    raw_low = min(raw_min_v, bounds["minimum_raw_voltage_during_transient_v"])
    raw_high = bounds["maximum_source_voltage_including_transient_v"]
    acon = data["converter"]
    aon_low = acon["rated_v"] * (1 - acon["output_accuracy_fraction"])
    aon_high = max(aon_max_v, acon["rated_v"] * (1 + acon["output_accuracy_fraction"]))
    adapter_low = data["adapter"]["rated_v"] * (1 - data["adapter"]["voltage_tolerance_fraction"])
    adapter_high = data["adapter"]["rated_v"] * (1 + data["adapter"]["voltage_tolerance_fraction"])
    if (raw_low < max(raw_window[0], converter_min_v) or raw_high > raw_window[1]
            or adapter_low < raw_window[0] or adapter_high > raw_window[1]
            or aon_low < aon_window[0] or aon_high > aon_window[1]):
        return {"decision": "FAIL_VOLTAGE_COMPATIBILITY", "hardware_release": False}
    reserve = data["screening"]["reserve_fraction"]
    motor = bounds["motor_total_peak_a"]
    aon = bounds["external_aon_total_3v3_peak_a"]
    five_v = (bounds["waveshare_total_5v_peak_a"] + bounds["seven_driver_board_overhead_5v_peak_a"]
              + motor + bounds["lighting_total_peak_a"] + bounds["fan_start_stall_peak_a"]
              + bounds["other_raw_5v_peak_a"])
    calculated = five_v + aon_high * aon / (raw_low * eta)
    required = max(calculated, bounds["measured_total_input_peak_a"])
    if motor >= min(efuse_min_a, bounds["efuse_guaranteed_min_limit_a"]) * (1 - reserve):
        decision = "FAIL_MOTOR_LIMIT_MARGIN"
    elif aon >= min(aon_qualified_a, data["converter"]["catalog_max_continuous_a_thermal_dependent"]) * (1 - reserve):
        decision = "FAIL_AON_LIMIT_MARGIN"
    elif required >= capacity * (1 - reserve):
        decision = "FAIL_INPUT_LIMIT_MARGIN"
    else:
        decision = "CONDITIONAL_NUMERIC_SCREEN_ONLY"
    return {"decision": decision, "calculated_input_a": calculated,
            "required_input_a": required, "path_capacity_a": capacity,
            "hardware_release": False,
            "remaining": "Voltage compatibility/dropout, reverse feed, transient limits, source provenance and physical fault tests remain required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = estimate(json.loads((HERE / "components.json").read_text()))
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        print(f"WROTE {args.output}: {report['decision']}")
    else:
        print(text)


if __name__ == "__main__":
    main()
