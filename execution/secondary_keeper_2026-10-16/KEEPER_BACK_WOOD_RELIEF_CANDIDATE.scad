// Seven-axis rear-wood machining overlay for source-D7 review only.
// It contains cutter volumes, not a replacement enclosure or manufacturing file.
// Required order: cut shallow seats from BACK_WOOD front face, then clearance
// bores through the remaining panel. Remove the common rear grille for access.
// Axis 5 still depends on relocation of the original FAN_MAX_BODY/FAN_GASKET.
$fn = 48;
AXES = [[1,85,40],[2,55,140],[3,135,140],[4,225,130],
        [5,140,85],[6,50,85],[7,140,40]];
SEAT_SIZE = [4.1, 4.75];
SEAT_CENTER_OFFSET = [22.95, -1.775];
SEAT_Z = [137.0, 138.6];
STUD_CENTER_OFFSET = [22.95, -1.1];
WOOD_BACK_Z = 145.0;
BORE_DIAMETER = 3.2;

module back_wood_keeper_cutters() {
  for (a = AXES) {
    x = a[1];
    y = a[2];
    seat_x = x + SEAT_CENTER_OFFSET[0];
    seat_y = y + SEAT_CENTER_OFFSET[1];
    stud_x = x + STUD_CENTER_OFFSET[0];
    stud_y = y + STUD_CENTER_OFFSET[1];
    color([0.95,0.25,0.05,0.55])
      translate([seat_x-SEAT_SIZE[0]/2, seat_y-SEAT_SIZE[1]/2, SEAT_Z[0]])
        cube([SEAT_SIZE[0], SEAT_SIZE[1], SEAT_Z[1]-SEAT_Z[0]]);
    color([0.05,0.35,0.95,0.65])
      translate([stud_x, stud_y, 136.9])
        cylinder(d=BORE_DIAMETER, h=WOOD_BACK_Z-136.9+0.1);
  }
}

back_wood_keeper_cutters();
