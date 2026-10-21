#!/usr/bin/env python3
"""Generate a non-manufacturing OpenSCAD envelope model from the gear-axis CSV."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEDULE = ROOT / "gear_axis_schedule.csv"
OUTPUT = ROOT / "cots_clock_envelope_review.scad"
CASE_W = 270.0
CASE_H = 205.0


def read_gears() -> dict[str, list[tuple[int, float, float]]]:
    result: dict[str, list[tuple[int, float, float]]] = {"A": [], "B": []}
    with SCHEDULE.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            layer = row["layer"]
            if layer not in result:
                raise ValueError(f"unknown gear layer: {layer}")
            teeth = int(row["teeth"])
            # Convert from case top-left to a centered OpenSCAD XY plane.
            x = float(row["case_x_mm"]) - CASE_W / 2
            y = CASE_H / 2 - float(row["case_y_mm"])
            result[layer].append((teeth, x, y))

    if len(result["A"]) != 14 or len(result["B"]) != 14:
        raise ValueError(f"expected 14 gears per layer, got A={len(result['A'])}, B={len(result['B'])}")
    if result["A"][0][1:] != result["B"][0][1:]:
        raise ValueError("A00 and B00 must share their compound shaft center")
    return result


def scad_array(gears: list[tuple[int, float, float]]) -> str:
    rows = [f"  [{teeth}, {x:.3f}, {y:.3f}]" for teeth, x, y in gears]
    return "[\n" + ",\n".join(rows) + "\n]"


def main() -> None:
    gears = read_gears()
    template = r'''// Generated from gear_axis_schedule.csv by generate_clock_envelope_review.py.
// Nominal visualization only. Do not use as a manufacturing file.
$fn = 48;

A_GEARS = __A_GEARS__;
B_GEARS = __B_GEARS__;

CASE_W = 270;
CASE_H = 205;
CASE_D = 145;
WALL = 12;
INNER_D = 121;
PLATE_W = 252;
PLATE_H = 187;
PLATE_T = 8;
BORE_D = 5;
BUSHING_D = 7;
BOARD_XY = 115;
BOARD_VIS_DEPTH = 15; // placeholder; actual board/cable envelope is unmeasured
ACTIVE_D = 87.6;
GEAR_FACE_T = 6;
GEAR_HUB_D_VIS = 10; // schematic placeholder; DS1 boss diameter is not modeled

show_shell = true;
show_guard = true;
show_supports = true;
show_gears = true;
show_board = true;
show_motor = true;

function gear_points(teeth, root_r, tip_r, phase=0) = [
  for (i = [0:teeth-1]) each [
    [root_r*cos(i*360/teeth - 0.50*360/teeth + phase), root_r*sin(i*360/teeth - 0.50*360/teeth + phase)],
    [root_r*cos(i*360/teeth - 0.28*360/teeth + phase), root_r*sin(i*360/teeth - 0.28*360/teeth + phase)],
    [tip_r*cos(i*360/teeth - 0.18*360/teeth + phase), tip_r*sin(i*360/teeth - 0.18*360/teeth + phase)],
    [tip_r*cos(i*360/teeth + 0.18*360/teeth + phase), tip_r*sin(i*360/teeth + 0.18*360/teeth + phase)],
    [root_r*cos(i*360/teeth + 0.28*360/teeth + phase), root_r*sin(i*360/teeth + 0.28*360/teeth + phase)],
    [root_r*cos(i*360/teeth + 0.50*360/teeth + phase), root_r*sin(i*360/teeth + 0.50*360/teeth + phase)]
  ]
];

module gear_disc(teeth, x, y, z, face_color, phase=0) {
  tip_r = (teeth + 2) / 2;
  root_r = (teeth - 2.5) / 2;
  translate([x, y, z])
    color(face_color)
      linear_extrude(height=GEAR_FACE_T, convexity=10)
        difference() {
          polygon(points=gear_points(teeth, root_r, tip_r, phase));
          circle(d=BORE_D, $fn=24);
        }
}

module gear_hub(x, y, z, face_color) {
  color(face_color)
    translate([x, y, z])
      difference() {
        cylinder(d=GEAR_HUB_D_VIS, h=6);
        translate([0,0,-0.1]) cylinder(d=BORE_D, h=6.2, $fn=24);
      }
}

module support_a() {
  color([0.66, 0.83, 0.80, 0.46])
    difference() {
      translate([-PLATE_W/2, -PLATE_H/2, 0]) cube([PLATE_W, PLATE_H, PLATE_T]);
      translate([0,0,-0.1]) cylinder(d=112, h=PLATE_T+0.2);
      for (g=A_GEARS) translate([g[1],g[2],-0.1]) cylinder(d=BUSHING_D, h=PLATE_T+0.2);
    }
}

module support_b() {
  color([0.66, 0.83, 0.80, 0.46])
    difference() {
      translate([-PLATE_W/2, -PLATE_H/2, 36]) cube([PLATE_W, PLATE_H, PLATE_T]);
      translate([-60,-60,35.9]) cube([120,120,PLATE_T+0.2]);
      for (g=B_GEARS) translate([g[1],g[2],35.9]) cylinder(d=BUSHING_D, h=PLATE_T+0.2);
    }
}

module bushings_and_shafts() {
  for (g=A_GEARS) {
    color([0.78,0.78,0.74])
      translate([g[1],g[2],0])
        difference() {
          cylinder(d=BUSHING_D, h=PLATE_T);
          translate([0,0,-0.1]) cylinder(d=BORE_D, h=PLATE_T+0.2, $fn=24);
        }
  }
  for (g=B_GEARS) {
    color([0.78,0.78,0.74])
      translate([g[1],g[2],36])
        difference() {
          cylinder(d=BUSHING_D, h=PLATE_T);
          translate([0,0,-0.1]) cylinder(d=BORE_D, h=PLATE_T+0.2, $fn=24);
        }
  }
  // Twenty-six individual axes bridge the two support planes. The shared A00/B00 axis is shown separately.
  for (i=[1:13])
    color([0.60,0.63,0.65]) translate([A_GEARS[i][1],A_GEARS[i][2],8]) cylinder(d=BORE_D,h=28,$fn=24);
  for (i=[1:13])
    color([0.60,0.63,0.65]) translate([B_GEARS[i][1],B_GEARS[i][2],8]) cylinder(d=BORE_D,h=28,$fn=24);
  color([0.60,0.63,0.65]) translate([A_GEARS[0][1],A_GEARS[0][2],-3.5]) cylinder(d=BORE_D,h=58.5,$fn=24);
}

module gear_layers() {
  if (show_gears) {
    for (g=A_GEARS) {
      gear_hub(g[1],g[2],9,[0.78,0.50,0.19]);
      gear_disc(g[0],g[1],g[2],15,[0.83,0.61,0.31],0);
    }
    for (g=B_GEARS) {
      gear_disc(g[0],g[1],g[2],23,[0.58,0.34,0.18],180/g[0]);
      gear_hub(g[1],g[2],29,[0.47,0.26,0.14]);
    }
  }
}

module dial_face() {
  color([0.018,0.025,0.032])
    translate([0,0,39.4]) cylinder(d=ACTIVE_D,h=0.6);
  // Generic test face, not the user's final artwork.
  color([0.89,0.65,0.34]) {
    for (i=[0:11])
      rotate([0,0,i*30]) translate([0,34.5,40.05]) cube([1.3,7,0.25],center=true);
    rotate([0,0,90]) translate([0,8,40.10]) cube([1.6,22,0.4],center=true);
    rotate([0,0,42]) translate([0,12,40.15]) cube([1.1,30,0.35],center=true);
    translate([0,0,40.30]) cylinder(d=4,h=0.5,$fn=24);
  }
}

module display_board() {
  if (show_board) {
    color([0.10,0.27,0.25,0.86])
      translate([-BOARD_XY/2,-BOARD_XY/2,40]) cube([BOARD_XY,BOARD_XY,BOARD_VIS_DEPTH]);
    dial_face();
  }
}

module motor_and_coupler() {
  if (show_motor) {
    // Motor/coupler bodies are simplified vendor-envelope representations.
    color([0.69,0.71,0.67])
      translate([A_GEARS[0][1],A_GEARS[0][2],48]) cylinder(d=14,h=22);
    color([0.28,0.34,0.38])
      translate([A_GEARS[0][1]-10,A_GEARS[0][2]-10,72]) cube([20,20,33]);
    color([0.74,0.74,0.70])
      translate([A_GEARS[0][1],A_GEARS[0][2],63]) cylinder(d=4,h=9,$fn=24);
  }
}

module case_shell() {
  color([0.25,0.12,0.055]) {
    // Open-back/open-front shell, with only the outer walls and front perimeter rails shown.
    translate([-CASE_W/2,-CASE_H/2,-12]) cube([WALL,CASE_H,CASE_D]);
    translate([CASE_W/2-WALL,-CASE_H/2,-12]) cube([WALL,CASE_H,CASE_D]);
    translate([-CASE_W/2,-CASE_H/2,-12]) cube([CASE_W,WALL,CASE_D]);
    translate([-CASE_W/2,CASE_H/2-WALL,-12]) cube([CASE_W,WALL,CASE_D]);
    translate([-CASE_W/2,-CASE_H/2,-12]) cube([CASE_W,WALL,9]);
    translate([-CASE_W/2,CASE_H/2-WALL,-12]) cube([CASE_W,WALL,9]);
    translate([-CASE_W/2,-CASE_H/2,-12]) cube([WALL,CASE_H,9]);
    translate([CASE_W/2-WALL,-CASE_H/2,-12]) cube([WALL,CASE_H,9]);
  }
}

module front_guard() {
  if (show_guard)
    color([0.76,0.89,0.91,0.20])
      translate([-CASE_W/2,-CASE_H/2,-3]) cube([CASE_W,CASE_H,3]);
}

if (show_shell) case_shell();
if (show_supports) {
  support_a();
  support_b();
}
bushings_and_shafts();
gear_layers();
display_board();
motor_and_coupler();
front_guard();
'''
    template = template.replace("__A_GEARS__", scad_array(gears["A"]))
    template = template.replace("__B_GEARS__", scad_array(gears["B"]))
    OUTPUT.write_text(template, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT.parent.parent)} (14 gears per layer, 28 total)")


if __name__ == "__main__":
    main()
