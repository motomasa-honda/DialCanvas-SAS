// Forest Guardian G1 positive bayonet: native 3D reference only.
// Unit coupon MUST NOT be printed for product use. No anti-backslide keeper.
$fn=36; lock_state="locked"; SHIFT_Y=2.5;
module guide(){difference(){union(){
 translate([60.8,26,123])cube([1.2,28,13.5]);
 translate([60.25,32,134.3])cube([1.75,5,2.35]);}
 translate([61.28,32.2,134.85])cube([.87,4.6,.85]);
 translate([61.28,32.3,135.70])cube([.87,1.4,1.05]);
}}
module key(){translate([0,lock_state=="locked"?SHIFT_Y:0,0])union(){
 translate([62.05,32.5,138.05])cube([.4,5.5,1.3]);
 translate([62.05,32.5,135])cube([.4,1,4.35]);
 translate([61.4,32.5,135])cube([1.05,1,.5]);}}
color([.10,.50,.60])guide();
color([.82,.30,.70])key();
