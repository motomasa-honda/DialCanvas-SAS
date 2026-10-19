// EAGLE-source placement overlay. Review regions only; no retaining mechanism is released.
// Units: mm. Board XY follows source EAGLE datum (0,0) .. (35,19.3).
board_xy=[35,19.3];
board_visual_thickness=0.2; // visualization only; actual PCB thickness not sourced
lip_depth=0.6;
$fn=32;

color([0.35,0.38,0.42,0.45]) cube([board_xy[0],board_xy[1],board_visual_thickness]);
// Source-clear top edge segment: x=3..17, y=18.7..19.3.
color([0.15,0.72,0.25,0.8]) translate([3,18.7,board_visual_thickness]) cube([14,lip_depth,0.6]);
// Source-clear short bottom edge segment: x=24..28, y=0..0.6.
color([0.15,0.72,0.25,0.8]) translate([24,0,board_visual_thickness]) cube([4,lip_depth,0.6]);
// tPlace proxy silhouettes for the two nearest components are visual orientation aids only.
color([0.9,0.2,0.12,0.6]) translate([17.462,16.256,board_visual_thickness]) cube([5.703,1.27,0.6]); // D4/R4 region
color([0.9,0.2,0.12,0.6]) translate([16.21,0.762,board_visual_thickness]) cube([7.2,7.62,0.6]); // SW2 region
