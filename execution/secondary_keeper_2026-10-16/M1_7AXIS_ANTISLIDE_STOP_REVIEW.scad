// Forest Guardian M1 seven-axis secondary anti-slide M2x5 headless-stud design review.
// 2026-10-19 candidate: outboard boss and X-screened cassette notch.
// NOT for fabrication. Full 1,774 D7 source solids are not embedded in this lightweight SCAD.
// Required independent sequence: remove cover, grille and access Gx stud, reverse Y 2.5mm, remove bar, +Z55mm sled.
// Rear wood cutters are integrated as a separate review overlay only; this model has no wood solid.
$fn=28;
BOSS_X_MIN=21.3; BOSS_X_MAX=24.6; BOSS_Y_MIN=-3.75; BOSS_Y_MAX=0.2;
SCREW_X=22.95; SCREW_Y=-1.1; BOSS_Z=134; BOSS_HEIGHT=4;
SEAT_X=4.1; SEAT_Y=4.75; SEAT_CX=22.95; SEAT_CY=-1.775; SEAT_Z=137; SEAT_DEPTH=1.6;
WOOD_BORE_D=3.2; WOOD_Z=137; WOOD_THICKNESS=8; SHOW_WOOD_CUTTER_OVERLAY=false;
AXES=[[1,85,40],[2,55,140],[3,135,140],[4,225,130],[5,140,85],[6,50,85],[7,140,40]];
locked=true;stud_removed=false;
function sy()=locked?2.5:0;
module guide(x,y,side){
  by=y+side*7;rx=side<0?x-24.2:x+23;wx=side<0?x-23.72:x+22.85;
  color([.1,.53,.64]) difference(){
    translate([rx,y-14,123])cube([1.2,28,13.5]);
    translate([wx,by-.8,134.85])cube([.87,4.6,.85]);
    translate([wx,by-.7,135.70])cube([.87,1.4,1.05]);
    if(side>0)translate([x+SCREW_X,y+SCREW_Y,133.9])cylinder(r=1.025,h=4.1);
  }
  color([.1,.53,.64]) difference(){
    translate([side<0?x-24.75:x+23,by-1,134.3])cube([1.75,4.85,2.35]);
    translate([wx,by-.8,134.85])cube([.87,4.6,.85]);
    translate([wx,by-.7,135.70])cube([.87,1.4,1.05]);
  }
}
module sled(x,y){color([.48,.76,.22,.85])difference(){
  translate([x-22,y-17.5,123])difference(){
    cube([44,35,15]);translate([1.6,1.6,-.1])cube([40.8,31.8,15.2]);
  }
  // The entire side-wall HEIGHT has to be relieved or the fixed boss blocks +Z removal.
  // Integrated 0.2mm inward-shifted boss x=21.3..24.6; notch clears the conservative
  // 40mm board envelope in X and the boss footprint in Y (assumed tolerance only).
  translate([x+20.6,y-4.2,122.9])cube([1.9,4.85,15.2]);
}}
module screw_boss(x,y){
 color([.05,.50,.64])difference(){
   translate([x+BOSS_X_MIN,y+BOSS_Y_MIN,BOSS_Z])cube([BOSS_X_MAX-BOSS_X_MIN,BOSS_Y_MAX-BOSS_Y_MIN,BOSS_HEIGHT]);
   translate([x+SCREW_X,y+SCREW_Y,133.9])cylinder(r=1.025,h=5);
 }
 if(!stud_removed)color([.94,.61,.08])translate([x+SCREW_X,y+SCREW_Y,134.35])cylinder(r=1,h=5);
}
// Candidate wood machining volumes, positioned from the actual integrated keeper dimensions.
// These are orange review cutters, NOT boolean cuts from the D7 or a machining release.
module wood_relief_cutters(x,y){
 color([1,.35,.05,.45])translate([x+SEAT_CX-SEAT_X/2,y+SEAT_CY-SEAT_Y/2,SEAT_Z])cube([SEAT_X,SEAT_Y,SEAT_DEPTH]);
 color([1,.1,.1,.45])translate([x+SCREW_X,y+SCREW_Y,WOOD_Z])cylinder(d=WOOD_BORE_D,h=WOOD_THICKNESS);
}
// Lifted 0.55mm to screen 0.1mm worst-case Z clearance above the cassette wall.
module bar(x,y){color([.67,.21,.67])translate([x-24,y-2+sy(),138.6])cube([48,4,1.3]);}
module keyed_parts(x,y){
 for(side=[-1,1]){
   by=y+side*7;px=side<0?x-22.95:x+22.55;kx=side<0?x-23.6:x+22.55;
   bottom=min(by-.5,y-2);top=max(by+.5,y+2);
   color([.67,.21,.67])translate([0,sy(),0])union(){
     translate([px,bottom,138.6])cube([.4,top-bottom,1.3]);
     translate([px,by-.5,135])cube([.4,1,4.35]);
     translate([kx,by-.5,135])cube([1.05,1,.5]);
   }
 }
}
color([.1,.2,.4,.75]){
 translate([18,18,130])cube([3,168,3]);translate([250,18,130])cube([3,168,3]);
 translate([18,18,130])cube([235,3,3]);translate([18,183,130])cube([235,3,3]);
}
for(a=AXES){x=a[1];y=a[2];
 guide(x,y,-1);guide(x,y,1);sled(x,y);screw_boss(x,y);bar(x,y);keyed_parts(x,y);
 if(SHOW_WOOD_CUTTER_OVERLAY)wood_relief_cutters(x,y);
}
