#!/usr/bin/env python3
"""Source-bound screening for seven shallow keeper seats and rear tool bores."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import audit_full_d7_clearance as audit

SOURCE_SHA256 = audit.EXPECTED_SHA256
EXPECTED_SOLIDS = 1774
WOOD_Z = (137.0, 145.0)
SEAT_Z = (137.0, 138.6)
SEAT_SIZE = (4.1, 4.75)
SEAT_CENTER = (22.95, -1.775)
KEEPER_BOSS_X = (21.3, 24.6)  # proposed 0.2mm inward shift, retains 0.625mm bore wall
KEEPER_BOSS_Y = (-3.75, 0.2)
STUD_CENTER = (22.95, -1.1)
STUD_LENGTH_Z = (134.35, 139.35)
BORE_SIZE = 3.2
DRIVER_DIAMETER = 2.4


def rect(x0: float, x1: float, y0: float, y1: float) -> tuple[float, float, float, float]:
    if not x0 < x1 or not y0 < y1:
        raise ValueError("rectangle bounds must be strictly increasing")
    return x0, x1, y0, y1


def point_segment_distance(p: tuple[float, float], a: list[float], b: list[float]) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    t = 0.0 if denom == 0 else max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / denom))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def orientation(a: list[float], b: list[float], c: list[float]) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def segments_intersect(a: list[float], b: list[float], c: list[float], d: list[float]) -> bool:
    o1, o2, o3, o4 = orientation(a, b, c), orientation(a, b, d), orientation(c, d, a), orientation(c, d, b)
    eps = 1e-10
    if (o1 > eps and o2 < -eps or o1 < -eps and o2 > eps) and (
            o3 > eps and o4 < -eps or o3 < -eps and o4 > eps):
        return True
    for value, p, u, v in ((o1, c, a, b), (o2, d, a, b), (o3, a, c, d), (o4, b, c, d)):
        if abs(value) <= eps and min(u[0], v[0])-eps <= p[0] <= max(u[0], v[0])+eps and min(u[1], v[1])-eps <= p[1] <= max(u[1], v[1])+eps:
            return True
    return False


def segment_distance(a: list[float], b: list[float], c: list[float], d: list[float]) -> float:
    if segments_intersect(a, b, c, d):
        return 0.0
    return min(point_segment_distance(p, u, v) for p, u, v in ((a, c, d), (b, c, d), (c, a, b), (d, a, b)))


def rect_boundary_distance(box: tuple[float, float, float, float], rings: list[list[list[float]]]) -> float:
    x0, x1, y0, y1 = box
    edges = [([x0, y0], [x1, y0]), ([x1, y0], [x1, y1]),
             ([x1, y1], [x0, y1]), ([x0, y1], [x0, y0])]
    dists = []
    for ring in rings:
        vertices = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            dists.extend(segment_distance(p, q, a, b) for p, q in edges)
    return min(dists, default=math.inf)


def box_material_area(source: dict, box: tuple[float, float, float, float], z_range: tuple[float, float]) -> list[dict]:
    areas = []
    for source_index, solid in enumerate(source["solids"]):
        if solid["id"] != "BACK_WOOD" or solid["axis"] != "XY":
            continue
        overlap = max(0.0, min(z_range[1], solid["high"]) - max(z_range[0], solid["low"]))
        if overlap <= 0:
            continue
        area = sum(audit.polygon_rect_area(poly, box)
                   for poly in audit.geometry_polygons(solid["geometry"]))
        areas.append({"source_index": source_index, "z_overlap_mm": overlap, "intersection_area_mm2": area})
    return areas


def screen_reliefs(source: dict) -> dict:
    expected_area = SEAT_SIZE[0] * SEAT_SIZE[1]
    bore_square_area = BORE_SIZE * BORE_SIZE
    axes = {}
    all_seats_inside, all_bores_inside = True, True
    for axis_number, x, y in audit.AXES:
        sx, sy = x + SEAT_CENTER[0], y + SEAT_CENTER[1]
        seat = rect(sx-SEAT_SIZE[0]/2, sx+SEAT_SIZE[0]/2,
                    sy-SEAT_SIZE[1]/2, sy+SEAT_SIZE[1]/2)
        bx, by = x + STUD_CENTER[0], y + STUD_CENTER[1]
        bore_square = rect(bx-BORE_SIZE/2, bx+BORE_SIZE/2,
                           by-BORE_SIZE/2, by+BORE_SIZE/2)
        seat_areas = box_material_area(source, seat, SEAT_Z)
        bore_areas = box_material_area(source, bore_square, WOOD_Z)
        seat_ok = bool(seat_areas) and all(abs(item["intersection_area_mm2"] - expected_area) < 1e-6
                                           for item in seat_areas)
        # A full-area hit is wood to be drilled; zero is an existing void.
        # Partial area means the path clips a wood edge and is not accepted.
        bore_ok = bool(bore_areas) and all(
            min(abs(item["intersection_area_mm2"]),
                abs(item["intersection_area_mm2"]-bore_square_area)) < 1e-6
            for item in bore_areas)
        all_seats_inside &= seat_ok
        all_bores_inside &= bore_ok
        layer = next((solid for solid in source["solids"] if solid["id"] == "BACK_WOOD"
                      and solid["axis"] == "XY" and solid["low"] <= SEAT_Z[0]
                      and solid["high"] >= SEAT_Z[1]), None)
        boundary_clearance = math.inf
        if layer:
            rings = audit.geometry_polygons(layer["geometry"])[0]
            boundary_clearance = rect_boundary_distance(seat, rings)
        axes[str(axis_number)] = {
            "seat_xy_world_mm": [round(seat[0], 4), round(seat[1], 4), round(seat[2], 4), round(seat[3], 4)],
            "seat_z_mm": list(SEAT_Z),
            "seat_area_mm2": expected_area,
            "seat_layers": seat_areas,
            "seat_entirely_in_existing_wood": seat_ok,
            "seat_to_nearest_existing_wood_boundary_mm": round(boundary_clearance, 4),
            "bore_xy_world_mm": [round(bore_square[0], 4), round(bore_square[1], 4),
                                 round(bore_square[2], 4), round(bore_square[3], 4)],
            "bore_square_area_mm2": bore_square_area,
            "bore_layers": bore_areas,
            "bore_path_is_full_wood_or_full_void_at_every_layer": bore_ok,
        }

    # The 3.2mm square is a conservative lateral envelope for a 2.4mm driver
    # along Z=137..145; check all non-wood source solids in that entire corridor.
    nonwood_corridor_hits = {}
    removable_grille_hits = {}
    for axis_number, *_ in audit.AXES:
        hits = audit.boss_intersections(source,
            x_offset=(STUD_CENTER[0]-BORE_SIZE/2, STUD_CENTER[0]+BORE_SIZE/2),
            y_offset=(STUD_CENTER[1]-BORE_SIZE/2, STUD_CENTER[1]+BORE_SIZE/2),
            z_range=WOOD_Z)[str(axis_number)]
        nonwood = [hit for hit in hits if hit["solid_id"] != "BACK_WOOD"]
        removable_grille_hits[str(axis_number)] = [hit for hit in nonwood if hit["solid_id"] == "REAR_GRILLE"]
        nonwood_corridor_hits[str(axis_number)] = [hit for hit in nonwood if hit["solid_id"] != "REAR_GRILLE"]

    # The proposed boss is narrowed/translated by 0.2mm from the current CAD.
    # Its nominal wood overlap is covered by the 1.6mm seat; the remaining fan
    # overlap on axis 5 is explicitly not resolved here.
    body_hits = audit.boss_intersections(source, x_offset=KEEPER_BOSS_X,
        y_offset=KEEPER_BOSS_Y, z_range=(134.0, 138.0))
    counts = {axis: [hit["solid_id"] for hit in hits] for axis, hits in body_hits.items()}
    return {
        "audit": "candidate_seven_keeper_backwood_seats_and_rear_tool_bores",
        "source_sha256": SOURCE_SHA256,
        "source_solid_count": len(source["solids"]),
        "status": "GEOMETRY_SCREEN_ONLY_NOT_FOR_MANUFACTURE",
        "proposed_geometry": {
            "boss_xy_offsets_mm": {"x": list(KEEPER_BOSS_X), "y": list(KEEPER_BOSS_Y)},
            "boss_nominal_backwood_overlap_z_mm": [137.0, 138.0],
            "seat_size_mm": list(SEAT_SIZE), "seat_center_offset_mm": list(SEAT_CENTER),
            "seat_z_mm": list(SEAT_Z), "seat_depth_mm": SEAT_Z[1]-SEAT_Z[0],
            "seat_margin_each_side_vs_boss_mm": [
                (SEAT_SIZE[0]-(KEEPER_BOSS_X[1]-KEEPER_BOSS_X[0]))/2,
                (SEAT_SIZE[1]-(KEEPER_BOSS_Y[1]-KEEPER_BOSS_Y[0]))/2],
            "stud_center_offset_mm": list(STUD_CENTER),
            "stud_z_mm": list(STUD_LENGTH_Z),
            "rear_clearance_bore_diameter_mm": BORE_SIZE,
            "review_driver_diameter_mm": DRIVER_DIAMETER,
            "nominal_diameter_clearance_mm": BORE_SIZE-DRIVER_DIAMETER,
            "rear_wood_z_mm": list(WOOD_Z),
            "boss_shift_from_current_x_mm": -0.2,
        },
        "axis_results": axes,
        "all_seats_inside_original_wood": all_seats_inside,
        "all_bore_envelopes_are_full_wood_or_full_void": all_bores_inside,
        "rear_driver_square_corridor_fixed_nonwood_intersections": nonwood_corridor_hits,
        "rear_driver_square_corridor_removable_grille_intersections": removable_grille_hits,
        "boss_candidate_full_source_intersections_by_axis": counts,
        "explicit_remaining_blocker": "axis 5 boss still overlaps original FAN_MAX_BODY/FAN_GASKET; relocated fan source/position is not represented in immutable D7",
        "limitations": [
            "the 3.2mm square bore envelope is conservative relative to the 2.4mm round driver",
            "the common removable rear grille must be removed before tool access as specified by G6-06 service sequence",
            "no wood strength, grain, breakout, machining process capability or fastener load verified",
            "no physical module measurement, full tool handle envelope, vibration, heat or 55mm exchange test",
            "fan relocation and altered keeper CAD must be integrated and re-audited before accepting the candidate",
        ],
        "disposition": "WOOD_RELIEF_SCREEN_PASS; AXIS5_FAN_RELOCATION_REQUIRED; NOT_RELEASED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assembly_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.assembly_json.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise SystemExit(f"FAIL: source SHA256 mismatch: {digest}")
    source = json.loads(raw)
    if len(source.get("solids", [])) != EXPECTED_SOLIDS:
        raise SystemExit(f"FAIL: expected {EXPECTED_SOLIDS} source solids")
    result = screen_reliefs(source)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    all_driver_clear = all(not hits for hits in result["rear_driver_square_corridor_fixed_nonwood_intersections"].values())
    if not result["all_seats_inside_original_wood"] or not result["all_bore_envelopes_are_full_wood_or_full_void"] or not all_driver_clear:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
