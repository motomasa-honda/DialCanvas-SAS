#!/usr/bin/env python3
"""Check a motor datum plate candidate against source drawing and reservation dimensions."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = json.loads((HERE / "cad_evidence.json").read_text(encoding="utf-8"))
reserve = source["within_project_reserved_axis_envelope_mm"]
motor = source["motor_mechanical_drawing"]
plate = [48.0, 39.0]
spacing = motor["mounting_hole_center_distance_mm"]
spacing_nominal = float(spacing["nominal"])
spacing_tol = float(spacing["tolerance"])
hole_max = float(motor["mounting_holes"]["diameter_mm"]["nominal"]) + float(motor["mounting_holes"]["diameter_mm"]["tolerance"])
boss_max = float(motor["shaft_boss_diameter_mm"]["nominal"]) + float(motor["shaft_boss_diameter_mm"]["tolerance"])
body_max = float(motor["body_diameter_mm"]["nominal"]) + float(motor["body_diameter_mm"]["tolerance"])
slot_width = 4.8
slot_half_travel = 0.4
boss_opening = 10.0
assert plate[0] <= reserve["x"] and plate[1] <= reserve["y"]
assert spacing_tol <= slot_half_travel
assert slot_width > hole_max
assert boss_opening > boss_max
assert min((plate[0] - spacing_nominal - 2*slot_half_travel - slot_width)/2,
           (plate[1] - body_max)/2) > 0
# The board and motor are separate overlapping XY projections; this is deliberately a HOLD.
board = source["nominal_pcb_envelope_mm"]
assert board["x"] == 35.0 and board["y"] == 19.3
assert board["x"] <= plate[0] and board["y"] <= plate[1]
result = {
    "status": "MOTOR_DATUM_PLATE_CANDIDATE_ONLY",
    "source": "cad_evidence.json; Seeed motor drawing and EAGLE board outline",
    "plate_xy_mm": plate,
    "reservation_xy_mm": [reserve["x"], reserve["y"]],
    "reservation_margin_each_side_mm": [(reserve["x"]-plate[0])/2, (reserve["y"]-plate[1])/2],
    "motor_hole_spacing_drawing_mm": [spacing_nominal-spacing_tol, spacing_nominal+spacing_tol],
    "slot_center_spacing_adjustment_mm": [-slot_half_travel, slot_half_travel],
    "candidate_slot_width_mm": slot_width,
    "motor_hole_diameter_max_from_drawing_mm": hole_max,
    "boss_opening_candidate_mm": boss_opening,
    "motor_boss_diameter_max_from_drawing_mm": boss_max,
    "body_diameter_max_from_drawing_mm": body_max,
    "edge_margin_after_slot_envelope_mm": (plate[0]-spacing_nominal-2*slot_half_travel-slot_width)/2,
    "board_outline_xy_mm": [board["x"], board["y"]],
    "board_plan_fits_plate": True,
    "board_motor_xy_overlap": True,
    "board_retention": "NOT_DESIGNED; source board has no mounting holes",
    "stacking_and_clearance": "HOLD: motor depth, shaft projection, board component height, cable and fastening Z stack are not integrated",
    "fastener_and_material": "HOLD: slot width is a geometric candidate; fastener, washer, plate material, thickness, process and strength are not selected or qualified",
    "d7_clearance_55mm": "NOT_RECOMPUTED; this local plate screen is not full-assembly geometry",
    "manufacturing_release": False,
}
(HERE / "mount_candidate_screen.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("PASS: candidate 48 x 39 mm motor plate fits within each 50 x 41 mm axis reservation")
print("PASS: 4.8 mm slots cover 35 +/- 0.2 mm motor-hole spacing; boss opening clears drawing maximum")
print("HOLD: driver PCB overlaps the motor in XY; Z stack, retention, fasteners, D7 sweep and physical fit remain open")
