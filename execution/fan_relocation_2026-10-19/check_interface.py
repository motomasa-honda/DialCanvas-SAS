#!/usr/bin/env python3
"""Validate source-derived fan interface facts and prevent premature release claims."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "interface_contract.json").read_text(encoding="utf-8"))
GEOMETRY = json.loads((ROOT / "evidence/candidate_source_audit.json").read_text(encoding="utf-8"))

def check() -> None:
    assert DATA["status"] == "PROVISIONAL_SCREENING_INTERFACE_NOT_FABRICATION_RELEASE"
    assert DATA["source"]["document"] == "DC Fan catalog 2026-02-10 (255-E)"
    rated = DATA["manufacturer_rated_data"]
    assert (rated["supply_vdc"], rated["rated_current_ma"]) == (5, 45)
    mech = DATA["manufacturer_mechanical_interface_mm"]
    assert (mech["body_w"], mech["body_h"], mech["depth"]) == (30, 30, 10)
    assert mech["mount_hole_count"] == 3
    assert (mech["mount_hole_diameter_nominal"], mech["mount_pitch_nominal"]) == (3.2, 24)
    integration = DATA["candidate_integration"]
    geom = GEOMETRY["candidate"]
    assert integration["site_xy_mm"] == geom["center_xy_mm"]
    assert integration["wood_port_diameter_nominal_mm"] == geom["backwood_vent_diameter_mm"]
    # External adapter-to-wood supports are four points; they are distinct from three fan holes.
    assert integration["wood_adapter_support_count"] == 4
    assert integration["fan_mount_hole_centers"] is None
    assert "NOT_RELEASED" in integration["fan_mount_hole_layout_status"]
    plate_half = integration["wood_adapter_nominal_mm"][0] / 2
    support_offset = max(abs(v) for p in integration["wood_adapter_support_pattern_relative_mm"] for v in p)
    assert abs((plate_half - support_offset) - integration["nominal_adapter_edge_distance_at_support_center_mm"]) < 1e-9
    # The nominal wood opening equals the fan inlet diameter: this is not machining clearance.
    assert integration["nominal_port_to_fan_inlet_diameter_difference_mm"] == 0
    assert integration["wood_port_tolerance_mm"] is None
    unknowns = " ".join(DATA["explicit_unknowns"])
    assert "startup" in unknowns and "tolerance" in unknowns and "guard" in unknowns
    release = DATA["release_state"]
    assert release["purchase"] is False and release["cut"] is False and release["power"] is False
    assert release["motor_efuse_en"] == "LOW" and release["manufacturing_gates_closed"] == 0
    assert GEOMETRY["release"]["G3_06"] == "OPEN"
    print("PASS: official-rated/interface dimensions are traced; 3 fan holes cannot be confused with 4 wood supports")
    print("HOLD: exact fan-hole coordinates, wood-port fit, wiring termination, startup/stall and thermal tests remain open")

if __name__ == "__main__":
    check()
