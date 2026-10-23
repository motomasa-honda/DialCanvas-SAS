#!/usr/bin/env python3
"""Render nominal BSS20 support-plate maps from the generated axis schedule."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "gear_axis_schedule_bss20_candidate.csv"
PLATE_W, PLATE_H, PLATE_T = 252.0, 187.0, 8.0


def read_rows() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 28:
        raise ValueError("BSS20 axis schedule must contain 28 rows")
    return rows


def render(layer: str, rows: list[dict[str, str]]) -> str:
    gear_rows = [row for row in rows if row["layer"] == layer]
    if len(gear_rows) != 14:
        raise ValueError(f"layer {layer} must contain 14 axes")
    axial = "z=29…37" if layer == "A" else "z=70…78"
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="850" viewBox="-20 -34 292 228" role="img" aria-labelledby="title desc">',
        f'<title id="title">BSS20 support plate {layer}</title>',
        '<desc id="desc">Nominal 252 by 187 by 8 millimeter support plate with fourteen OILES 80B-0608 seats. Plate A also has four display-carrier M3 clearance holes. Not a manufacturing drawing.</desc>',
        '<style>text{font-family:DejaVu Sans,sans-serif;fill:#29251f}.title{font-size:5px;font-weight:bold}.small{font-size:3px}.tiny{font-size:2.4px;fill:#625c54}.plate{fill:#eaf2ef;stroke:#477a78;stroke-width:.7}.opening{fill:#fff;stroke:#39787c;stroke-width:.5;stroke-dasharray:2 1}.seat{fill:#b8dbd8;stroke:#1c7475;stroke-width:.65}.cross{stroke:#574e42;stroke-width:.25}.carrier{fill:#d19a40;stroke:#7b4c16;stroke-width:.55}</style>',
        '<rect x="-20" y="-34" width="292" height="228" fill="#faf9f4"/>',
        f'<text class="title" x="0" y="-23">PLANE {layer} · {PLATE_W:.0f}×{PLATE_H:.0f}×{PLATE_T:.0f} mm · {axial} · PROVISIONAL</text>',
        f'<rect class="plate" x="0" y="0" width="{PLATE_W:.0f}" height="{PLATE_H:.0f}"/>',
    ]
    if layer == "A":
        out.append('<circle class="opening" cx="126" cy="93.5" r="59.5"/>')
        out.append('<g class="carrier"><circle cx="46" cy="13.5" r="1.7"/><circle cx="206" cy="13.5" r="1.7"/><circle cx="46" cy="173.5" r="1.7"/><circle cx="206" cy="173.5" r="1.7"/></g>')
    else:
        out.append('<rect class="opening" x="66" y="33.5" width="120" height="120"/>')
    for row in gear_rows:
        x, y = float(row["plate_x_mm"]), float(row["plate_y_mm"])
        out.append(f'<circle class="seat" cx="{x:.3f}" cy="{y:.3f}" r="4"/>')
        out.append(f'<path class="cross" d="M{x-1.4:.3f},{y:.3f} H{x+1.4:.3f} M{x:.3f},{y-1.4:.3f} V{y+1.4:.3f}"/>')
        out.append(f'<text class="tiny" x="{x+4.2:.3f}" y="{y-3.1:.3f}">{row["gear_id"]}</text>')
    out.extend([
        '<circle class="seat" cx="5" cy="170" r="4"/>',
        '<text class="small" x="12" y="171">14 × OILES 80B-0608 · nominal housing seat Ø8 H7</text>',
        '<text class="tiny" x="0" y="194">Plate datum: outer-case origin + (9, 9) mm; axis coordinates are from CSV.</text>',
        '<text class="tiny" x="0" y="199">Use the catalog Ø8 H7 seat on the finished plate; inspect fit and free rotation during assembly.</text>',
        f'<text class="tiny" x="0" y="204">{"Orange dots: display-carrier M3 clearance holes, case X/Y=±80mm, Ø3.4." if layer == "A" else "Plate B has no display-carrier anchors in this arrangement."}</text>',
        '<text class="tiny" x="0" y="209">Transparent PC is a one-off material candidate; drawing is not CNC/CAM output.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def main() -> None:
    rows = read_rows()
    for layer in ("A", "B"):
        path = HERE / f"gear_support_plate_{layer}_bss20_candidate.svg"
        path.write_text(render(layer, rows), encoding="utf-8")
        print(path.name)


if __name__ == "__main__":
    main()
