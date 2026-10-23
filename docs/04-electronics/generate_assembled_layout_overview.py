#!/usr/bin/env python3
"""Generate the current assembled-layout overview from the BSS20 candidate schedule."""

from __future__ import annotations

import csv
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
MECH = HERE.parent / "03-mechanical"
SCHEDULE = MECH / "gear_axis_schedule_bss20_candidate.csv"
OUT = HERE / "assembled-layout-overview-candidate-v0.1.svg"

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def tag(name: str) -> str:
    return f"{{{NS}}}{name}"


def add(parent, name, attrs=None, text=None):
    element = ET.SubElement(parent, tag(name), attrs or {})
    if text is not None:
        element.text = str(text)
    return element


def line(parent, x1, y1, x2, y2, cls="a-rule", **extra):
    attrs = {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), "class": cls}
    attrs.update({key.replace("_", "-"): str(value) for key, value in extra.items()})
    return add(parent, "line", attrs)


def rect(parent, x, y, width, height, cls=None, **extra):
    attrs = {"x": str(x), "y": str(y), "width": str(width), "height": str(height)}
    if cls:
        attrs["class"] = cls
    attrs.update({key.replace("_", "-"): str(value) for key, value in extra.items()})
    return add(parent, "rect", attrs)


def circle(parent, cx, cy, r, cls=None, **extra):
    attrs = {"cx": str(cx), "cy": str(cy), "r": str(r)}
    if cls:
        attrs["class"] = cls
    attrs.update({key.replace("_", "-"): str(value) for key, value in extra.items()})
    return add(parent, "circle", attrs)


def text(parent, x, y, value, cls="a-body", **extra):
    attrs = {"x": str(x), "y": str(y), "class": cls}
    attrs.update({key.replace("_", "-"): str(v) for key, v in extra.items()})
    return add(parent, "text", attrs, value)


def panel(root, x, y, w, h, title_text, subtitle):
    rect(root, x, y, w, h, "a-panel", rx="12")
    text(root, x + 24, y + 37, title_text, "a-panel-title")
    text(root, x + 24, y + 63, subtitle, "a-panel-sub")


def arrow_dim(parent, x1, y1, x2, y2, label, label_x, label_y, vertical=False):
    line(parent, x1, y1, x2, y2, "a-dim", marker_start="url(#arrow)", marker_end="url(#arrow)")
    attrs = {"text_anchor": "middle"}
    if vertical:
        attrs["transform"] = f"rotate(-90 {label_x} {label_y})"
    text(parent, label_x, label_y, label, "a-dim-text", **attrs)


def load_gears():
    with SCHEDULE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    gears = []
    for row in rows:
        if row["layer"] not in {"A", "B"}:
            continue
        gears.append(
            {
                "layer": row["layer"],
                "id": row["gear_id"],
                "x": float(row["case_x_mm"]) - 135.0,
                "y": 102.5 - float(row["case_y_mm"]),
                "teeth": int(row["teeth"]),
            }
        )
    if len(gears) != 28:
        raise ValueError(f"Expected the current 28-position calculation example, found {len(gears)} rows")
    return gears


def draw_front(root, gears):
    # Plan is based on the current gear-axis schedule; gear tooth profiles are simplified to OD envelopes.
    scale = 2.0
    cx, cy = 420.0, 418.0
    outer_w, outer_h = 270 * scale, 205 * scale
    left, top = cx - outer_w / 2, cy - outer_h / 2
    inner_left, inner_top = cx - 246 * scale / 2, cy - 181 * scale / 2
    rect(root, left, top, outer_w, outer_h, "a-walnut", rx="8")
    rect(root, inner_left, inner_top, 246 * scale, 181 * scale, "a-window", rx="2")

    # The support plates are each 252 x 187 mm and sit partly in the case grooves.
    rect(root, cx - 252 * scale / 2, cy - 187 * scale / 2, 252 * scale, 187 * scale,
         "a-support-outline", rx="2")

    # Integrated display/main-control board and its active circular screen.
    circle(root, cx, cy, 115 * scale / 2, "a-display-shell")
    circle(root, cx, cy, 87.6 * scale / 2, "a-screen")
    circle(root, cx, cy, 35.0 * scale, "a-dial-ring")
    for i in range(12):
        import math
        angle = math.radians(i * 30 - 90)
        r1, r2 = 31.5 * scale, 34.5 * scale
        line(root, cx + r1 * math.cos(angle), cy + r1 * math.sin(angle),
             cx + r2 * math.cos(angle), cy + r2 * math.sin(angle), "a-tick")
    line(root, cx, cy, cx + 5 * scale, cy - 23 * scale, "a-hand-hour")
    line(root, cx, cy, cx + 22 * scale, cy + 8 * scale, "a-hand-minute")
    circle(root, cx, cy, 2.0 * scale, "a-hand-hub")

    # Rear gear plane first, then the front plane, matching their physical order.
    for gear in sorted(gears, key=lambda item: (item["layer"] == "A", item["id"])):
        gx, gy = cx + gear["x"] * scale, cy - gear["y"] * scale
        cls = "a-gear-a" if gear["layer"] == "A" else "a-gear-b"
        circle(root, gx, gy, 11 * scale, cls)
        circle(root, gx, gy, 2.5 * scale, "a-gear-bore")

    # Outer frame and internal support outline are called out without hiding the arrangement.
    rect(root, left, top, outer_w, outer_h, "a-case-outline", rx="8")
    rect(root, inner_left, inner_top, 246 * scale, 181 * scale, "a-opening-outline", rx="2")

    # Motor/compound-axis marker at the current A00/B00 shared axis.
    mx, my = cx, cy - 68 * scale
    circle(root, mx, my, 5.5 * scale, "a-motor-axis")
    line(root, mx + 10, my - 10, 680, 200, "a-callout")
    text(root, 700, 196, "モーター軸", "a-note-strong")
    text(root, 700, 219, "複合軸", "a-note")
    line(root, cx + 55 * scale, cy - 5 * scale, 680, 324, "a-callout")
    text(root, 700, 320, "3.4C基板", "a-note-strong")
    text(root, 700, 343, "表示・制御一体", "a-note")

    # Dimensions and compact front-view legend.
    arrow_dim(root, left, top - 20, left + outer_w, top - 20, "270 mm（参考）", cx, top - 28)
    arrow_dim(root, left - 20, top, left - 20, top + outer_h, "205 mm（参考）", left - 30, cy, vertical=True)
    text(root, 58, 688, "現在の歯車配置は計算例です（A層14個＋B層14個）。", "a-note-strong")
    text(root, 58, 710, "歯車数・軸数は製品仕様で固定されていません。", "a-note")
    circle(root, 77, 731, 10, "a-gear-a")
    text(root, 95, 737, "A層：z=24–30mm（前側）", "a-note")
    circle(root, 355, 731, 10, "a-gear-b")
    text(root, 373, 737, "B層：z=33–39mm（後側）", "a-note")
    rect(root, 622, 721, 22, 18, "a-support-outline")
    text(root, 652, 737, "透明支持板", "a-note")
    text(root, 58, 779, "歯車は外径Ø22mmの円で表示。歯形・振れ・配線・固定部品は省略。", "a-note")


def draw_side(root):
    # s is distance from the exterior front face; s = z + 12 mm in the current CAD.
    scale = 1.9
    x0, top = 858.0, 273.0
    h = 205 * scale
    bottom = top + h
    x = lambda s: x0 + s * scale
    yy = lambda y: top + (102.5 - y) * scale

    # Case envelope, inner cavity rails, clear front guard, and removable rear cover.
    rect(root, x(0), top, 145 * scale, h, "a-side-outline")
    rect(root, x(12), top, 121 * scale, 12 * scale, "a-case-wall")
    rect(root, x(12), bottom - 12 * scale, 121 * scale, 12 * scale, "a-case-wall")
    rect(root, x(133), top, 12 * scale, h, "a-rear-cover")
    rect(root, x(9), top, 3 * scale, h, "a-guard")

    # Plate sections: openings leave the center clear for the display module.
    center_top = yy(56)
    center_bottom = yy(-56)
    rect(root, x(19), top + 12 * scale, 8 * scale, center_top - (top + 12 * scale), "a-plate-a")
    rect(root, x(19), center_bottom, 8 * scale, bottom - 12 * scale - center_bottom, "a-plate-a")
    b_top, b_bottom = yy(60), yy(-60)
    rect(root, x(60), top + 12 * scale, 8 * scale, b_top - (top + 12 * scale), "a-plate-b")
    rect(root, x(60), b_bottom, 8 * scale, bottom - 12 * scale - b_bottom, "a-plate-b")

    # Display cylinder envelope through the rear support aperture.
    display_left, display_right = x(56.5), x(72)
    display_top, display_bottom = yy(57.5), yy(-57.5)
    rect(root, display_left, display_top, display_right - display_left,
         display_bottom - display_top, "a-display-side", rx="8")

    # Gear cross-sections at the shared A00/B00 compound axis.
    gear_cy = yy(68)
    rect(root, x(36), gear_cy - 11 * scale, 6 * scale, 22 * scale, "a-gear-a-side", rx="3")
    rect(root, x(45), gear_cy - 11 * scale, 6 * scale, 22 * scale, "a-gear-b-side", rx="3")
    line(root, x(42), gear_cy, x(45), gear_cy, "a-shaft")

    # Candidate 3 mm carrier and motor drive set from the envelope model.
    rect(root, x(74), yy(44), 3 * scale, yy(-44) - yy(44), "a-carrier-side")
    rect(root, x(69), gear_cy - 7 * scale, 22 * scale, 14 * scale, "a-coupler-side", rx="5")
    rect(root, x(93), gear_cy - 10 * scale, 33 * scale, 20 * scale, "a-motor-side", rx="4")
    line(root, x(91), gear_cy, x(93), gear_cy, "a-shaft")

    # Centerline, depth dimensions, and labels.
    line(root, x(0), yy(0), x(145), yy(0), "a-centerline")
    line(root, x(72), top - 25, x(133), top - 25, "a-dim", marker_start="url(#arrow)", marker_end="url(#arrow)")
    text(root, (x(72) + x(133)) / 2, top - 34, "表示器背面〜背面電装面：61mm", "a-dim-text", text_anchor="middle")
    line(root, x(126), gear_cy - 42, x(133), gear_cy - 42, "a-dim", marker_start="url(#arrow)", marker_end="url(#arrow)")
    text(root, (x(126) + x(133)) / 2, gear_cy - 50, "7 mm", "a-dim-text", text_anchor="middle")
    arrow_dim(root, x(0), bottom + 32, x(145), bottom + 32, "145mm（参考）", (x(0) + x(145)) / 2, bottom + 52)
    text(root, x(0), bottom + 76, "前面", "a-note-strong")
    text(root, x(145), bottom + 76, "背面", "a-note-strong", text_anchor="end")

    # Layer labels remain outside the physical stack so the section stays readable.
    text(root, 1150, 352, "単一モーター", "a-note-strong")
    text(root, 1150, 373, "NEMA-8候補", "a-note")
    line(root, x(109), gear_cy - 8, 1142, 366, "a-callout")
    text(root, 1150, 414, "カップリング／複合軸", "a-note-strong")
    line(root, x(80), gear_cy + 12, 1142, 420, "a-callout")
    text(root, 1150, 478, "歯車層A：z=24–30", "a-note-strong")
    text(root, 1150, 500, "歯車層B：z=33–39", "a-note-strong")
    line(root, x(48), gear_cy - 3, 1142, 484, "a-callout")
    text(root, 1150, 550, "3.4C一体基板", "a-note-strong")
    text(root, 1150, 572, "前面ガラス：z=44.5", "a-note")
    line(root, display_right, yy(8), 1142, 557, "a-callout")
    text(root, 1150, 628, "支持板A：z=7–15", "a-note")
    text(root, 1150, 650, "支持板B：z=48–56", "a-note")
    line(root, x(64), yy(-60), 1142, 635, "a-callout")
    text(root, 1150, 700, "着脱式背面カバー", "a-note-strong")
    text(root, 1150, 722, "補助電装は内面に配置", "a-note")
    line(root, x(133), yy(-36), 1142, 706, "a-callout")

    text(root, 858, 820, "模式断面。ケーブル経路・整備空間は未確認。", "a-note")


def draw_rear(root):
    # Simplified plan view using the existing rear layout's candidate centers and allocation bounds.
    s = 1.35
    cx, cy = 1682.0, 430.0
    case_w, case_h = 270 * s, 205 * s
    x = lambda mm: cx + mm * s
    y = lambda mm: cy - mm * s
    rect(root, cx - case_w / 2, cy - case_h / 2, case_w, case_h, "a-rear-outline", rx="5")
    rect(root, x(-123), y(90.5), 246 * s, 181 * s, "a-rear-inner", rx="2")
    text(root, cx, cy + case_h / 2 + 22, "背面カバー外形：270×205mm（暫定）", "a-mini", text_anchor="middle")

    # TI area is only an allocation; dimensions of the evaluation board have not been confirmed.
    rect(root, x(-118), y(35), 125 * s, 120 * s, "a-reserve", rx="6")
    text(root, x(-112), y(35) + 26, "TI基板枠", "a-mini-strong")
    text(root, x(-112), y(35) + 47, "125×120mm枠", "a-mini")
    text(root, x(-112), y(35) + 68, "基板外形ではない", "a-mini")

    # Shared service zone for four carriers and an unsized fuse/switch reserve.
    wx, wy = x(15), y(35)
    rect(root, wx, wy, 100 * s, 120 * s, "a-service-zone", rx="5")
    # WAGO mounting carrier footprints are shown rotated; operating clearance is excluded.
    carrier_w, carrier_h = 23.7 * s, 52.8 * s
    positions = [(wx + 8, wy + 8), (wx + 48, wy + 8), (wx + 8, wy + 84), (wx + 48, wy + 84)]
    for index, (px, py) in enumerate(positions, 1):
        rect(root, px, py, carrier_w, carrier_h, "a-wago", rx="3")
        text(root, px + carrier_w / 2, py + carrier_h / 2 + 4, f"W{index}", "a-mini", text_anchor="middle")
    rect(root, wx + 101, wy + 8, 31, 146, "a-unselected", rx="3")
    text(root, wx + 116.5, wy + 86, "F", "a-mini-strong", text_anchor="middle")

    def board(px, py, bw, bh, title, subtitle, klass="a-board"):
        rect(root, px, py, bw, bh, klass, rx="3")
        text(root, px + 4, py + 13, title, "a-mini-strong")
        if subtitle:
            text(root, px + 4, py + 26, subtitle, "a-mini")

    board(x(-86) - 12.25 * s, y(58) - 10.1 * s, 24.5 * s, 20.2 * s, "HUSB", "")
    board(x(-48) - 8.9 * s, y(58) - 10.15 * s, 17.8 * s, 20.3 * s, "5V", "")
    board(x(85) - 11.5 * s, y(50) - 8.8 * s, 23 * s, 17.6 * s, "RTC", "")
    board(x(35) - 13.3 * s, y(68) - 12.05 * s, 26.6 * s, 24.1 * s, "DRV", "", "a-driver")
    rect(root, x(0) - 10 * s, y(68) - 10 * s, 20 * s, 20 * s, "a-projection", rx="3")
    text(root, x(0), y(68) + 4, "M", "a-mini-strong", text_anchor="middle")

    # A compact legend occupies the free right edge of this view.
    text(root, 1890, 320, "背面電装", "a-mini-strong")
    text(root, 1890, 350, "HUSB：PD入力", "a-mini")
    text(root, 1890, 372, "5V：DC/DC", "a-mini")
    text(root, 1890, 394, "RTC：DS3231", "a-mini")
    text(root, 1890, 416, "DRV：TMC2209", "a-mini")
    text(root, 1890, 438, "WAGO取付台×4", "a-mini")
    text(root, 1890, 460, "ヒューズ保持具", "a-mini")
    text(root, 1890, 481, "未選定", "a-mini")
    text(root, 1890, 519, "破線枠は割当範囲", "a-mini-strong")
    text(root, 1890, 540, "部品外形ではありません", "a-mini")
    text(root, 1890, 576, "モーター軸投影", "a-mini")

    text(root, 1443, 630, "補助電装は着脱式背面カバー内面に配置する案。", "a-note-strong")
    text(root, 1443, 655, "TI枠は割当領域。WAGO×4の配線・レバー操作空間は含みません。", "a-note")
    text(root, 1443, 681, "3.4C一体基板はこの面から約61mm前方。", "a-note")
    text(root, 1443, 715, "未確定：配線、保持具、ブラケット、ケース開口。", "a-note")


def build():
    root = ET.Element(tag("svg"), {
        "width": "2100", "height": "1390", "viewBox": "0 0 2100 1390",
        "role": "img", "aria-labelledby": "title desc",
        "{http://www.w3.org/XML/1998/namespace}lang": "ja"
    })
    add(root, "title", {"id": "title"}, "Forest Guardian 内部配置図候補 v0.1")
    add(root, "desc", {"id": "desc"}, "正面透視配置、側面断面、背面カバー内側の補助電装配置候補を示す三面図です。")
    defs = add(root, "defs")
    style = """
      text { font-family: 'Noto Sans CJK JP', 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif; fill: #29333a; }
      .a-title { font-size: 31px; font-weight: 700; }
      .a-subtitle { font-size: 17px; fill: #58646d; }
      .a-panel { fill: #fff; stroke: #ccd2d4; stroke-width: 2; }
      .a-panel-title { font-size: 23px; font-weight: 700; }
      .a-panel-sub { font-size: 15px; fill: #69747b; }
      .a-body { font-size: 17px; }
      .a-note { font-size: 15px; fill: #52606a; }
      .a-note-strong { font-size: 16px; font-weight: 700; fill: #36424a; }
      .a-rule { stroke: #9ba5aa; stroke-width: 1.5; }
      .a-callout { stroke: #6e7a82; stroke-width: 1.4; fill: none; }
      .a-dim { stroke: #4d6876; stroke-width: 1.5; fill: none; }
      .a-dim-text { font-size: 14px; font-weight: 600; fill: #405f70; }
      .a-walnut { fill: #926c4f; stroke: #5d402e; stroke-width: 2; }
      .a-window { fill: #f6f6f2; stroke: #c8c8bd; stroke-width: 1.5; }
      .a-case-outline { fill: none; stroke: #543b2b; stroke-width: 3; }
      .a-opening-outline { fill: none; stroke: #d2c5b6; stroke-width: 1.5; }
      .a-support-outline { fill: none; stroke: #4e9690; stroke-width: 2; stroke-dasharray: 9 6; }
      .a-display-shell { fill: #d4ded9; stroke: #34766f; stroke-width: 2; }
      .a-screen { fill: #1c292d; stroke: #596a6b; stroke-width: 2; }
      .a-dial-ring { fill: none; stroke: #a98b5e; stroke-width: 1.5; }
      .a-tick { stroke: #d9bc84; stroke-width: 1.6; }
      .a-hand-hour { stroke: #e6d4ac; stroke-width: 4; stroke-linecap: round; }
      .a-hand-minute { stroke: #e6d4ac; stroke-width: 2.5; stroke-linecap: round; }
      .a-hand-hub { fill: #dfa851; stroke: #33291e; stroke-width: 1; }
      .a-gear-a { fill: #d4a047; fill-opacity: .91; stroke: #80551e; stroke-width: 1.5; }
      .a-gear-b { fill: #946247; fill-opacity: .88; stroke: #5c3828; stroke-width: 1.5; }
      .a-gear-bore { fill: #f5ead5; stroke: #614a36; stroke-width: 1; }
      .a-motor-axis { fill: #4d4d56; stroke: #f2e5cc; stroke-width: 2; }
      .a-side-outline { fill: #fbfaf7; stroke: #574738; stroke-width: 2.5; }
      .a-case-wall { fill: #8b674d; stroke: #684b36; stroke-width: 1; }
      .a-rear-cover { fill: #ad886b; stroke: #6e5039; stroke-width: 1.5; }
      .a-guard { fill: #d8eff0; fill-opacity: .65; stroke: #57969b; stroke-width: 1.4; }
      .a-plate-a { fill: #b8d8d1; fill-opacity: .8; stroke: #4e9690; stroke-width: 1; }
      .a-plate-b { fill: #c6dfd9; fill-opacity: .8; stroke: #4e9690; stroke-width: 1; }
      .a-display-side { fill: #77aaa7; fill-opacity: .83; stroke: #34766f; stroke-width: 2; }
      .a-gear-a-side { fill: #d4a047; stroke: #80551e; stroke-width: 1.5; }
      .a-gear-b-side { fill: #946247; stroke: #5c3828; stroke-width: 1.5; }
      .a-carrier-side { fill: #d7ad6d; fill-opacity: .8; stroke: #9a722f; stroke-width: 1.3; stroke-dasharray: 4 3; }
      .a-coupler-side { fill: #9ba3a3; stroke: #515d62; stroke-width: 1.5; }
      .a-motor-side { fill: #424d55; stroke: #252e34; stroke-width: 2; }
      .a-shaft { stroke: #565e60; stroke-width: 4; }
      .a-centerline { stroke: #aaa; stroke-width: 1; stroke-dasharray: 6 5; }
      .a-warning { fill: #fbf3e4; stroke: #d4b579; stroke-width: 1.5; }
      .a-rear-outline { fill: #eee8df; stroke: #6f5b49; stroke-width: 2; }
      .a-rear-inner { fill: #faf9f6; stroke: #ad9b88; stroke-width: 1.4; stroke-dasharray: 6 4; }
      .a-reserve { fill: #fff1ce; stroke: #b78625; stroke-width: 1.7; stroke-dasharray: 7 4; }
      .a-service-zone { fill: #e8efdb; stroke: #718957; stroke-width: 1.5; stroke-dasharray: 5 4; }
      .a-wago { fill: #dce7cd; stroke: #718957; stroke-width: 1.3; }
      .a-unselected { fill: #f6dddd; stroke: #aa5959; stroke-width: 1.3; stroke-dasharray: 4 3; }
      .a-board { fill: #d9e7ef; stroke: #54788d; stroke-width: 1.4; }
      .a-driver { fill: #e5d9f0; stroke: #745493; stroke-width: 1.4; }
      .a-projection { fill: #f6dddd; fill-opacity: .55; stroke: #aa5959; stroke-width: 1.4; stroke-dasharray: 4 3; }
      .a-mini { font-size: 12px; fill: #46515b; }
      .a-mini-strong { font-size: 13px; font-weight: 700; fill: #36424a; }
      .a-footer { font-size: 15px; fill: #4d5961; }
      .a-footer-strong { font-size: 17px; font-weight: 700; fill: #3f4b52; }
      #arrow { }
    """
    add(defs, "style", text=style)
    marker = add(defs, "marker", {"id": "arrow", "markerWidth": "8", "markerHeight": "8", "refX": "4", "refY": "4", "orient": "auto-start-reverse", "markerUnits": "strokeWidth"})
    add(marker, "path", {"d": "M 0 0 L 8 4 L 0 8 z", "fill": "#4d6876"})

    rect(root, 0, 0, 2100, 1390, fill="#f2f4f3")
    text(root, 34, 49, "Forest Guardian / DialCanvas Desk Edition", "a-title")
    text(root, 36, 78, "組立状態の内部配置候補 v0.1｜正面・側面断面・背面カバー内側", "a-subtitle")

    panel(root, 25, 105, 785, 835, "1  正面から内部を見る", "前面ガード越しの配置｜歯車表に基づく候補")
    panel(root, 825, 105, 570, 835, "2  側面断面", "前面から背面への層順と奥行")
    panel(root, 1410, 105, 665, 835, "3  背面カバー内側", "着脱式カバー内面の補助電装配置候補")

    gears = load_gears()
    draw_front(root, gears)
    draw_side(root)
    draw_rear(root)

    rect(root, 25, 963, 2050, 395, "a-warning", rx="12")
    text(root, 52, 1007, "この図が示す構成", "a-footer-strong")
    text(root, 52, 1040, "表示・主制御は前面のWaveshare ESP32-P4 3.4C一体基板。単一モーターで装飾歯車列を動かす案です。", "a-footer")
    text(root, 52, 1070, "電源変換、RTC、モータードライバー、分岐端子は着脱式背面カバー内面に配置。配線経路は未確定です。", "a-footer")
    text(root, 52, 1125, "未確定・未確認", "a-footer-strong")
    text(root, 52, 1158, "外箱270×205×145mmは暫定。TI基板の適合、コネクター／ケーブル、ヒューズ・スイッチ保持具、工具空間、熱、配線は未確認です。", "a-footer")
    text(root, 52, 1188, "ケース開口・配線・取付部品の加工には使わないでください。実機組立、物理試験、製造リリースは未実施です。", "a-footer")
    line(root, 52, 1214, 2045, 1214, "a-rule")
    text(root, 52, 1251, "色：黄土／茶＝歯車層｜青緑＝表示器・透明支持板｜紫／黄＝背面基板・割当枠｜破線＝候補位置", "a-footer")
    text(root, 52, 1290, "参照：design-baseline-v0.21.md / bss20_clock_envelope_review.scad / gear_axis_schedule_bss20_candidate.csv / rear-harness-and-mount-candidate-v0.1.md", "a-footer")
    text(root, 52, 1325, "設計概要のみ — 購入・加工用の図面ではありません", "a-footer-strong")

    ET.ElementTree(root).write(OUT, encoding="utf-8", xml_declaration=True)
    print(OUT)


if __name__ == "__main__":
    build()
