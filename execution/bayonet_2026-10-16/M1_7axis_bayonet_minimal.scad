// D7 seven-axis nominal matched guide/rigid-bayonet proof of concept.
// DESIGN REVIEW, NOT APPROVED HARDWARE. 14 guide lips, 14 keys.
// Does NOT include independently load-certified bracket anchors, other D7 solids, real motor PCBs or 14 webs.
// Source 1774 solid SHA256 20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f.
// Lock state: "entry" for insertion, "locked" after +Y2.5mm. REVERSE UNINTENDED SLIDE STILL UNBLOCKED.
$fn=24;lock_state="locked";show_sleds=true;
function lock_y()=lock_state=="locked"?2.5:0;
module fixed_ring(){color([.10,.22,.45,.8]){
  translate([18,18,130])cube([3,168,3]);
  translate([250,18,130])cube([3,168,3]);
  translate([18,18,130])cube([235,3,3]);
  translate([18,183,130])cube([235,3,3]);}}
module all_notched_guides(){difference(){
  union(){
    // Axis G1, left and right guide plus thickening boss
    translate([60.8,26,123])cube([1.2,28,13.5]);
    translate([60.25,32,134.3])cube([1.75,4.85,2.35]);
    translate([108,26,123])cube([1.2,28,13.5]);
    translate([108,46,134.3])cube([1.75,4.85,2.35]);
    // Axis G2, left and right guide plus thickening boss
    translate([30.8,126,123])cube([1.2,28,13.5]);
    translate([30.25,132,134.3])cube([1.75,4.85,2.35]);
    translate([78,126,123])cube([1.2,28,13.5]);
    translate([78,146,134.3])cube([1.75,4.85,2.35]);
    // Axis G3, left and right guide plus thickening boss
    translate([110.8,126,123])cube([1.2,28,13.5]);
    translate([110.25,132,134.3])cube([1.75,4.85,2.35]);
    translate([158,126,123])cube([1.2,28,13.5]);
    translate([158,146,134.3])cube([1.75,4.85,2.35]);
    // Axis G4, left and right guide plus thickening boss
    translate([200.8,116,123])cube([1.2,28,13.5]);
    translate([200.25,122,134.3])cube([1.75,4.85,2.35]);
    translate([248,116,123])cube([1.2,28,13.5]);
    translate([248,136,134.3])cube([1.75,4.85,2.35]);
    // Axis G5, left and right guide plus thickening boss
    translate([115.8,71,123])cube([1.2,28,13.5]);
    translate([115.25,77,134.3])cube([1.75,4.85,2.35]);
    translate([163,71,123])cube([1.2,28,13.5]);
    translate([163,91,134.3])cube([1.75,4.85,2.35]);
    // Axis G6, left and right guide plus thickening boss
    translate([25.8,71,123])cube([1.2,28,13.5]);
    translate([25.25,77,134.3])cube([1.75,4.85,2.35]);
    translate([73,71,123])cube([1.2,28,13.5]);
    translate([73,91,134.3])cube([1.75,4.85,2.35]);
    // Axis G7, left and right guide plus thickening boss
    translate([115.8,26,123])cube([1.2,28,13.5]);
    translate([115.25,32,134.3])cube([1.75,4.85,2.35]);
    translate([163,26,123])cube([1.2,28,13.5]);
    translate([163,46,134.3])cube([1.75,4.85,2.35]);
  }
  translate([61.28,32.20,134.85])cube([.87,4.6,.85]); // lower G1L keyway
  translate([61.28,32.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([107.85,46.20,134.85])cube([.87,4.6,.85]); // lower G1R keyway
  translate([107.85,46.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([31.28,132.20,134.85])cube([.87,4.6,.85]); // lower G2L keyway
  translate([31.28,132.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([77.85,146.20,134.85])cube([.87,4.6,.85]); // lower G2R keyway
  translate([77.85,146.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([111.28,132.20,134.85])cube([.87,4.6,.85]); // lower G3L keyway
  translate([111.28,132.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([157.85,146.20,134.85])cube([.87,4.6,.85]); // lower G3R keyway
  translate([157.85,146.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([201.28,122.20,134.85])cube([.87,4.6,.85]); // lower G4L keyway
  translate([201.28,122.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([247.85,136.20,134.85])cube([.87,4.6,.85]); // lower G4R keyway
  translate([247.85,136.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([116.28,77.20,134.85])cube([.87,4.6,.85]); // lower G5L keyway
  translate([116.28,77.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([162.85,91.20,134.85])cube([.87,4.6,.85]); // lower G5R keyway
  translate([162.85,91.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([26.28,77.20,134.85])cube([.87,4.6,.85]); // lower G6L keyway
  translate([26.28,77.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([72.85,91.20,134.85])cube([.87,4.6,.85]); // lower G6R keyway
  translate([72.85,91.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([116.28,32.20,134.85])cube([.87,4.6,.85]); // lower G7L keyway
  translate([116.28,32.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
  translate([162.85,46.20,134.85])cube([.87,4.6,.85]); // lower G7R keyway
  translate([162.85,46.30,135.7])cube([.87,1.4,1.05]); // top ENTRY aperture
}}
module sled(x,y){color([.45,.73,.2,.8])translate([x-22,y-17.5,123])difference(){
  cube([44,35,15]);translate([1.6,1.6,-.3])cube([40.8,31.8,15.6]);}}
module bar(axis,x,y){ color([.7,.25,.7,.8])translate([0,lock_y(),0])union(){
  translate([x-24,y-2,138.05])cube([48,4,1.3]);
  if(axis==1){
    translate([62.05,32.5,138.05])cube([.4,5.500,1.3]);
    translate([62.05,32.5,135])cube([.4,1,4.35]);
    translate([61.4,32.5,135])cube([1.05,1,.5]);
    translate([107.55,42,138.05])cube([.4,5.500,1.3]);
    translate([107.55,46.5,135])cube([.4,1,4.35]);
    translate([107.55,46.5,135])cube([1.05,1,.5]);
  }
  if(axis==2){
    translate([32.05,132.5,138.05])cube([.4,5.500,1.3]);
    translate([32.05,132.5,135])cube([.4,1,4.35]);
    translate([31.4,132.5,135])cube([1.05,1,.5]);
    translate([77.55,142,138.05])cube([.4,5.500,1.3]);
    translate([77.55,146.5,135])cube([.4,1,4.35]);
    translate([77.55,146.5,135])cube([1.05,1,.5]);
  }
  if(axis==3){
    translate([112.05,132.5,138.05])cube([.4,5.500,1.3]);
    translate([112.05,132.5,135])cube([.4,1,4.35]);
    translate([111.4,132.5,135])cube([1.05,1,.5]);
    translate([157.55,142,138.05])cube([.4,5.500,1.3]);
    translate([157.55,146.5,135])cube([.4,1,4.35]);
    translate([157.55,146.5,135])cube([1.05,1,.5]);
  }
  if(axis==4){
    translate([202.05,122.5,138.05])cube([.4,5.500,1.3]);
    translate([202.05,122.5,135])cube([.4,1,4.35]);
    translate([201.4,122.5,135])cube([1.05,1,.5]);
    translate([247.55,132,138.05])cube([.4,5.500,1.3]);
    translate([247.55,136.5,135])cube([.4,1,4.35]);
    translate([247.55,136.5,135])cube([1.05,1,.5]);
  }
  if(axis==5){
    translate([117.05,77.5,138.05])cube([.4,5.500,1.3]);
    translate([117.05,77.5,135])cube([.4,1,4.35]);
    translate([116.4,77.5,135])cube([1.05,1,.5]);
    translate([162.55,87,138.05])cube([.4,5.500,1.3]);
    translate([162.55,91.5,135])cube([.4,1,4.35]);
    translate([162.55,91.5,135])cube([1.05,1,.5]);
  }
  if(axis==6){
    translate([27.05,77.5,138.05])cube([.4,5.500,1.3]);
    translate([27.05,77.5,135])cube([.4,1,4.35]);
    translate([26.4,77.5,135])cube([1.05,1,.5]);
    translate([72.55,87,138.05])cube([.4,5.500,1.3]);
    translate([72.55,91.5,135])cube([.4,1,4.35]);
    translate([72.55,91.5,135])cube([1.05,1,.5]);
  }
  if(axis==7){
    translate([117.05,32.5,138.05])cube([.4,5.500,1.3]);
    translate([117.05,32.5,135])cube([.4,1,4.35]);
    translate([116.4,32.5,135])cube([1.05,1,.5]);
    translate([162.55,42,138.05])cube([.4,5.500,1.3]);
    translate([162.55,46.5,135])cube([.4,1,4.35]);
    translate([162.55,46.5,135])cube([1.05,1,.5]);
  }
}}
fixed_ring();
color([.06,.50,.55])all_notched_guides();
if(show_sleds)sled(85,40);
bar(1,85,40);
if(show_sleds)sled(55,140);
bar(2,55,140);
if(show_sleds)sled(135,140);
bar(3,135,140);
if(show_sleds)sled(225,130);
bar(4,225,130);
if(show_sleds)sled(140,85);
bar(5,140,85);
if(show_sleds)sled(50,85);
bar(6,50,85);
if(show_sleds)sled(140,40);
bar(7,140,40);
// Nominal reverse unlock: lock_state="entry". No secondary keeper designed.
