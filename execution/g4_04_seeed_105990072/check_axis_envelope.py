#!/usr/bin/env python3
"""Screen vendor motor and driver board plan envelopes against existing M1 reservations."""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "cad_evidence.json"
OUTPUT = HERE / "axis_envelope_screen.json"


def max_dimension(d: dict) -> float:
    return float(d["nominal"]) + float(d["tolerance"])


def margin(container: float, item: float) -> float:
    return (container - item) / 2


def main() -> None:
    e = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    motor = e["motor_mechanical_drawing"]
    board = e["nominal_pcb_envelope_mm"]
    hole_span = max_dimension(motor["mounting_hole_center_distance_mm"])
    hole_diameter = max_dimension(motor["mounting_holes"]["diameter_mm"])
    body_diameter = max_dimension(motor["body_diameter_mm"])
    motor_long = hole_span + hole_diameter
    motor_short = body_diameter

    cassette = {"x": 40.0, "y": 31.0}
    reserve = e["within_project_reserved_axis_envelope_mm"]
    orientation_x = {
        "orientation": "mounting-hole span along envelope X",
        "motor_envelope_mm": [motor_long, motor_short],
        "within_40x31_cassette_margin_each_side_mm": [
            margin(cassette["x"], motor_long), margin(cassette["y"], motor_short)
        ],
        "within_50x41_axis_reservation_margin_each_side_mm": [
            margin(reserve["x"], motor_long), margin(reserve["y"], motor_short)
        ],
    }
    orientation_y = {
        "orientation": "mounting-hole span along envelope Y",
        "motor_envelope_mm": [motor_short, motor_long],
        "within_40x31_cassette_margin_each_side_mm": [
            margin(cassette["x"], motor_short), margin(cassette["y"], motor_long)
        ],
        "within_50x41_axis_reservation_margin_each_side_mm": [
            margin(reserve["x"], motor_short), margin(reserve["y"], motor_long)
        ],
    }
    board_margins_cassette = [margin(cassette["x"], board["x"]),
                              margin(cassette["y"], board["y"])]
    board_margins_reserve = [margin(reserve["x"], board["x"]),
                             margin(reserve["y"], board["y"])]

    assert math.isclose(motor_long, 39.55, abs_tol=1e-9) and math.isclose(motor_short, 28.1, abs_tol=1e-9)
    assert all(v >= 0 for v in orientation_x["within_40x31_cassette_margin_each_side_mm"])
    assert orientation_y["within_40x31_cassette_margin_each_side_mm"][1] < 0
    assert all(v >= 5 for v in orientation_x["within_50x41_axis_reservation_margin_each_side_mm"])
    assert all(v >= 0 for v in board_margins_cassette + board_margins_reserve)

    out = {
        "status": "STATIC_PLAN_ENVELOPE_SCREEN_ONLY",
        "source_evidence": "cad_evidence.json; official Seeed 105990072 EAGLE and CX28BYJ48-08 drawing fields",
        "basis": {
            "mounting_span_upper_mm": hole_span,
            "mounting_hole_diameter_upper_mm": hole_diameter,
            "motor_outer_span_upper_mm": motor_long,
            "motor_body_diameter_upper_mm": motor_short,
            "driver_board_nominal_mm": [board["x"], board["y"]],
            "cassette_candidate_mm": [cassette["x"], cassette["y"]],
            "axis_reservation_mm": [reserve["x"], reserve["y"]],
        },
        "motor_orientations": [orientation_x, orientation_y],
        "driver_board_clearance_each_side_mm": {
            "within_40x31_cassette": board_margins_cassette,
            "within_50x41_axis_reservation": board_margins_reserve,
        },
        "design_disposition": "Orient the motor mounting-hole span along the 50mm cassette/reservation direction. Its conservative 39.55x28.1mm plan envelope nominally fits the 40x31mm candidate envelope, with only 0.225mm and 1.45mm per-side nominal geometric margin before screw heads, washers, retainer walls, process tolerance, wiring or tool access.",
        "stacking_constraint": "The motor and the 35x19.3mm driver PCB are separate overlapping plan envelopes; this check does not place them in Z or establish a common bracket. A vertical/axial arrangement, component height, connector projection and cable bend envelope still need source dimensions or received-part measurement.",
        "service_constraint": "No 55mm extraction sweep is evaluated. Existing 55mm is module displacement and remains unaccepted until the combined motor, board, harness, fastener and tool envelope is integrated against full D7 geometry and physically exchanged.",
        "manufacturing_status": "NOT_A_MANUFACTURING_RELEASE; source dimensions only, no process capability or received-unit verification",
    }
    OUTPUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS: motor upper-bound plan envelope 39.55 x 28.10 mm fits the 40 x 31 mm candidate only with mounting span along X")
    print("PASS: motor margins in 40 x 31 mm are 0.225 / 1.450 mm per side; 50 x 41 mm reservation margins are at least 5 mm")
    print("HOLD: driver PCB is a separate overlapping plan envelope; Z stack, harness, retainers, tolerance and 55 mm D7 sweep remain unchecked")


if __name__ == "__main__":
    main()
