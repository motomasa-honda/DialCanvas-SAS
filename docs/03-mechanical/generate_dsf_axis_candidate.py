#!/usr/bin/env python3
"""Generate a desk-only KHK DSF gear/shaft-support candidate from the current XY path.

This is a reversible alternative study. It does not edit the current baseline files.
The input schedule supplies the old path directions; DS1 tooth counts are mapped to
available DSF1 gears and each chain is re-spaced to exact module-1 pitch distances.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gear_axis_schedule.csv"
CSV_OUT = ROOT / "gear_axis_schedule_dsf_candidate.csv"
SVG_OUT = ROOT / "irregular_layered_gear_layout_dsf_candidate.svg"

CASE_W, CASE_H = 270.0, 205.0
WALL = 12.0
INSIDE_W, INSIDE_H = CASE_W - 2 * WALL, CASE_H - 2 * WALL
BOARD = 115.0
OPENING = 120.0
ACTIVE_D = 87.6
SUPPORT_OD = 7.0
THRUST_WASHER_OD = 14.0
TEETH_MAP = {18: 20, 20: 20, 24: 24, 28: 25}
SUPPORTED_TEETH = {20, 24, 25}

# Axial proposal: front guard -3..0; one thrust washer on each side of each
# supported plate; 30mm single pins; 60mm compound pin; motor body ends at z=114.
A_STACK = {
    "shaft_start": 1.0, "shaft_end": 31.0,
    "collar_start": 1.0, "collar_end": 6.0,
    "collar_washer_start": 6.0, "collar_washer_end": 7.0,
    "plate_start": 7.0, "plate_end": 15.0,
    "gear_washer_start": 15.0, "gear_washer_end": 16.0,
    "hub_start": 16.0, "hub_end": 24.0,
    "face_start": 24.0, "face_end": 30.0,
}
B_STACK = {
    "shaft_start": 33.0, "shaft_end": 63.0,
    "face_start": 33.0, "face_end": 39.0,
    "hub_start": 39.0, "hub_end": 47.0,
    "gear_washer_start": 47.0, "gear_washer_end": 48.0,
    "plate_start": 48.0, "plate_end": 56.0,
    "collar_washer_start": 56.0, "collar_washer_end": 57.0,
    "collar_start": 57.0, "collar_end": 62.0,
}
COMPOUND = {
    "shaft_start": 4.0, "shaft_end": 64.0,
    "coupler_start": 57.0, "coupler_end": 79.0,
    "motor_face": 81.0, "motor_end": 114.0,
}


def read_source() -> dict[str, list[dict[str, str]]]:
    grouped = {"A": [], "B": []}
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            grouped[row["layer"]].append(row)
    if len(grouped["A"]) != 14 or len(grouped["B"]) != 14:
        raise ValueError("source must contain 14 gears in each layer")
    return grouped


def reflow(rows: list[dict[str, str]]) -> list[dict[str, float | int | str]]:
    result: list[dict[str, float | int | str]] = []
    for index, row in enumerate(rows):
        old_teeth = int(row["teeth"])
        teeth = TEETH_MAP[old_teeth]
        old_x, old_y = float(row["inside_x_mm"]), float(row["inside_y_mm"])
        if not index:
            x, y = old_x, old_y
        else:
            prev_old = rows[index - 1]
            prev_new = result[-1]
            dx = old_x - float(prev_old["inside_x_mm"])
            dy = old_y - float(prev_old["inside_y_mm"])
            length = math.hypot(dx, dy)
            center_distance = (teeth + int(prev_new["teeth"])) / 2
            x = float(prev_new["x"]) + dx / length * center_distance
            y = float(prev_new["y"]) + dy / length * center_distance
        result.append({
            "layer": row["layer"],
            "gear_id": row["gear_id"],
            "old_teeth": old_teeth,
            "teeth": teeth,
            "part": f"DSF1-{teeth}",
            "x": x,
            "y": y,
        })
    return result


def rect_distance(x: float, y: float, bounds: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = bounds
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def validate(layers: dict[str, list[dict[str, float | int | str]]]) -> dict[str, float | int]:
    cx, cy = INSIDE_W / 2, INSIDE_H / 2
    board_bounds = (cx - BOARD / 2, cy - BOARD / 2, cx + BOARD / 2, cy + BOARD / 2)
    open_bounds = (cx - OPENING / 2, cy - OPENING / 2, cx + OPENING / 2, cy + OPENING / 2)
    min_edge = min_display_gap = min_web = min_washer_web = min_nonmesh = min_washer_gap = float("inf")
    max_mesh_error = 0.0
    projected_overlaps = 0
    counts: Counter[int] = Counter()
    for layer_key, gears in layers.items():
        for i, gear in enumerate(gears):
            teeth, x, y = int(gear["teeth"]), float(gear["x"]), float(gear["y"])
            if teeth not in SUPPORTED_TEETH:
                raise ValueError(f"unsupported DSF1 tooth count at {gear['gear_id']}: {teeth}")
            counts[teeth] += 1
            radius = (teeth + 2) / 2
            edge = min(x - radius, INSIDE_W - x - radius, y - radius, INSIDE_H - y - radius)
            display_gap = math.hypot(x - cx, y - cy) - radius - ACTIVE_D / 2
            web = (
                math.hypot(x - cx, y - cy) - 112 / 2 - SUPPORT_OD / 2
                if layer_key == "A"
                else rect_distance(x, y, open_bounds) - SUPPORT_OD / 2
            )
            min_edge = min(min_edge, edge)
            min_display_gap = min(min_display_gap, display_gap)
            min_web = min(min_web, web)
            washer_web = (
                math.hypot(x - cx, y - cy) - 112 / 2 - THRUST_WASHER_OD / 2
                if layer_key == "A"
                else rect_distance(x, y, open_bounds) - THRUST_WASHER_OD / 2
            )
            min_washer_web = min(min_washer_web, washer_web)
            if edge < 5.0 or display_gap < 12.0 or web < 2.5:
                raise ValueError(f"clearance threshold failed at {gear['gear_id']}")
            if i:
                previous = gears[i - 1]
                measured = math.hypot(x - float(previous["x"]), y - float(previous["y"]))
                nominal = (teeth + int(previous["teeth"])) / 2
                max_mesh_error = max(max_mesh_error, abs(measured - nominal))
            for prior in gears[: max(0, i - 1)]:
                clearance = math.hypot(x - float(prior["x"]), y - float(prior["y"])) - radius - (int(prior["teeth"]) + 2) / 2
                min_nonmesh = min(min_nonmesh, clearance)
                if clearance < 1.0:
                    raise ValueError(f"same-plane non-mesh interference {prior['gear_id']}-{gear['gear_id']}")
            for prior in gears[:i]:
                washer_clearance = math.hypot(x - float(prior["x"]), y - float(prior["y"])) - THRUST_WASHER_OD
                min_washer_gap = min(min_washer_gap, washer_clearance)
                if washer_clearance < 1.0:
                    raise ValueError(f"thrust-washer interference {prior['gear_id']}-{gear['gear_id']}")

    a0, b0 = layers["A"][0], layers["B"][0]
    if math.hypot(float(a0["x"]) - float(b0["x"]), float(a0["y"]) - float(b0["y"])) > 0.001:
        raise ValueError("compound gears must share one axis")
    for a in layers["A"]:
        for b in layers["B"]:
            if (a["gear_id"], b["gear_id"]) == ("A00", "B00"):
                continue
            center_sep = math.hypot(float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"]))
            if (int(a["teeth"]) + int(b["teeth"]) + 4) / 2 - center_sep > 1:
                projected_overlaps += 1
    if len(counts) == 0 or sum(counts.values()) != 28 or max_mesh_error > 0.001:
        raise ValueError("gear count or mesh center-distance check failed")
    if min_washer_web < 0.5:
        raise ValueError("thrust-washer clearance to the support opening is too small")

    # Verify that the proposed axial part intervals add up and do not consume the 2mm tooth gap.
    if A_STACK["plate_end"] != A_STACK["gear_washer_start"] or A_STACK["face_end"] + 3 != B_STACK["face_start"]:
        raise ValueError("A/B axial separation or support stack is inconsistent")
    if A_STACK["collar_washer_end"] != A_STACK["plate_start"] or B_STACK["collar_washer_end"] != B_STACK["plate_end"] + 1:
        raise ValueError("shaft collar position does not match the support plate")
    if COMPOUND["coupler_start"] - COMPOUND["shaft_end"] + 7 != 0:
        raise ValueError("compound shaft insertion must be 7mm")
    if 121 - COMPOUND["motor_end"] != 7:
        raise ValueError("motor rear clearance should be 7mm in this draft")
    return {
        "gear_count": 28,
        "shaft_count": 27,
        "min_edge_mm": min_edge,
        "min_active_screen_gap_mm": min_display_gap,
        "min_support_web_mm": min_web,
        "min_thrust_washer_web_mm": min_washer_web,
        "min_thrust_washer_gap_mm": min_washer_gap,
        "min_nonmesh_clearance_mm": min_nonmesh,
        "max_mesh_error_mm": max_mesh_error,
        "projected_cross_layer_overlaps": projected_overlaps,
        "dsf20": counts[20], "dsf24": counts[24], "dsf25": counts[25],
    }


def write_schedule(layers: dict[str, list[dict[str, float | int | str]]]) -> None:
    fields = [
        "layer", "gear_id", "KHK_part", "teeth", "module_mm",
        "inside_x_mm", "inside_y_mm", "case_x_mm", "case_y_mm", "plate_x_mm", "plate_y_mm",
        "shaft_group", "shaft_type", "shaft_z_start_mm", "shaft_z_end_mm",
        "collar_z_start_mm", "collar_z_end_mm", "collar_washer_z_start_mm", "collar_washer_z_end_mm",
        "support_plate_z_start_mm", "support_plate_z_end_mm",
        "gear_washer_z_start_mm", "gear_washer_z_end_mm", "hub_z_start_mm", "hub_z_end_mm",
        "tooth_face_z_start_mm", "tooth_face_z_end_mm", "bushing_position", "previous_center_distance_mm",
    ]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for layer_key, gears in layers.items():
            for i, gear in enumerate(gears):
                shared = gear["gear_id"] in {"A00", "B00"}
                stack = A_STACK if layer_key == "A" else B_STACK
                if shared:
                    record = {
                        "shaft_group": "compound-01", "shaft_type": "5mm h7 parallel pin, 60mm stock, uncut",
                        "shaft_z_start_mm": COMPOUND["shaft_start"], "shaft_z_end_mm": COMPOUND["shaft_end"],
                        "collar_z_start_mm": "", "collar_z_end_mm": "",
                        "collar_washer_z_start_mm": "", "collar_washer_z_end_mm": "",
                        "support_plate_z_start_mm": stack["plate_start"], "support_plate_z_end_mm": stack["plate_end"],
                        "gear_washer_z_start_mm": stack["gear_washer_start"], "gear_washer_z_end_mm": stack["gear_washer_end"],
                        "hub_z_start_mm": stack["hub_start"], "hub_z_end_mm": stack["hub_end"],
                        "tooth_face_z_start_mm": stack["face_start"], "tooth_face_z_end_mm": stack["face_end"],
                        "bushing_position": "front+rear",
                    }
                else:
                    record = {
                        "shaft_group": gear["gear_id"], "shaft_type": "5mm h7 parallel pin, 30mm",
                        "shaft_z_start_mm": stack["shaft_start"], "shaft_z_end_mm": stack["shaft_end"],
                        "collar_z_start_mm": stack["collar_start"], "collar_z_end_mm": stack["collar_end"],
                        "collar_washer_z_start_mm": stack["collar_washer_start"], "collar_washer_z_end_mm": stack["collar_washer_end"],
                        "support_plate_z_start_mm": stack["plate_start"], "support_plate_z_end_mm": stack["plate_end"],
                        "gear_washer_z_start_mm": stack["gear_washer_start"], "gear_washer_z_end_mm": stack["gear_washer_end"],
                        "hub_z_start_mm": stack["hub_start"], "hub_z_end_mm": stack["hub_end"],
                        "tooth_face_z_start_mm": stack["face_start"], "tooth_face_z_end_mm": stack["face_end"],
                        "bushing_position": "front" if layer_key == "A" else "rear",
                    }
                previous = ""
                if i:
                    p = gears[i - 1]
                    previous = f"{math.hypot(float(gear['x']) - float(p['x']), float(gear['y']) - float(p['y'])):.3f}"
                writer.writerow({
                    "layer": layer_key, "gear_id": gear["gear_id"], "KHK_part": gear["part"],
                    "teeth": gear["teeth"], "module_mm": "1.0",
                    "inside_x_mm": f"{float(gear['x']):.3f}", "inside_y_mm": f"{float(gear['y']):.3f}",
                    "case_x_mm": f"{float(gear['x']) + WALL:.3f}", "case_y_mm": f"{float(gear['y']) + WALL:.3f}",
                    "plate_x_mm": f"{float(gear['x']) + 3:.3f}", "plate_y_mm": f"{float(gear['y']) + 3:.3f}",
                    **record, "previous_center_distance_mm": previous,
                })


def draw_svg(layers: dict[str, list[dict[str, float | int | str]]], metrics: dict[str, float | int]) -> None:
    scale = 2.05
    top = 90.0
    panels = {"A": 42.0, "B": 666.0}
    def sx(panel: float, x: float) -> float: return panel + x * scale
    def sy(y: float) -> float: return top + y * scale
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-labelledby="title desc">',
        '<title id="title">DSF1 two-layer gear layout candidate</title>',
        '<desc id="desc">Separate top views of front and rear gear planes. Existing 28 positions re-spaced to catalog KHK DSF1 gears with 5mm clamp hubs. Not a fabrication drawing.</desc>',
        '<rect width="1280" height="720" fill="#101112"/>',
        '<style>text{font-family:DejaVu Sans,sans-serif;fill:#eee0c7}.title{font-size:24px;font-weight:bold}.sub{font-size:13px;fill:#cdbfa7}.panelTitle{font-size:17px;font-weight:bold}.small{font-size:13px;fill:#d7cbb7}.tiny{font-size:10px;fill:#bdb09b}.id{font-size:8px;font-weight:bold;text-anchor:middle;dominant-baseline:middle}.mesh{stroke:#e8c68b;stroke-width:1;stroke-dasharray:4 4;opacity:.55}.case{fill:#211b15;stroke:#a77d49;stroke-width:2}.board{fill:#315b60;fill-opacity:.13;stroke:#a5cfcc;stroke-width:2;stroke-dasharray:7 5}.opening{fill:none;stroke:#ffe2a1;stroke-width:1.5;stroke-dasharray:6 4}.gearA{fill:#d19b50;fill-opacity:.86;stroke:#ffe2a1;stroke-width:1.4}.gearB{fill:#9a572b;fill-opacity:.82;stroke:#eab36d;stroke-width:1.4}.hub{fill:#43351f;stroke:#fff0bd;stroke-width:1.2}.bore{fill:#101112;stroke:#fff0bd;stroke-width:1}</style>',
        '<text class="title" x="40" y="34">DSF1 gear layout candidate</text>',
        '<text class="sub" x="40" y="54">Separate plane views · 28 positions kept for comparison · not a fabrication drawing</text>',
    ]
    for layer_key, gears in layers.items():
        panel = panels[layer_key]
        elements.append(f'<text class="panelTitle" x="{panel:.1f}" y="78">{"Front plane A" if layer_key == "A" else "Rear plane B"}</text>')
        elements.append(f'<rect class="case" x="{panel:.1f}" y="{top:.1f}" width="{CASE_W*scale:.1f}" height="{CASE_H*scale:.1f}" rx="8"/>')
        board_x = WALL + (INSIDE_W - BOARD) / 2
        board_y = WALL + (INSIDE_H - BOARD) / 2
        elements.append(f'<rect class="board" x="{sx(panel,board_x):.1f}" y="{sy(board_y):.1f}" width="{BOARD*scale:.1f}" height="{BOARD*scale:.1f}" rx="5"/>')
        if layer_key == "A":
            elements.append(f'<circle class="opening" cx="{sx(panel,WALL+INSIDE_W/2):.1f}" cy="{sy(WALL+INSIDE_H/2):.1f}" r="{56*scale:.1f}"/>')
        else:
            opx = WALL + (INSIDE_W - OPENING) / 2
            opy = WALL + (INSIDE_H - OPENING) / 2
            elements.append(f'<rect class="opening" x="{sx(panel,opx):.1f}" y="{sy(opy):.1f}" width="{OPENING*scale:.1f}" height="{OPENING*scale:.1f}"/>')
        for a, b in zip(gears, gears[1:]):
            elements.append(f'<line class="mesh" x1="{sx(panel,float(a["x"])+WALL):.1f}" y1="{sy(float(a["y"])+WALL):.1f}" x2="{sx(panel,float(b["x"])+WALL):.1f}" y2="{sy(float(b["y"])+WALL):.1f}"/>')
        klass = "gearA" if layer_key == "A" else "gearB"
        for gear in gears:
            x, y, teeth = float(gear["x"])+WALL, float(gear["y"])+WALL, int(gear["teeth"])
            radius = (teeth + 2) / 2 * scale
            elements.append(f'<circle class="{klass}" cx="{sx(panel,x):.1f}" cy="{sy(y):.1f}" r="{radius:.1f}"/>')
            elements.append(f'<circle class="hub" cx="{sx(panel,x):.1f}" cy="{sy(y):.1f}" r="{7*scale:.1f}"/>')
            elements.append(f'<circle class="bore" cx="{sx(panel,x):.1f}" cy="{sy(y):.1f}" r="{2.5*scale:.1f}"/>')
            elements.append(f'<text class="id" x="{sx(panel,x):.1f}" y="{sy(y):.1f}">{gear["gear_id"]}</text>')
    elements.extend([
        f'<text class="small" x="40" y="625">Gears: DSF1-20 × {metrics["dsf20"]} · DSF1-24 × {metrics["dsf24"]} · DSF1-25 × {metrics["dsf25"]}</text>',
        f'<text class="small" x="40" y="649">Minimum case margin {metrics["min_edge_mm"]:.1f}mm · minimum active-display gap {metrics["min_active_screen_gap_mm"]:.1f}mm · center-distance error {metrics["max_mesh_error_mm"]:.3f}mm</text>',
        f'<text class="small" x="40" y="673">OD14 washer/opening web {metrics["min_thrust_washer_web_mm"]:.1f}mm · washer gap {metrics["min_thrust_washer_gap_mm"]:.1f}mm · min non-mesh gap {metrics["min_nonmesh_clearance_mm"]:.1f}mm</text>',
        '<text class="tiny" x="40" y="698">Blue dashed: board/opening · dashed gold lines: mesh pairs · ID inside each hub · tooth outlines are pitch-circle envelopes only</text>',
        '</svg>',
    ])
    SVG_OUT.write_text("\n".join(elements), encoding="utf-8")


def main() -> None:
    source = read_source()
    layers = {key: reflow(rows) for key, rows in source.items()}
    metrics = validate(layers)
    write_schedule(layers)
    draw_svg(layers, metrics)
    print(f"Wrote {CSV_OUT.name} and {SVG_OUT.name}: {metrics}")


if __name__ == "__main__":
    main()
