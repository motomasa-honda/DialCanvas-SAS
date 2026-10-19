#!/usr/bin/env python3
"""Validate USB-C candidate provenance and fail-closed release assumptions."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
candidate = json.loads((D / "usb_c_sink_candidate.json").read_text(encoding="utf-8"))
assert candidate["scope"] == "G1-05 USB-C 5V input controller candidate; review only"
assert candidate["status"] == "PROVISIONAL_DESIGN_CANDIDATE"
assert candidate["manufacturing_release"] is False
assert candidate["purchase_authorized"] is False
assert candidate["motor_power_enabled"] is False
assert candidate["manufacturer_release_gates_closed"] == 0
c = candidate["candidate"]
assert c["order_code"] == "STUSB4500LQTR"
assert c["package"] == "QFN-24 EP (4x4 mm)"
assert c["manufacturer_marketing_status"] == "Active"
assert c["maximum_supported_input"] == {"voltage_v": 5, "current_a": 3, "power_w": 15}
assert c["source_current_advertisements_detected"] == ["default", "1.5A", "3A"]
assert c["source_current_is_detected_not_limited"] is True
assert c["external_vbus_path_switch_required"] is True
assert c["usb_pd_higher_voltage_request"] is False
assert candidate["source_documents"]["datasheet"].endswith("stusb4500l.pdf")
assert candidate["source_documents"]["product_page"].startswith("https://www.st.com/")
assert all(v is None for v in candidate["unresolved_design_inputs"].values())
acceptance = json.loads((D / "motor_current_acceptance.json").read_text(encoding="utf-8"))
for key in ("motor_sku", "efuse_min_current_limit_a", "five_volt_supply_sku",
            "five_volt_supply_min_current_a", "board_measured_peak_input_a"):
    assert acceptance["unverified_field_values"][key] is None, key
assert acceptance["hardware_release"] is False
print("PASS USB-C source candidate is evidence-backed, 5V-only, and remains non-limiting/non-release; all supply/current inputs HOLD")
