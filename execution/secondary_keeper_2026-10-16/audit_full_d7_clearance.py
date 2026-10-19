#!/usr/bin/env python3
"""Source-bound boss-vs-D7 intersection audit. Review evidence, not release approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

EXPECTED_SHA256 = "20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
AXES = [(1, 85, 40), (2, 55, 140), (3, 135, 140), (4, 225, 130),
        (5, 140, 85), (6, 50, 85), (7, 140, 40)]
TOL = 1e-12


def ring_clip(points: list[list[float]], axis: int, boundary: float, greater: bool) -> list[list[float]]:
    if not points:
        return []
    inside = lambda p: p[axis] >= boundary - TOL if greater else p[axis] <= boundary + TOL
    out: list[list[float]] = []
    prev = points[-1]
    prev_inside = inside(prev)
    for cur in points:
        cur_inside = inside(cur)
        if cur_inside != prev_inside:
            denominator = cur[axis] - prev[axis]
            if abs(denominator) > 1e-15:
                t = (boundary - prev[axis]) / denominator
                cross = [prev[0] + t * (cur[0] - prev[0]), prev[1] + t * (cur[1] - prev[1])]
                cross[axis] = boundary
                out.append(cross)
        if cur_inside:
            out.append(cur)
        prev, prev_inside = cur, cur_inside
    return out


def ring_area(points: list[list[float]]) -> float:
    if len(points) < 3:
        return 0.0
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1]
                   - points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) / 2.0)


def polygon_rect_area(rings: list[list[list[float]]], rect: tuple[float, float, float, float]) -> float:
    xmin, xmax, ymin, ymax = rect
    area = 0.0
    for index, ring in enumerate(rings):
        pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
        for axis, boundary, greater in ((0, xmin, True), (0, xmax, False),
                                        (1, ymin, True), (1, ymax, False)):
            pts = ring_clip(pts, axis, boundary, greater)
        part = ring_area(pts)
        area += part if index == 0 else -part
    return max(0.0, area)


def geometry_polygons(geometry: dict) -> list[list[list[list[float]]]]:
    coords = geometry["coordinates"]
    return [coords] if geometry["type"] == "Polygon" else coords


def boss_intersections(source: dict) -> dict:
    by_axis: dict[str, list[dict]] = {}
    for axis_number, x, y in AXES:
        # Current reviewed outboard boss, rectangular envelope, Z 134..138 mm.
        bx0, bx1, by0, by1, bz0, bz1 = x + 21.5, x + 24.8, y - 3.75, y + 0.2, 134.0, 138.0
        hits: dict[str, float] = defaultdict(float)
        for solid in source["solids"]:
            frame = solid["axis"]
            if frame == "XY":
                z_overlap = max(0.0, min(bz1, solid["high"]) - max(bz0, solid["low"]))
                rect = (bx0, bx1, by0, by1)
            elif frame == "XZ":
                z_overlap = max(0.0, min(by1, solid["high"]) - max(by0, solid["low"]))
                rect = (bx0, bx1, bz0, bz1)
            elif frame == "YZ":
                z_overlap = max(0.0, min(bx1, solid["high"]) - max(bx0, solid["low"]))
                rect = (by0, by1, bz0, bz1)
            else:
                raise ValueError(f"unknown source extrusion axis: {frame}")
            if z_overlap <= 0:
                continue
            cross_section = sum(polygon_rect_area(poly, rect)
                                for poly in geometry_polygons(solid["geometry"]))
            volume = cross_section * z_overlap
            if volume > 1e-6:
                hits[solid["id"]] += volume
        by_axis[str(axis_number)] = [
            {"solid_id": solid_id, "overlap_volume_mm3": round(volume, 6)}
            for solid_id, volume in sorted(hits.items())
        ]
    return by_axis


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assembly_json", type=Path, help="canonical D7/cad/assembly.json from the immutable handoff")
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    args = parser.parse_args()

    digest = hashlib.sha256(args.assembly_json.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"FAIL: source SHA256 mismatch: {digest}")
    source = json.loads(args.assembly_json.read_text(encoding="utf-8"))
    if len(source.get("solids", [])) != 1774:
        raise SystemExit("FAIL: expected 1,774 source solids")

    hits = boss_intersections(source)
    expected = {
        str(axis): ([{"solid_id": "BACK_WOOD", "overlap_volume_mm3": 13.035}]
                    if axis != 5 else [
                        {"solid_id": "BACK_WOOD", "overlap_volume_mm3": 13.035},
                        {"solid_id": "FAN_GASKET", "overlap_volume_mm3": 13.035},
                        {"solid_id": "FAN_MAX_BODY", "overlap_volume_mm3": 26.07},
                    ])
        for axis, _, _ in AXES
    }
    if hits != expected:
        raise SystemExit("FAIL: source intersection result differs from reviewed expected geometry: "
                         + json.dumps(hits, sort_keys=True))

    report = {
        "audit": "current_outboard_boss_vs_immutable_D7_source",
        "source_sha256": digest,
        "source_solid_count": len(source["solids"]),
        "boss_envelope_relative_to_each_axis_mm": {"x": [21.5, 24.8], "y": [-3.75, 0.2], "z": [134, 138]},
        "axis_intersections": hits,
        "fixed_core_collisions_excluding_known_removal_or_redesign_items": 0,
        "known_unresolved_interferences": {
            "back_wood_boss_overlap_axes": list(range(1, 8)),
            "existing_fan_body_and_gasket_overlap_axis": 5,
        },
        "tool_corridor": "NOT_CHECKED_BY_THIS_BOSS_VOLUME_AUDIT",
        "physical_fit_or_strength": "NOT_TESTED",
        "disposition": "FAILS_UNMODIFIED_D7_CLEARANCE; REQUIRES_BACK_WOOD_RELIEF_AND_FAN_RELOCATION_OR_BOSS_REDRAW; NOT_FOR_MANUFACTURE",
        "progress": {"tasks": 48, "done_scope": 21, "working": 8, "open": 15,
                      "hardware_wait": 4, "manufacturing_gates_closed": 0, "manufacturing_gates_total": 6},
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    print("PASS: rehashed all 1,774 canonical solids and reproduced 7 wood + axis-5 fan conflicts")


if __name__ == "__main__":
    main()
