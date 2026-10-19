// G5 actual five discrete members, EDITABLE reviewer solid model; original D7 SHA 20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f
// The external six interfaces (2 G5 guides, 4 sidewood anchors) NOT QUALIFIED.
$fn=32;part_name="ASSEMBLY";
module CROSSBAR(){translate([18,12,127])cube([235,6,9]);}
module SIDE_LEFT(){difference(){union(){translate([18,18,130])cube([3,168,3]);translate([18,16,130])cube([3,6,3]);}CROSSBAR();}}
module SIDE_RIGHT(){difference(){union(){translate([251,18,130])cube([3,168,3]);translate([250,16,130])cube([3,6,3]);}CROSSBAR();}}
module G5_LEFT(){difference(){union(){translate([111,17,130])cube([3,46,6]);translate([111,61.5,130])cube([6,6.5,6]);translate([114,66,130])cube([3,19,6]);}CROSSBAR();}}
module G5_RIGHT(){difference(){union(){translate([166,12,116])cube([3,6,20]);translate([166,17,116])cube([3,73,7]);translate([166,89,116])cube([3,6,7]);translate([163,93,116])cube([6,6,20]);translate([163,95,130])cube([3,5,6]);}CROSSBAR();}}
module ASSEMBLY(){color([.02,.29,.45])CROSSBAR();color([.35,.52,.68])SIDE_LEFT();color([.35,.52,.68])SIDE_RIGHT();color([.08,.63,.45])G5_LEFT();color([.84,.37,.28])G5_RIGHT();}
if(part_name=="ASSEMBLY") ASSEMBLY(); else { if(part_name=="CROSSBAR")CROSSBAR();if(part_name=="SIDE_LEFT")SIDE_LEFT();if(part_name=="SIDE_RIGHT")SIDE_RIGHT();if(part_name=="G5_LEFT")G5_LEFT();if(part_name=="G5_RIGHT")G5_RIGHT(); }
