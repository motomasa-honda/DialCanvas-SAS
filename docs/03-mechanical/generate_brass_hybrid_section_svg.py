#!/usr/bin/env python3
"""Create a nominal axial section for the optional 21-gear brass hybrid."""

from pathlib import Path


OUT = Path(__file__).with_name("layered_gear_axial_section_brass_candidate.svg")
SCALE = 8.0  # px/mm
X0 = 110.0   # z=0 datum


def x(z_mm: float) -> float:
    return X0 + z_mm * SCALE


def rect(z0: float, z1: float, y: float, h: float, cls: str, label: str) -> str:
    text = "" if not label else (
        f'<text class="part" x="{(x(z0)+x(z1))/2:.1f}" y="{y+h/2+5:.1f}" '
        f'text-anchor="middle">{label}</text>'
    )
    return (
        f'<rect class="{cls}" x="{x(z0):.1f}" y="{y:.1f}" '
        f'width="{(z1-z0)*SCALE:.1f}" height="{h:.1f}" rx="5"/>'
        f'{text}'
    )


parts = "\n".join(
    [
        # Support boards and bearing sleeves
        rect(0, 8, 212, 110, "plate", "Front"),
        rect(0, 8, 260, 14, "bearing", ""),
        # Shared 6mm compound shaft: trim 1mm from 6x60 stock; z=0..59 gives 10mm insertion.
        rect(0, 59, 261, 12, "shaft", ""),
        # Hub and tooth faces are shown separately to make the 8mm hub visible.
        rect(9, 17, 248, 38, "brass", "Hub A"),
        rect(17, 23, 231, 72, "brass-face", "A face"),
        rect(25, 31, 231, 72, "brass-face", "B face"),
        rect(31, 39, 248, 38, "brass", "Hub B"),
        rect(40, 48, 212, 110, "plate", "Rear"),
        rect(40, 48, 260, 14, "bearing", ""),
        rect(49, 79, 228, 78, "coupler", "4 to 6mm"),
        rect(79, 112, 200, 134, "motor", "NEMA-8"),
    ]
)

ticks = []
for z in range(0, 122, 10):
    xx = x(z)
    ticks.append(
        f'<line class="tick" x1="{xx:.1f}" y1="477" x2="{xx:.1f}" y2="490"/>'
        f'<text class="small" x="{xx:.1f}" y="511" text-anchor="middle">{z}</text>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="780" viewBox="0 0 1800 780" role="img" aria-labelledby="title desc">
  <title id="title">21 brass gear candidate axial section</title>
  <desc id="desc">Nominal axial arrangement for an optional mixed KHK BSS brass and DS POM gear set. Not a fabrication drawing. Display board depth is not to scale.</desc>
  <style>
    text {{ font-family: "DejaVu Sans", sans-serif; fill:#29241e; }}
    .title {{ font-size:29px; font-weight:700; }} .subtitle {{ font-size:16px; fill:#61594e; }}
    .part {{ font-size:14px; font-weight:600; }} .small {{ font-size:13px; fill:#61594e; }}
    .tiny {{ font-size:12px; fill:#61594e; }} .head {{ font-size:18px; font-weight:700; }}
    .plate {{ fill:#c9e5e5; stroke:#39787c; stroke-width:2; }}
    .bearing {{ fill:#e9d19d; stroke:#76552d; stroke-width:1.5; }}
    .shaft {{ fill:#818f98; stroke:#38464d; stroke-width:1.5; }}
    .brass {{ fill:#d9a445; stroke:#80531d; stroke-width:2; }}
    .brass-face {{ fill:#be8430; stroke:#80531d; stroke-width:2; }}
    .coupler {{ fill:#c5c8bd; stroke:#53574e; stroke-width:2; }}
    .motor {{ fill:#647887; stroke:#293943; stroke-width:2; }}
    .datum {{ stroke:#b14c35; stroke-width:2; stroke-dasharray:7 5; }}
    .wall {{ stroke:#33271d; stroke-width:8; }} .axis {{ stroke:#92928c; stroke-width:1.5; stroke-dasharray:7 5; }}
    .tick {{ stroke:#514b43; stroke-width:1.4; }}
    .panel {{ fill:#f4eee3; stroke:#b8a88e; stroke-width:1.5; }}
    .dim {{ stroke:#514b43; stroke-width:1.5; marker-start:url(#arrow); marker-end:url(#arrow); }}
  </style>
  <defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto-start-reverse"><path d="M9,0 L0,4.5 L9,9" fill="none" stroke="#514b43" stroke-width="1.2"/></marker></defs>
  <rect width="1800" height="780" fill="#fbfaf6"/>
  <text class="title" x="42" y="48">BRASS HYBRID · NOMINAL AXIAL STACK</text>
  <text class="subtitle" x="42" y="78">21 brass gears / 7 POM gears · z=0 is the inside face of the front frame · dimensions in mm · not a fabrication drawing</text>
  <text class="small" x="42" y="130">FRONT</text>
  <text class="small" x="1018" y="130">REAR INNER WALL</text>
  <line class="axis" x1="65" y1="267" x2="1100" y2="267"/>
  {parts}
  <line class="datum" x1="{x(40):.1f}" y1="165" x2="{x(40):.1f}" y2="435"/>
  <text class="tiny" x="{x(40)+5:.1f}" y="156">LCD glass datum z=40</text>
  <line class="wall" x1="{x(121):.1f}" y1="178" x2="{x(121):.1f}" y2="354"/>
  <line class="dim" x1="{x(112):.1f}" y1="383" x2="{x(121):.1f}" y2="383"/>
  <text class="small" x="{(x(112)+x(121))/2:.1f}" y="408" text-anchor="middle">9mm rear gap</text>
  <line class="dim" x1="{x(23):.1f}" y1="453" x2="{x(25):.1f}" y2="453"/>
  <text class="tiny" x="{(x(23)+x(25))/2:.1f}" y="446" text-anchor="middle">2mm gap</text>
  <line class="axis" x1="{x(0):.1f}" y1="490" x2="{x(121):.1f}" y2="490"/>
  {''.join(ticks)}
  <text class="small" x="{x(60.5):.1f}" y="539" text-anchor="middle">z (mm)</text>
  <rect class="panel" x="1180" y="116" width="570" height="574" rx="8"/>
  <text class="head" x="1210" y="157">Z CHANGES</text>
  <text class="small" x="1210" y="198">A face: z=17–23 (+2mm)</text>
  <text class="small" x="1210" y="226">B face: z=25–31 (+2mm)</text>
  <text class="small" x="1210" y="254">Rear plate: z=40–48 (+4mm)</text>
  <text class="small" x="1210" y="282">Coupler: 49–79 / motor: 79–112</text>
  <text class="small" x="1210" y="310">Rear gap: 9mm in a 145mm-deep case</text>
  <text class="head" x="1210" y="364">OPEN FIT CHECKS</text>
  <text class="small" x="1210" y="402">- 3.4C carrier and rear ports in 120mm opening</text>
  <text class="small" x="1210" y="432">- 6mm shaft retention and 10mm coupler insertion</text>
  <text class="small" x="1210" y="462">- NEMA-8 rear wire bend clearance</text>
  <text class="small" x="1210" y="492">- Mixed 7/8mm bearing holes in the support plates</text>
  <text class="head" x="1210" y="552">DISPLAY DATUM</text>
  <text class="small" x="1210" y="585">LCD glass stays at z=40. Board thickness and</text>
  <text class="small" x="1210" y="613">connectors are not to scale; verify with carrier.</text>
  <text class="tiny" x="42" y="733">Brass hub length 8mm. Nominal 1mm clearance to each support plate. Gear teeth, tolerances, plate flex and wire routing are not validated; this is not a fabrication drawing.</text>
</svg>'''

OUT.write_text(svg, encoding="utf-8")
print(OUT)
