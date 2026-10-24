// FG-D01 v0.1: geometry study only, NOT manufacturing geometry.
// Units mm. Existing four-arm carrier remains the load-bearing mount.
// The ring does not touch the glass in this envelope study.
$fn = 180;
module half_ring(outer_d=119, inner_d=113.4, thickness=2, side=1, seam=0.8) {
  // side=1 is right half, side=-1 is left half.
  intersection() {
    difference() {
      cylinder(d=outer_d, h=thickness, center=true);
      cylinder(d=inner_d, h=thickness+0.2, center=true);
    }
    translate([side*(outer_d/2+seam/4),0,0])
      cube([outer_d,outer_d+2,thickness+1],center=true);
  }
}
// Gap between the two halves is 0.8mm total at the seam.
color("goldenrod") half_ring(side=1);
color("goldenrod") half_ring(side=-1);
// Missing by design: fasteners, support tabs, front guard interface,
// connector access, tolerance stack, and final finish.
