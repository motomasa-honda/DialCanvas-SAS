// Forest Guardian G5 real-source eight-datum external assembly fixture. NOT product/NOT CAM.
// Dimensions in mm; base relative Z=0 is original D7 source Z116.
$fn=24;
show_original_source_member_boxes=true;
module board(){color([.72,.58,.4,.5])cube([270,190,8]);}
module spacers(){
  color([.1,.45,.62]){
    translate([40,15,8])cylinder(r=4,h=11);
    translate([130,15,8])cylinder(r=4,h=11);
    translate([230,15,8])cylinder(r=4,h=11);
    translate([19.5,120,8])cylinder(r=4,h=14);
    translate([252,120,8])cylinder(r=4,h=14);
    translate([112.5,44,8])cylinder(r=4,h=14);
  }
}
// Two right underpass supports seat on the base directly at original D7 Z116.
// Product components are separate from jig and must NOT be fastened to it in service.
board();spacers();
if(show_original_source_member_boxes) {
  // Schematic only: selected five part bounding routes, source solids not fully rendered.
  color([.2,.27,.4,.65])translate([18,12,19])cube([235,6,9]);
  color([.2,.56,.44,.65])translate([111,17,22])cube([3,46,6]);
  color([.68,.32,.34,.65])translate([166,17,8])cube([3,73,7]);
}
