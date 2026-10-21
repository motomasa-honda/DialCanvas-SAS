#!/usr/bin/env python3
"""Generate nominal mixed 6mm/5mm bearing-seat maps for the 21-brass option."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "gear_axis_schedule.csv"
BRASS_TEETH = {18, 20}


def read_rows() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def render_plate(layer: str, rows: list[dict[str, str]]) -> str:
    plate_rows = [r for r in rows if r["layer"] == layer]
    assert len(plate_rows) == 14
    brass_count = sum(int(r["teeth"]) in BRASS_TEETH for r in plate_rows)
    pom_count = len(plate_rows) - brass_count
    axial = "z=0-8" if layer == "A" else "z=40-48"
    title = f"PLANE {layer} · 252×187×8mm · {axial} · NOMINAL ONLY"
    output = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="820" viewBox="-18 -32 300 222" role="img" aria-labelledby="title desc">',
        f'<title id="title">Plane {layer} brass hybrid support seat map</title>',
        '<desc id="desc">Nominal support plate seat layout for the 21-brass, 7-POM gear candidate. D8 seats use 80B-0608; D7 seats use 80B-0508. Not a manufacturing file.</desc>',
        '<style>',
        'text{font-family:"DejaVu Sans",sans-serif;fill:#29251f}.title{font-size:5px;font-weight:bold}',
        '.small{font-size:3px}.tiny{font-size:2.4px;fill:#625c54}',
        '.plate{fill:#d7eeee;stroke:#387a7c;stroke-width:.7}',
        '.opening{fill:#fff;stroke:#39787c;stroke-width:.5;stroke-dasharray:2 1}',
        '.bss{fill:#f5d891;stroke:#9d641c;stroke-width:.65}',
        '.pom{fill:#fff;stroke:#557f93;stroke-width:.65}',
        '.cross{stroke:#5b5144;stroke-width:.25}',
        '</style>',
        '<rect x="-18" y="-32" width="300" height="222" fill="#faf9f4"/>',
        f'<text class="title" x="0" y="-21">{title}</text>',
        '<rect class="plate" x="0" y="0" width="252" height="187"/>',
    ]
    if layer == "A":
        output.append('<circle class="opening" cx="126" cy="93.5" r="56"/>')
    else:
        output.append('<rect class="opening" x="66" y="33.5" width="120" height="120"/>')

    for row in plate_rows:
        gear_id = row["gear_id"]
        teeth = int(row["teeth"])
        cx = float(row["plate_x_mm"])
        cy = float(row["plate_y_mm"])
        is_brass = teeth in BRASS_TEETH
        radius = 4.0 if is_brass else 3.5
        cls = "bss" if is_brass else "pom"
        output.append(f'<circle class="{cls}" cx="{cx:.3f}" cy="{cy:.3f}" r="{radius:.1f}"/>')
        output.append(f'<path class="cross" d="M{cx-1.4:.3f},{cy:.3f} H{cx+1.4:.3f} M{cx:.3f},{cy-1.4:.3f} V{cy+1.4:.3f}"/>')
        output.append(f'<text class="tiny" x="{cx+4:.3f}" y="{cy-3:.3f}">{gear_id}</text>')

    output.extend(
        [
            '<circle class="bss" cx="5" cy="171" r="4"/>',
            '<text class="small" x="12" y="172">D8 nominal · 18/20T brass · OILES 80B-0608</text>',
            '<circle class="pom" cx="5" cy="178" r="3.5"/>',
            '<text class="small" x="12" y="179">D7 nominal · 24/28T POM · OILES 80B-0508</text>',
            f'<text class="tiny" x="0" y="195">{brass_count} brass seats / {pom_count} POM seats. Plate datum coordinates are case coordinates +3mm.</text>',
            '<text class="tiny" x="0" y="200">Nominal only: confirm OILES housing tolerance, press fit and clear web on a same-material test coupon.</text>',
            '<text class="tiny" x="0" y="205">Candidate plate thickness 8mm; A stays at z=0-8, B moves to z=40-48. Not CAM-ready.</text>',
            '</svg>',
        ]
    )
    return "\n".join(output) + "\n"


def main() -> None:
    rows = read_rows()
    assert len(rows) == 28
    assert sum(int(r["teeth"]) in BRASS_TEETH for r in rows) == 21
    assert sum(int(r["teeth"]) not in BRASS_TEETH for r in rows) == 7
    for layer in ("A", "B"):
        path = HERE / f"gear_support_plate_{layer}_brass_candidate.svg"
        path.write_text(render_plate(layer, rows), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
