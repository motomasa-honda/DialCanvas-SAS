// Original D7 SHA256 20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f
// Review only; source D7 solids not embedded; physical assembly unqualified.
color([0.05,0.28,0.44]) translate([18,12,127])cube([235,6,9]); // FRONT_CROSSBAR
color([0.05,0.28,0.44]) translate([18,18,130])cube([3,168,3]); // SIDE_FRAME_LEFT
color([0.05,0.28,0.44]) translate([251,18,130])cube([3,168,3]); // SIDE_FRAME_RIGHT
color([0.05,0.28,0.44]) translate([18,16,130])cube([3,6,3]); // FRONT_LEFT_FRAME_COUPLER
color([0.05,0.28,0.44]) translate([250,16,130])cube([3,6,3]); // FRONT_RIGHT_FRAME_COUPLER
color([0.03,0.57,0.55]) translate([111,17,130])cube([3,46,6]); // LEFT_FRONT_WEB
color([0.03,0.57,0.55]) translate([111,61.5,130])cube([6,6.5,6]); // LEFT_JOG
color([0.03,0.57,0.55]) translate([114,66,130])cube([3,19,6]); // LEFT_TO_G5_GUIDE
color([0.71,0.33,0.44]) translate([166,12,116])cube([3,6,20]); // RIGHT_ROOT_Z_RISER
color([0.71,0.33,0.44]) translate([166,17,116])cube([3,73,7]); // RIGHT_LOWER_WEB
color([0.71,0.33,0.44]) translate([166,89,116])cube([3,6,7]); // RIGHT_LOWER_TO_TIP
color([0.71,0.33,0.44]) translate([163,93,116])cube([6,6,20]); // RIGHT_REAR_Z_RISER
color([0.71,0.33,0.44]) translate([163,95,130])cube([3,5,6]); // RIGHT_TO_G5_GUIDE
