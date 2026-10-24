// FG-D01 v0.2 — split bezel geometry / assembly envelope
// Units: mm. Study only; NOT manufacturing or order release.
// This is an aesthetic bezel, not a load-bearing glass clamp.
$fn=240;
outer_d=119.0;
inner_d=113.4;
thickness=2.0;
split_gap=0.8;
module bezel_half(side=1) {
  assert(side==1 || side==-1);
  assert(outer_d>inner_d && split_gap>=0);
  // Clip the right half at x>=gap/2 and the left at x<=-gap/2.
  intersection() {
    difference() {
      cylinder(d=outer_d,h=thickness,center=true);
      cylinder(d=inner_d,h=thickness+0.4,center=true);
    }
    translate([side*(outer_d/2+split_gap/2),0,0])
      cube([outer_d,outer_d+2,thickness+1],center=true);
  }
}
color([0.65,0.48,0.25]) bezel_half(1);
color([0.65,0.48,0.25]) bezel_half(-1);
// Design hold: fasteners, mounting tabs, guard interface and z-offset are not yet specified.
// Do not export this study as manufacturing-ready STL/STEP.
