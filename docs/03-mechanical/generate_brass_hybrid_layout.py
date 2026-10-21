#!/usr/bin/env python3
"""Derive a material/actual-hub map from the unchanged nominal XY layout."""

from __future__ import annotations

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "irregular_layered_gear_layout.svg"
OUT = HERE / "irregular_layered_gear_layout_brass_candidate.svg"
GEAR = re.compile(
    r'<g class="gear ([ab])"(?P<attrs>[^>]*)data-id="(?P<id>[^"]+)" '
    r'data-teeth="(?P<teeth>\d+)">(?P<body>.*?)</g>',
    re.DOTALL,
)


def replace_gear(match: re.Match[str]) -> str:
    layer = match.group(1)
    attrs = match.group("attrs")
    gear_id = match.group("id")
    teeth = int(match.group("teeth"))
    body = match.group("body")
    if teeth in (18, 20):
        hub_radius = 7.5 if teeth == 18 else 8.0
        body = re.sub(r'(<circle class="hub" r=")[^"]+"', rf'\g<1>{hub_radius:.1f}"', body)
        body = re.sub(r'(<circle class="bore" r=")2\.5("/>)', r'\g<1>3.0\2', body)
        css_class = "gear brass"
    else:
        css_class = f"gear {layer}"
    return f'<g class="{css_class}"{attrs}data-id="{gear_id}" data-teeth="{teeth}">{body}</g>'


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    content, gear_count = GEAR.subn(replace_gear, source)
    assert gear_count == 28, f"expected 28 gear groups; found {gear_count}"
    assert content.count('class="gear brass"') == 21

    content = content.replace(
        "Forest Guardian — 28-wheel irregular layered gear layout",
        "Forest Guardian — 21 brass / 7 POM irregular gear variant",
    )
    content = content.replace(
        "270 by 205 millimeter case, centered 3.4-inch round display, 28 KHK module-one gears in two asymmetrical depth-plane clusters. The drawing is a nominal geometry review, not a fabrication drawing.",
        "270 by 205 millimeter case, centered 3.4-inch round display, 21 KHK BSS brass gears and 7 DS POM gears in two asymmetrical depth-plane clusters. Same nominal XY centers as the all-POM baseline. Not a fabrication drawing.",
    )
    content = content.replace(
        "FOREST GUARDIAN · 3.4-IN ONE-OFF DESIGN CANDIDATE",
        "FOREST GUARDIAN · 21 BRASS / 7 POM VARIANT",
    )
    content = content.replace(
        "Offset open trains · mixed standard gears · separate depth planes · dimensions in mm",
        "Irregular XY retained · BSS hubs at catalog diameters · dimensions in mm",
    )
    content = content.replace("28 OILES bushings", "21 ID6 / 7 ID5 bushings")
    content = content.replace("18T × 11 · 20T × 10 · 24T × 3 · 28T × 4", "BSS brass: 18T × 11 · 20T × 10")
    content = content.replace("A: 14 wheels · B: 14 wheels", "POM: 24T × 3 · 28T × 4")
    content = content.replace("A00/B00: one shared shaft", "A: 11/14 brass · B: 10/14 brass")
    content = content.replace("15 projected gear overlaps &gt;1mm", "A00/B00: shared 6mm shaft")
    content = content.replace("Smallest support-hole web: 4.5", "Minimum support-hole web: 4.0")
    content = content.replace("Non-mesh clearance: ≥1.8", "Brass hub clearance: ≥3.5")
    content = content.replace("M1 mesh center error: ≤0.003", "Cross-layer shaft gap: ≥1.85")
    content = content.replace("Schematic gear cutouts", "Material / hub key")
    content = content.replace("Catalog OD is shown. Tooth outlines", "Gold: BSS1-18B / BSS1-20C")
    content = content.replace("are illustrative, not involute geometry.", "Layer tint: POM DS1-24 / DS1-28")
    content = content.replace("Board/gear 3D clearance is a Z-stack", "Tooth outlines are schematic, not involute")
    content = content.replace("assumption; actual module revision still", "and hubs use catalog diameters. 3D clearance")
    content = content.replace("needs physical inspection.", "and board fit remain to be checked.")
    content = content.replace(
        "28-wheel layout: 3.4-inch IPS, 270×205×145 case, KHK DS1 M1 gears, A Ø112 front opening and B 120-square rear opening.",
        "21 brass / 7 POM variant: 3.4-inch IPS, 270×205×145 case, KHK BSS/DS M1 gears, A Ø112 and B 120-square openings.",
    )

    style_anchor = '    .b .hub { fill:#44271c; stroke:#eab36d; stroke-width:.42; }\n'
    brass_style = (
        '    .brass path { fill:#f2c447; fill-opacity:.98; stroke:#fff0ad; }\n'
        '    .brass .hub { fill:#c48a1e; stroke:#fff0ad; stroke-width:.48; }\n'
        '    .brass .bore { fill:#111; stroke:#fff0c4; stroke-width:.4; }\n'
    )
    assert style_anchor in content
    content = content.replace(style_anchor, style_anchor + brass_style)
    OUT.write_text(content, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
