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
assert candidate["source_documents"]["mosfet_datasheet"].endswith("stl9p3llh6.pdf")
receptacle = candidate["receptacle_candidate"]
assert receptacle["manufacturer"] == "Global Connector Technology (GCT)"
assert receptacle["series"] == "USB4105"
assert receptacle["candidate_order_code"] == "USB4105-GF-A-120"
assert receptacle["status"] == "PROVISIONAL_MECHANICAL_CANDIDATE_NOT_RELEASED"
assert receptacle["manufacturer_page_status"] == "Active"
assert receptacle["interface"] == "USB Type-C receptacle, USB 2.0, 16 contacts"
assert receptacle["mounting"] == "Horizontal, side-entry, top-mount SMT; shell stakes through-hole"
assert receptacle["profile_mm"] == 3.31
assert receptacle["mating_cycles"] == 20000
assert receptacle["contact_current_ratings"] == {
    "vbus_collective_a": 5.0, "gnd_collective_a": 6.25,
    "b5_vconn_a": 1.25, "other_contact_per_pin_a": 0.25,
}
assert "USB4105-GF-A-120" in receptacle["order_code_options_as_listed_by_manufacturer"]
assert receptacle["source"] == candidate["source_documents"]["receptacle_manufacturer_page"]
assert "not a production selection" in receptacle["selection_boundary"].lower()
assert "BLOCKED" in candidate["unresolved_design_inputs"]["type_c_receptacle_pin_and_footprint_drawing_review"]
pin_map = candidate["manufacturer_pin_map"]
assert pin_map["source"].startswith("ST DS13102 Rev 6, Figure 2/Table 1")
assert pin_map["footprint_selection"] == "NOT_SELECTED"
assert pin_map["net_assignment"].startswith("NOT_DESIGNED")
expected_pin_map = {
    "1": "CC1DB", "2": "CC1", "3": "NU", "4": "CC2", "5": "CC2DB",
    "6": "RESET", "7": "SCL", "8": "SDA", "9": "DISCH", "10": "GND",
    "11": "ATTACH", "12": "ADDR0", "13": "ADDR1", "14": "RP_1A5",
    "15": "GPIO", "16": "VBUS_EN_SNK", "17": "A_B_SIDE",
    "18": "VBUS_VS_DISCH", "19": "ALERT", "20": "RP_3A",
    "21": "VREG_1V2", "22": "VSYS", "23": "VREG_2V7", "24": "VDD",
    "EP": "GND",
}
assert pin_map["pins"] == expected_pin_map, "STUSB4500L QFN-24 EP pin mapping drifted"
fet = candidate["external_pmos_candidate"]
assert fet["order_code"] == "STL9P3LLH6"
assert fet["manufacturer_pin_map"] == {
    "1": "S", "2": "S", "3": "S", "4": "G",
    "5": "D", "6": "D", "7": "D", "8": "D",
}
assert fet["datasheet_claims"] == {"vds_v": -30, "rds_on_max_ohm": 0.015, "id_a": -9}
assert "not a usable board current" in fet["claims_scope"]
unresolved = candidate["unresolved_design_inputs"]
for key in ("type_c_receptacle_mpn", "external_pmos_mpn_and_safe_operating_area",
            "vbus_tvs_and_connector_esd_selection", "adapter_sku_and_guaranteed_rating",
            "actual_board_max_input_current", "rp_current_to_motor_permission_hardware_logic",
            "motor_sku_and_measured_current", "thermal_and_hil_evidence"):
    assert unresolved[key] is None, key
assert unresolved["usb_c_sink_pin_net_assignment"].startswith("NOT_DESIGNED")
assert unresolved["complete_usb_c_input_schematic_and_native_erc"] is None
assert unresolved["pcb_footprint_and_layout"] is None
acceptance = json.loads((D / "motor_current_acceptance.json").read_text(encoding="utf-8"))
for key in ("motor_sku", "efuse_min_current_limit_a", "five_volt_supply_sku",
            "five_volt_supply_min_current_a", "board_measured_peak_input_a"):
    assert acceptance["unverified_field_values"][key] is None, key
assert acceptance["hardware_release"] is False
print("PASS USB-C review contract: exact 25-pad ST pin map + 8-pad P-MOS map; no netlist/footprint/current/safety release implied")
