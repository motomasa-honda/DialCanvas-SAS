#!/usr/bin/env python3
"""Generate the one-off gear layout, plate templates, and axis schedule.

Gear outlines are schematic; the checked geometry uses catalog module-1 pitch
center distances and catalog outside diameters, not generated involute teeth.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASE_W, CASE_H, DEPTH = 270.0, 205.0, 145.0
WALL = 12.0
INNER_W, INNER_H, INNER_D = CASE_W - 2 * WALL, CASE_H - 2 * WALL, DEPTH - 2 * WALL
BOARD = 115.0
ACTIVE_D = 87.6
OPENING = 120.0
A_OPENING_D = 112.0
PLATE_T = 8.0
PLATE_OVERHANG = 3.0
PLATE_W = INNER_W + 2 * PLATE_OVERHANG
PLATE_H = INNER_H + 2 * PLATE_OVERHANG
BUSHING_ID, BUSHING_OD, BUSHING_L = 5.0, 7.0, 8.0
MODULE = 1.0
COMPOUND_SHAFT_STOCK_MM = 60.0
COMPOUND_SHAFT_FINISHED_MM = 58.5
COMPOUND_SHAFT_START_Z = -3.5
COUPLER_START_Z = 48.0
COUPLER_LENGTH_MM = 22.0
COUPLER_OD_MM = 14.0
COUPLER_HUB_LENGTH_MM = 7.0
MOTOR_FACE_Z = 72.0
MOTOR_LENGTH_MM = 33.0
MOTOR_END_Z = MOTOR_FACE_Z + MOTOR_LENGTH_MM
SCREEN_CENTER = (INNER_W / 2, INNER_H / 2)
BOARD_BOUNDS = (
    SCREEN_CENTER[0] - BOARD / 2,
    SCREEN_CENTER[1] - BOARD / 2,
    SCREEN_CENTER[0] + BOARD / 2,
    SCREEN_CENTER[1] + BOARD / 2,
)
OPENING_BOUNDS = (
    SCREEN_CENTER[0] - OPENING / 2,
    SCREEN_CENTER[1] - OPENING / 2,
    SCREEN_CENTER[0] + OPENING / 2,
    SCREEN_CENTER[1] + OPENING / 2,
)

# Coordinates are measured from the top-left of the clear inside of the case.
# Each sequence is an open train. The A00/B00 wheels share one compound shaft.
# A is carried on an irregular circular-front-plate web around the active dial;
# B remains outside the rear board opening. Coordinates are relative to the
# display center. The open ends leave deliberate negative space on the upper
# right; the two trains cluster on the left and lower perimeter.
LAYERS = {
    "A": {
        "label": "前列 A",
        "fill": "#d19b50",
        "stroke": "#ffe2a1",
        "opacity": 0.88,
        "gears": [
            ("A00", 20, 123.000, 22.500),
            ("A01", 18, 104.332, 26.035),
            ("A02", 28, 82.134, 32.056),
            ("A03", 18, 62.388, 43.850),
            ("A04", 20, 57.878, 62.307),
            ("A05", 18, 43.639, 74.886),
            ("A06", 24, 50.895, 94.593),
            ("A07", 18, 55.565, 115.067),
            ("A08", 20, 60.280, 133.473),
            ("A09", 18, 73.947, 146.671),
            ("A10", 28, 94.912, 156.132),
            ("A11", 18, 117.911, 156.340),
            ("A12", 20, 136.658, 159.425),
            ("A13", 18, 154.861, 153.978),
        ],
    },
    "B": {
        "label": "後列 B",
        "fill": "#9a572b",
        "stroke": "#eab36d",
        "opacity": 0.70,
        "gears": [
            ("B00", 18, 123.000, 22.500),
            ("B01", 20, 104.667, 17.508),
            ("B02", 18, 86.334, 22.500),
            ("B03", 20, 68.334, 16.417),
            ("B04", 20, 51.013, 26.417),
            ("B05", 24, 31.746, 37.037),
            ("B06", 20, 48.746, 51.001),
            ("B07", 28, 31.746, 67.941),
            ("B08", 20, 48.746, 84.881),
            ("B09", 24, 31.746, 98.841),
            ("B10", 18, 48.746, 111.169),
            ("B11", 28, 33.746, 128.605),
            ("B12", 20, 47.746, 148.096),
            ("B13", 18, 32.746, 159.758),
        ],
    },
}


def radius(teeth: int) -> float:
    return MODULE * (teeth + 2) / 2


def rect_distance(x: float, y: float, bounds: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = bounds
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def counts() -> dict[int, int]:
    result: dict[int, int] = {}
    for layer in LAYERS.values():
        for _, teeth, _, _ in layer["gears"]:
            result[teeth] = result.get(teeth, 0) + 1
    return dict(sorted(result.items()))


def validate() -> dict[str, float | int]:
    board_opening_clearance = (OPENING - BOARD) / 2
    if board_opening_clearance < 0:
        raise ValueError(f"display board {BOARD:.1f} mm does not fit {OPENING:.1f} mm rear opening")
    if BOARD > INNER_W or BOARD > INNER_H:
        raise ValueError(f"display board {BOARD:.1f} mm does not fit case inner plan {INNER_W:.1f}×{INNER_H:.1f} mm")

    drive_axis = LAYERS["A"]["gears"][0]
    coupler_board_clearance = rect_distance(drive_axis[2], drive_axis[3], BOARD_BOUNDS) - COUPLER_OD_MM / 2
    if coupler_board_clearance < 3.0:
        raise ValueError(
            f"coupler-to-board nominal envelope clearance {coupler_board_clearance:.3f} mm < 3 mm"
        )

    minimum_case_margin = float("inf")
    minimum_display_gap = float("inf")
    minimum_bushing_web = float("inf")
    minimum_nonmesh_clearance = float("inf")
    maximum_mesh_error = 0.0
    all_ids: set[str] = set()

    for layer_key, layer in LAYERS.items():
        gears = layer["gears"]
        for index, (gear_id, teeth, x, y) in enumerate(gears):
            if gear_id in all_ids:
                raise ValueError(f"duplicate gear ID {gear_id}")
            all_ids.add(gear_id)
            if teeth not in {18, 20, 24, 28}:
                raise ValueError(f"unsupported 5 mm bore gear: {gear_id} {teeth}T")

            r = radius(teeth)
            case_margin = min(x - r, INNER_W - x - r, y - r, INNER_H - y - r)
            display_gap = math.hypot(x - SCREEN_CENTER[0], y - SCREEN_CENTER[1]) - r - ACTIVE_D / 2
            if layer_key == "A":
                bushing_web = math.hypot(x - SCREEN_CENTER[0], y - SCREEN_CENTER[1]) - A_OPENING_D / 2 - BUSHING_OD / 2
            else:
                bushing_web = rect_distance(x, y, OPENING_BOUNDS) - BUSHING_OD / 2
            minimum_case_margin = min(minimum_case_margin, case_margin)
            minimum_display_gap = min(minimum_display_gap, display_gap)
            minimum_bushing_web = min(minimum_bushing_web, bushing_web)
            if case_margin < 5.0:
                raise ValueError(f"{gear_id} case-edge margin {case_margin:.3f} mm < 5 mm")
            if display_gap < 12.0:
                raise ValueError(f"{gear_id} active-display gap {display_gap:.3f} mm < 12 mm")
            if bushing_web < 2.5:
                raise ValueError(f"{gear_id} bushing-hole web to the central opening {bushing_web:.3f} mm < 2.5 mm")

            if index:
                previous = gears[index - 1]
                center_distance = math.hypot(x - previous[2], y - previous[3])
                nominal = MODULE * (teeth + previous[1]) / 2
                error = abs(center_distance - nominal)
                maximum_mesh_error = max(maximum_mesh_error, error)
                if error > 0.02:
                    raise ValueError(
                        f"{layer_key} mesh {previous[0]}-{gear_id}: "
                        f"{center_distance:.3f} != {nominal:.3f} mm"
                    )

            for prior in gears[: max(0, index - 1)]:
                clearance = math.hypot(x - prior[2], y - prior[3]) - r - radius(prior[1])
                minimum_nonmesh_clearance = min(minimum_nonmesh_clearance, clearance)
                if clearance < 1.0:
                    raise ValueError(
                        f"same-plane non-mesh interference {prior[0]}-{gear_id}: {clearance:.3f} mm"
                    )

    a0, b0 = LAYERS["A"]["gears"][0], LAYERS["B"]["gears"][0]
    if math.hypot(a0[2] - b0[2], a0[3] - b0[3]) > 0.001:
        raise ValueError("A00/B00 must share the compound-shaft center")

    cross_layer_overlaps = 0
    minimum_cross_axis_separation = float("inf")
    for a in LAYERS["A"]["gears"]:
        for b in LAYERS["B"]["gears"]:
            if a[0] == "A00" and b[0] == "B00":
                continue
            axis_separation = math.hypot(a[2] - b[2], a[3] - b[3])
            minimum_cross_axis_separation = min(minimum_cross_axis_separation, axis_separation)
            if axis_separation < 6.0:
                raise ValueError(f"cross-layer shafts {a[0]}-{b[0]} are only {axis_separation:.3f} mm apart")
            overlap = radius(a[1]) + radius(b[1]) - axis_separation
            if overlap > 1.0:
                cross_layer_overlaps += 1
    if cross_layer_overlaps < 8:
        raise ValueError(f"only {cross_layer_overlaps} projected A/B overlaps")

    gear_count = sum(len(layer["gears"]) for layer in LAYERS.values())
    shaft_count = gear_count - 1  # only A00/B00 share one shaft
    if gear_count != 28 or shaft_count != 27:
        raise ValueError(f"unexpected count: {gear_count} wheels / {shaft_count} axes")

    return {
        "gear_count": gear_count,
        "shaft_count": shaft_count,
        "bushing_count": gear_count,
        "board_opening_clearance": board_opening_clearance,
        "coupler_board_clearance": coupler_board_clearance,
        "cross_layer_overlaps": cross_layer_overlaps,
        "minimum_cross_axis_separation": minimum_cross_axis_separation,
        "minimum_case_margin": minimum_case_margin,
        "minimum_display_gap": minimum_display_gap,
        "minimum_bushing_web": minimum_bushing_web,
        "minimum_nonmesh_clearance": minimum_nonmesh_clearance,
        "maximum_mesh_error": maximum_mesh_error,
    }


def gear_outline(teeth: int) -> str:
    pitch_radius = teeth / 2
    tip_radius = radius(teeth)
    root_radius = pitch_radius - 0.72
    points: list[tuple[float, float]] = []
    step = 360 / teeth
    for tooth in range(teeth):
        base = step * tooth
        for fraction, rad in [(-0.34, root_radius), (-0.18, root_radius), (-0.10, tip_radius),
                              (0.10, tip_radius), (0.18, root_radius), (0.34, root_radius)]:
            angle = math.radians(base + fraction * step)
            points.append((rad * math.cos(angle), rad * math.sin(angle)))
    return " ".join(("M" if i == 0 else "L") + f"{x:.4f},{y:.4f}" for i, (x, y) in enumerate(points)) + " Z"


def draw_links(layer: dict) -> str:
    result = []
    for left, right in zip(layer["gears"], layer["gears"][1:]):
        result.append(
            f'<line class="mesh" x1="{left[2] + WALL:.3f}" y1="{left[3] + WALL:.3f}" '
            f'x2="{right[2] + WALL:.3f}" y2="{right[3] + WALL:.3f}"/>'
        )
    return "\n".join(result)


def draw_gears(layer_key: str) -> str:
    layer = LAYERS[layer_key]
    result = []
    for gear_id, teeth, x, y in layer["gears"]:
        x += WALL
        y += WALL
        result.append(
            f'<g class="gear {layer_key.lower()}" transform="translate({x:.3f} {y:.3f})" '
            f'data-id="{gear_id}" data-teeth="{teeth}">'
            f'<path d="{gear_outline(teeth)}"/>'
            f'<circle class="hub" r="{min(5.8, radius(teeth) * 0.52):.2f}"/>'
            '<circle class="bore" r="2.5"/>'
            '</g>'
        )
    return "\n".join(result)


def write_plan(metrics: dict[str, float | int]) -> None:
    counts_text = " · ".join(f"{teeth}T × {number}" for teeth, number in counts().items())
    screen_x, screen_y = SCREEN_CENTER[0] + WALL, SCREEN_CENTER[1] + WALL
    board_x, board_y = BOARD_BOUNDS[0] + WALL, BOARD_BOUNDS[1] + WALL
    open_x, open_y = OPENING_BOUNDS[0] + WALL, OPENING_BOUNDS[1] + WALL
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1640" height="1130" viewBox="-12 -27 377 260" role="img" aria-labelledby="title desc">
  <title id="title">Forest Guardian — 28-wheel irregular layered gear layout</title>
  <desc id="desc">270 by 205 millimeter case, centered 3.4-inch round display, 28 KHK module-one gears in two asymmetrical depth-plane clusters. The drawing is a nominal geometry review, not a fabrication drawing.</desc>
  <style>
    text {{ font-family: DejaVu Sans, sans-serif; fill:#eee0c7; }}
    .bg {{ fill:#101112; }} .case {{ fill:#211b15; stroke:#a77d49; stroke-width:1.2; }}
    .inner {{ fill:none; stroke:#7e694d; stroke-width:.4; stroke-dasharray:1 1.2; }}
    .board {{ fill:#315b60; fill-opacity:.16; stroke:#a5cfcc; stroke-width:.55; stroke-dasharray:2 1.3; }}
    .opening {{ fill:none; stroke:#ffe2a1; stroke-width:.5; stroke-dasharray:1.5 1.3; }}
    .openingB {{ fill:none; stroke:#8ec4c6; stroke-width:.45; stroke-dasharray:1 1; }}
    .bezel {{ fill:#4b3420; stroke:#d6ad6e; stroke-width:.8; }}
    .screen {{ fill:#070c11; stroke:#c79a5d; stroke-width:.5; }}
    .screenline {{ stroke:#be9c69; stroke-width:.25; fill:none; }}
    .mesh {{ stroke:#e8c68b; stroke-width:.35; stroke-dasharray:1.1 1.4; opacity:.42; }}
    .gear path {{ stroke-width:.48; }} .a path {{ fill:#d19b50; fill-opacity:.88; stroke:#ffe2a1; }}
    .b path {{ fill:#9a572b; fill-opacity:.70; stroke:#eab36d; }}
    .a .hub {{ fill:#51391f; stroke:#ffe2a1; stroke-width:.42; }}
    .b .hub {{ fill:#44271c; stroke:#eab36d; stroke-width:.42; }}
    .bore {{ fill:#111; stroke:#f2d7a0; stroke-width:.35; }}
    .title {{ font-size:4.4px; font-weight:bold; }} .subtitle {{ font-size:2.8px; fill:#cdbfa7; }}
    .label {{ font-size:2.6px; }} .small {{ font-size:2.25px; fill:#d7cbb7; }} .tiny {{ font-size:1.85px; fill:#bdb09b; }}
    .dim {{ stroke:#bfad91; stroke-width:.28; fill:none; marker-start:url(#arr); marker-end:url(#arr); }}
    .call {{ stroke:#dbc394; stroke-width:.32; fill:none; }} .panel {{ fill:#171819; stroke:#514839; stroke-width:.5; }}
  </style>
  <defs><marker id="arr" markerWidth="4" markerHeight="4" refX="2" refY="2" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M4,0 L0,2 L4,4" fill="none" stroke="#bfad91" stroke-width=".35"/></marker></defs>
  <rect x="-12" y="-27" width="377" height="260" class="bg"/>
  <text class="title" x="0" y="-18">FOREST GUARDIAN · 3.4-IN ONE-OFF DESIGN CANDIDATE</text>
  <text class="subtitle" x="0" y="-12">Offset open trains · mixed standard gears · separate depth planes · dimensions in mm</text>
  <rect class="case" x="0" y="0" width="{CASE_W}" height="{CASE_H}" rx="3"/>
  <rect class="inner" x="{WALL}" y="{WALL}" width="{INNER_W}" height="{INNER_H}" rx="1"/>
  <circle class="opening" cx="{screen_x}" cy="{screen_y}" r="{A_OPENING_D / 2}"/>
  <rect class="openingB" x="{open_x}" y="{open_y}" width="{OPENING}" height="{OPENING}"/>
  <rect class="board" x="{board_x}" y="{board_y}" width="{BOARD}" height="{BOARD}" rx="2"/>
  <circle class="bezel" cx="{screen_x}" cy="{screen_y}" r="{ACTIVE_D / 2 + 1.4}"/>
  <circle class="screen" cx="{screen_x}" cy="{screen_y}" r="{ACTIVE_D / 2}"/>
  <circle class="screenline" cx="{screen_x}" cy="{screen_y}" r="33"/>
  <path class="screenline" d="M{screen_x - 20},{screen_y} H{screen_x + 20} M{screen_x},{screen_y - 20} V{screen_y + 20}"/>
  <circle cx="{screen_x}" cy="{screen_y}" r="2" fill="#d6ae74"/>
  <text class="tiny" x="{screen_x}" y="{screen_y + 25}" text-anchor="middle">800×800 / Ø87.6 active image</text>
  {draw_links(LAYERS['B'])}
  {draw_links(LAYERS['A'])}
  {draw_gears('B')}
  {draw_gears('A')}
  <circle cx="{screen_x}" cy="{SCREEN_CENTER[1] + WALL + 0}" r="16.5" fill="none" stroke="#fff2d1" stroke-width=".42" stroke-dasharray="1.4 1.1"/>
  <text class="tiny" x="8" y="20">gold circle: A front support opening Ø112</text>
  <text class="tiny" x="8" y="25">blue square: B rear support/display opening 120</text>
  <text class="tiny" x="8" y="30">blue dashed: display board 115×115 behind the gears</text>
  <text class="tiny" x="8" y="35">centered board clearance: {metrics['board_opening_clearance']:.1f}mm per side</text>
  <line class="dim" x1="0" y1="211" x2="{CASE_W}" y2="211"/>
  <text class="small" x="135" y="216" text-anchor="middle">270 outside</text>
  <line class="dim" x1="276" y1="0" x2="276" y2="{CASE_H}"/>
  <text class="small" x="280" y="102.5" transform="rotate(90 280 102.5)" text-anchor="middle">205 outside</text>

  <rect class="panel" x="280" y="0" width="72" height="205" rx="2"/>
  <text class="title" x="284" y="9">LAYOUT SUMMARY</text>
  <text class="label" x="284" y="18">{metrics['gear_count']} wheels / {metrics['shaft_count']} shafts</text>
  <text class="label" x="284" y="24">{metrics['bushing_count']} OILES bushings</text>
  <text class="small" x="284" y="32">{counts_text}</text>
  <text class="small" x="284" y="42">A: 14 wheels · B: 14 wheels</text>
  <text class="small" x="284" y="48">A00/B00: one shared shaft</text>
  <text class="small" x="284" y="54">{metrics['cross_layer_overlaps']} projected gear overlaps &gt;1mm</text>
  <text class="tiny" x="284" y="60">Open upper-right quadrant leaves clear negative space.</text>
  <text class="tiny" x="284" y="65">Only same-plane neighboring wheels mesh.</text>
  <text class="label" x="284" y="78">Clear inside</text>
  <text class="small" x="284" y="84">246×181×121 (walls 12)</text>
  <text class="label" x="284" y="96">Nominal XY checks</text>
  <text class="small" x="284" y="102">Smallest active-screen gap: {metrics['minimum_display_gap']:.1f}</text>
  <text class="small" x="284" y="108">Smallest case margin: {metrics['minimum_case_margin']:.1f}</text>
  <text class="small" x="284" y="114">Smallest support-hole web: {metrics['minimum_bushing_web']:.1f}</text>
  <text class="small" x="284" y="120">Non-mesh clearance: ≥{metrics['minimum_nonmesh_clearance']:.1f}</text>
  <text class="small" x="284" y="126">M1 mesh center error: ≤{metrics['maximum_mesh_error']:.3f}</text>
  <text class="small" x="284" y="132">Coupler / board clearance: {metrics['coupler_board_clearance']:.1f}</text>
  <text class="label" x="284" y="140">Schematic gear cutouts</text>
  <text class="tiny" x="284" y="146">Catalog OD is shown. Tooth outlines</text>
  <text class="tiny" x="284" y="151">are illustrative, not involute geometry.</text>
  <text class="tiny" x="284" y="157">Board/gear 3D clearance is a Z-stack</text>
  <text class="tiny" x="284" y="162">assumption; actual module revision still</text>
  <text class="tiny" x="284" y="167">needs physical inspection.</text>
  <text class="label" x="284" y="181">Not a fabrication release</text>
  <text class="tiny" x="284" y="187">Bushing seats, plate fasteners, gear</text>
  <text class="tiny" x="284" y="192">retention and acoustic/torque tests remain.</text>
  <text class="tiny" x="0" y="224">XY coordinates are relative to the case inside; see the generated axis schedule for case and support-plate datums.</text>
  <text class="tiny" x="0" y="230">28-wheel layout: 3.4-inch IPS, 270×205×145 case, KHK DS1 M1 gears, A Ø112 front opening and B 120-square rear opening.</text>
</svg>'''
    (ROOT / "irregular_layered_gear_layout.svg").write_text(svg, encoding="utf-8")


def write_section() -> None:
    # Z datum is the inside face of the front frame; dimensions use 8 px/mm.
    scale, x0 = 8.0, 60.0
    X = lambda z: x0 + scale * z
    end = X(INNER_D)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" role="img" aria-labelledby="title desc">
  <title id="title">Axial stack for two gear planes, display and motor</title>
  <desc id="desc">Scaled along Z. The front clear carrier plate supports plane A around a 112 millimeter circular opening; the rear plate supports plane B around a 120 millimeter square opening for the nominal 115 by 115 millimeter Waveshare 3.4C board. The display glass CAD datum is z=40; the board depth is not to scale.</desc>
  <style>
    text {{ font-family: DejaVu Sans, sans-serif; fill:#28231e; }}
    .title {{ font-size:28px; font-weight:bold; }} .head {{ font-size:19px; font-weight:bold; }}
    .label {{ font-size:15px; }} .small {{ font-size:13px; fill:#4c463e; }} .tiny {{ font-size:12px; fill:#61594e; }} .inverse {{ fill:#f4e7c9; }}
    .plate {{ fill:#aed4d5; fill-opacity:.55; stroke:#39787c; stroke-width:2; }}
    .gearA {{ fill:#d19b50; stroke:#6c4b25; stroke-width:2; }} .gearB {{ fill:#9a572b; stroke:#44271c; stroke-width:2; }}
    .hub {{ fill:#b17939; stroke:#6c4b25; stroke-width:1.5; }} .hubB {{ fill:#7a4021; stroke:#44271c; stroke-width:1.5; }}
    .bearing {{ fill:#ebd19a; stroke:#76552d; stroke-width:2; }} .shaft {{ fill:#788791; stroke:#38464d; stroke-width:1.5; }}
    .screen {{ fill:#172129; stroke:#bf9457; stroke-width:2; }} .pcb {{ fill:#315b60; stroke:#24464a; stroke-width:2; }}
    .motor {{ fill:#596c79; stroke:#293943; stroke-width:2; }} .coupler {{ fill:#c6c7ba; stroke:#55564d; stroke-width:2; }}
    .dim {{ stroke:#342e28; stroke-width:1.5; fill:none; marker-start:url(#arrow); marker-end:url(#arrow); }}
    .axis {{ stroke:#91918c; stroke-width:1; stroke-dasharray:7 5; }} .note {{ fill:#f6f0e5; stroke:#b5a68f; stroke-width:1.5; }}
  </style>
  <defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto-start-reverse"><path d="M9,0 L0,4.5 L9,9" fill="none" stroke="#342e28" stroke-width="1.2"/></marker></defs>
  <rect width="1500" height="820" fill="#fbfaf6"/>
  <text class="title" x="45" y="48">Axial stack · 270×205×145mm one-off case</text>
  <text class="small" x="45" y="77">Z scale: 8px/mm · Z=0 at the inside face of the front frame · not an assembly drawing</text>
  <text class="head" x="45" y="130">Gear and drive stack at the A00/B00 compound axis</text>
  <text class="small" x="45" y="159">Front / viewer</text>
  <line class="axis" x1="45" y1="265" x2="{end + 35:.0f}" y2="265"/>
  <rect class="plate" x="{X(0):.1f}" y="188" width="{PLATE_T * scale:.1f}" height="155" rx="2"/>
  <rect class="bearing" x="{X(0):.1f}" y="248" width="{BUSHING_L * scale:.1f}" height="34" rx="5"/>
  <rect class="shaft" x="{X(COMPOUND_SHAFT_START_Z):.1f}" y="258" width="{COMPOUND_SHAFT_FINISHED_MM * scale:.1f}" height="14" rx="6"/>
  <rect class="hub" x="{X(9):.1f}" y="242" width="{6 * scale:.1f}" height="46" rx="4"/>
  <rect class="gearA" x="{X(15):.1f}" y="214" width="{6 * scale:.1f}" height="102" rx="3"/>
  <rect class="gearB" x="{X(23):.1f}" y="214" width="{6 * scale:.1f}" height="102" rx="3"/>
  <rect class="hubB" x="{X(29):.1f}" y="242" width="{6 * scale:.1f}" height="46" rx="4"/>
  <rect class="bearing" x="{X(36):.1f}" y="248" width="{BUSHING_L * scale:.1f}" height="34" rx="5"/>
  <rect class="plate" x="{X(36):.1f}" y="188" width="{PLATE_T * scale:.1f}" height="155" rx="2"/>
  <rect class="coupler" x="{X(COUPLER_START_Z):.1f}" y="230" width="{COUPLER_LENGTH_MM * scale:.1f}" height="70" rx="8"/>
  <rect class="shaft" x="{X(MOTOR_FACE_Z - 9):.1f}" y="259" width="{9 * scale:.1f}" height="12" rx="6"/>
  <rect class="motor" x="{X(MOTOR_FACE_Z):.1f}" y="198" width="{MOTOR_LENGTH_MM * scale:.1f}" height="134" rx="9"/>
  <text class="label" x="{X(4):.1f}" y="183" text-anchor="middle">Front support</text>
  <text class="small" x="{X(18):.1f}" y="205" text-anchor="middle">A gear</text>
  <text class="tiny" x="{X(12):.1f}" y="326" text-anchor="middle">hub out</text>
  <text class="small" x="{X(26):.1f}" y="205" text-anchor="middle">B gear</text>
  <text class="tiny" x="{X(32):.1f}" y="326" text-anchor="middle">hub out</text>
  <text class="label" x="{X(40):.1f}" y="183" text-anchor="middle">Rear support</text>
  <text class="small" x="{X(COUPLER_START_Z + COUPLER_LENGTH_MM / 2):.1f}" y="223" text-anchor="middle">NBK MJT-14-RD-4-5</text>
  <text class="small inverse" x="{X(91.5):.1f}" y="265" text-anchor="middle">NEMA-8</text>
  <text class="tiny inverse" x="{X(91.5):.1f}" y="284" text-anchor="middle">33mm body</text>
  <text class="small" x="45" y="368">A/B face centers: 8mm · face width 6mm · tooth-face gap 2mm</text>
  <line class="dim" x1="{X(18):.1f}" y1="390" x2="{X(26):.1f}" y2="390"/>
  <text class="tiny" x="{(X(18)+X(26))/2:.1f}" y="412" text-anchor="middle">8mm</text>
  <line class="dim" x1="{X(15):.1f}" y1="438" x2="{X(21):.1f}" y2="438"/>
  <text class="tiny" x="{(X(15)+X(21))/2:.1f}" y="460" text-anchor="middle">6mm face</text>
  <line class="dim" x1="{X(21):.1f}" y1="486" x2="{X(23):.1f}" y2="486"/>
  <text class="tiny" x="{(X(21)+X(23))/2:.1f}" y="508" text-anchor="middle">2mm gap</text>
  <line class="dim" x1="{X(0):.1f}" y1="545" x2="{X(44):.1f}" y2="545"/>
  <text class="small" x="{(X(0)+X(44))/2:.1f}" y="568" text-anchor="middle">44mm bearing-plate outside span</text>

  <text class="head" x="45" y="626">Display opening through the two supports</text>
  <text class="small" x="45" y="654">Front support: Ø112mm round opening. Rear support: 120×120mm square opening.</text>
  <line class="axis" x1="45" y1="709" x2="{end + 35:.0f}" y2="709"/>
  <rect x="{X(0):.1f}" y="682" width="{PLATE_T * scale:.1f}" height="52" fill="none" stroke="#8baeb0" stroke-dasharray="5 4" stroke-width="2"/>
  <rect x="{X(36):.1f}" y="682" width="{PLATE_T * scale:.1f}" height="52" fill="none" stroke="#8baeb0" stroke-dasharray="5 4" stroke-width="2"/>
  <line x1="{X(40):.1f}" y1="680" x2="{X(40):.1f}" y2="738" stroke="#172129" stroke-width="5"/>
  <rect class="pcb" x="{X(40) + 24:.1f}" y="693" width="250" height="34" rx="5"/>
  <text class="tiny" x="{X(4):.1f}" y="754" text-anchor="middle">front Ø112 opening</text>
  <text class="tiny" x="{X(40):.1f}" y="674" text-anchor="middle">glass datum z=40</text>
  <text class="tiny" x="{X(36):.1f}" y="754" text-anchor="middle">rear 120-square opening</text>
  <text class="tiny inverse" x="{X(60):.1f}" y="716" text-anchor="middle">115×115 nominal board · depth not to scale</text>
  <text class="tiny" x="{X(50):.1f}" y="777">Use 28mm A shafts; verify the actual tips remain clear of glass at z=40.</text>
  <text class="tiny" x="{X(103):.1f}" y="800" text-anchor="middle">motor body ends z={MOTOR_END_Z:.0f} · inside rear wall z=121 · {INNER_D - MOTOR_END_Z:.0f}mm nominal clearance</text>

  <rect class="note" x="1170" y="120" width="285" height="610" rx="8"/>
  <text class="head" x="1195" y="159">Z coordinates</text>
  <text class="label" x="1195" y="198">Front plate</text><text class="small" x="1195" y="221">z=0…8 · 14 bushings · Ø112 opening</text>
  <text class="label" x="1195" y="260">Plane A</text><text class="small" x="1195" y="283">tooth face z=15…21</text><text class="small" x="1195" y="304">face center z=18 · hub toward front</text>
  <text class="label" x="1195" y="345">Plane B</text><text class="small" x="1195" y="368">tooth face z=23…29</text><text class="small" x="1195" y="389">face center z=26 · hub toward rear</text>
  <text class="label" x="1195" y="430">Rear plate</text><text class="small" x="1195" y="453">z=36…44 · 14 bushings · 120 square</text>
  <text class="label" x="1195" y="494">Display and motor</text><text class="small" x="1195" y="517">LCD front datum z=40 (CAD nominal)</text><text class="small" x="1195" y="538">coupler z=48…70 · OD14 · L=7</text><text class="small" x="1195" y="559">5×60 stock → 58.5mm finished</text><text class="small" x="1195" y="580">5mm shaft insertion: 7mm</text><text class="small" x="1195" y="601">4mm motor shaft: 9mm, inserted 7mm</text><text class="small" x="1195" y="622">motor: face z=72 / end z=105 / gap 16</text>
  <text class="tiny" x="1195" y="649">5mm side matches NBK hub length.</text><text class="tiny" x="1195" y="667">Nominal 115 board in 120 opening: 2.5mm/side.</text><text class="tiny" x="1195" y="685">Check depth, ports, and retention before final fit.</text>
</svg>'''
    (ROOT / "layered_gear_axial_section.svg").write_text(svg, encoding="utf-8")


def write_plate_template(layer_key: str) -> None:
    layer = LAYERS[layer_key]
    local_open_x = OPENING_BOUNDS[0] + PLATE_OVERHANG
    local_open_y = OPENING_BOUNDS[1] + PLATE_OVERHANG
    holes = []
    for gear_id, teeth, x, y in layer["gears"]:
        px, py = x + PLATE_OVERHANG, y + PLATE_OVERHANG
        holes.append(
            f'<circle class="hole" cx="{px:.3f}" cy="{py:.3f}" r="3.5"/>'
            f'<path class="cross" d="M{px-2:.3f},{py:.3f} H{px+2:.3f} M{px:.3f},{py-2:.3f} V{py+2:.3f}"/>'
            f'<text class="tiny" x="{px+4:.3f}" y="{py-3:.3f}">{gear_id}</text>'
        )
    opening_markup = (
        f'<circle class="opening" cx="{SCREEN_CENTER[0] + PLATE_OVERHANG:.3f}" '
        f'cy="{SCREEN_CENTER[1] + PLATE_OVERHANG:.3f}" r="{A_OPENING_D / 2:.1f}"/>'
        if layer_key == "A"
        else f'<rect class="opening" x="{local_open_x:.3f}" y="{local_open_y:.3f}" width="{OPENING:.0f}" height="{OPENING:.0f}"/>'
    )
    opening_label = "Ø112 circular opening" if layer_key == "A" else "120×120mm square opening"
    support_count = len(layer["gears"])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="760" viewBox="-18 -28 288 232" role="img" aria-labelledby="title desc">
  <title id="title">Support plate {layer_key} nominal hole pattern</title>
  <desc id="desc">Nominal 252 by 187 by 8 millimeter clear polycarbonate plate, {opening_label} and nominal seven millimeter bushing seats for {support_count} gear axes in plane {layer_key}. Not a manufacturing file.</desc>
  <style>text{{font-family:DejaVu Sans,sans-serif;fill:#29251f}}.title{{font-size:5px;font-weight:bold}}.small{{font-size:3px}}.tiny{{font-size:2.4px;fill:#625c54}}.plate{{fill:#d7eeee;stroke:#387a7c;stroke-width:.7}}.opening{{fill:#fff;stroke:#39787c;stroke-width:.5;stroke-dasharray:2 1}}.hole{{fill:#fff;stroke:#af562d;stroke-width:.55}}.cross{{stroke:#af562d;stroke-width:.25}}</style>
  <rect x="-18" y="-28" width="288" height="232" fill="#faf9f4"/>
  <text class="title" x="0" y="-18">PLANE {layer_key} · {PLATE_W:.0f}×{PLATE_H:.0f}×8mm SUPPORT PLATE · NOMINAL ONLY</text>
  <rect class="plate" x="0" y="0" width="{PLATE_W:.0f}" height="{PLATE_H:.0f}"/>
  {opening_markup}
  {''.join(holes)}
  <text class="small" x="0" y="193">{support_count} bushing axes; gear coordinates are case-inside coordinates +3mm.</text>
  <text class="tiny" x="0" y="198">Case capture: 3mm-deep × 8.2mm-wide perimeter grooves; material/fit must be tested.</text>
  <text class="tiny" x="0" y="203">Bushing seat Ø7 H7 is reference only; test OILES press-fit in the chosen plate before cutting.</text>
</svg>'''
    (ROOT / f"gear_support_plate_{layer_key}.svg").write_text(svg, encoding="utf-8")


def write_axis_schedule() -> None:
    path = ROOT / "gear_axis_schedule.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "layer", "gear_id", "KHK_part", "teeth", "module_mm",
            "inside_x_mm", "inside_y_mm", "case_x_mm", "case_y_mm",
            "plate_x_mm", "plate_y_mm", "shaft_group", "shared_shaft_flag",
            "shaft_stock_mm", "shaft_finished_mm", "bushing_position", "previous_center_distance_mm",
        ])
        for layer_key, layer in LAYERS.items():
            for index, (gear_id, teeth, x, y) in enumerate(layer["gears"]):
                previous_distance = ""
                if index:
                    previous = layer["gears"][index - 1]
                    previous_distance = f"{math.hypot(x - previous[2], y - previous[3]):.3f}"
                writer.writerow([
                    layer_key, gear_id, f"DS1-{teeth}", teeth, f"{MODULE:.1f}",
                    f"{x:.3f}", f"{y:.3f}", f"{x + WALL:.3f}", f"{y + WALL:.3f}",
                    f"{x + PLATE_OVERHANG:.3f}", f"{y + PLATE_OVERHANG:.3f}",
                    "compound-01" if gear_id in {"A00", "B00"} else gear_id,
                    "shared" if gear_id in {"A00", "B00"} else "single",
                    f"{COMPOUND_SHAFT_STOCK_MM:.1f}" if gear_id in {"A00", "B00"} else "28.0",
                    f"{COMPOUND_SHAFT_FINISHED_MM:.1f}" if gear_id in {"A00", "B00"} else "28.0",
                    "front+rear" if gear_id in {"A00", "B00"} else ("front" if layer_key == "A" else "rear"),
                    previous_distance,
                ])


def main() -> None:
    metrics = validate()
    write_plan(metrics)
    write_section()
    write_plate_template("A")
    write_plate_template("B")
    write_axis_schedule()
    print(
        f"28 wheels / 27 shafts / 28 bushings; "
        f"display-board clearance={metrics['board_opening_clearance']:.2f}mm/side; "
        f"coupler/board clearance={metrics['coupler_board_clearance']:.2f}mm; "
        f"cross-layer overlaps={metrics['cross_layer_overlaps']}; "
        f"min cross-axis separation={metrics['minimum_cross_axis_separation']:.2f}mm; "
        f"min edge={metrics['minimum_case_margin']:.2f}mm; "
        f"min display gap={metrics['minimum_display_gap']:.2f}mm; "
        f"min opening web={metrics['minimum_bushing_web']:.2f}mm; "
        f"min non-mesh clearance={metrics['minimum_nonmesh_clearance']:.2f}mm; "
        f"max mesh error={metrics['maximum_mesh_error']:.4f}mm"
    )


if __name__ == "__main__":
    main()
