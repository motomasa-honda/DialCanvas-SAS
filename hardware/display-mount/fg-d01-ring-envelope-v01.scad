// FG-D01 v0.2 - two-piece front trim study, NOT a structural display mount.
// Millimeters; Z is front-to-back. This CAD is a concept, not a cut file.
// The original four-arm carrier supports the display. No glass compression.
// Ring is considered OUTSIDE the continuous transparent guard, subject to review.
$fn=240;
outer_d=119;
inner_d=113.4;
thickness=2.0;
seam=0.8;
guard_thickness=3.0;
display_d=115;
glass_d_max=112.6;
lens_d_max=88.4;
show_envelope=true;
module half(side=1) {
  intersection() {
    difference() {
      cylinder(d=outer_d,h=thickness,center=true);
      cylinder(d=inner_d,h=thickness+0.2,center=true);
    }
    // At x=0 each half ends seam/2 from center; half-space with margin.
    translate([side*(outer_d/2+seam/2),0,0])
      cube([outer_d,outer_d+1,thickness+1],center=true);
  }
}
// z=0 is guard rear face, guard occupies -3..0.
// Display glass front is nominally z=+1.5.
// Ring envelope is outside guard at z=-5..-3, with no display contact.
// Attachment to guard NOT yet designed; no adhesive/fastener authorization.
translate([0,0,-4]) {
  color([0.72,0.49,0.18]) half(1);
  color([0.72,0.49,0.18]) half(-1);
}
if(show_envelope) {
  %translate([0,0,-guard_thickness/2]) cylinder(d=160,h=guard_thickness,center=true);
  %translate([0,0,1.5]) cylinder(d=glass_d_max,h=0.05,center=true);
  %translate([0,0,1.55]) cylinder(d=lens_d_max,h=0.05,center=true);
  %translate([0,0,1.65]) cylinder(d=display_d,h=0.05,center=true);
}
