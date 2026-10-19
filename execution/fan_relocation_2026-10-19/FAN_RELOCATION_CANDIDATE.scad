// External rear exhaust concept. Source D7 and wood are not embedded: geometry review only.
// Not a fabrication drawing. Fasteners, plate material, seal, intake and guard remain TBD.
$fn=64;
CX=220; CY=40;
FAN_W=30; FAN_T=10; FAN_Z=146.5;
WOOD_PORT_D=29.7;
PLATE_W=45; PLATE_T=1.5; PLATE_Z=145;
SUPPORT_OFFSET=19;
SHOW_PORT_AXIS=true;
SHOW_SUPPORT_MARKERS=true;

// Symbolic fan envelope: SUNON MF30100V3-1000U-A99 size class; actual CAD not supplied.
color([0.12,0.32,0.58,0.85])
 translate([CX-FAN_W/2,CY-FAN_W/2,FAN_Z]) cube([FAN_W,FAN_W,FAN_T]);

// Positional adapter plate envelope. The modeled center port is open; anchor centers are markers,
// not specified drill diameters. No wood solid is included, so no boolean wood cut is implied.
color([0.66,0.43,0.19,0.8]) difference(){
 translate([CX-PLATE_W/2,CY-PLATE_W/2,PLATE_Z]) cube([PLATE_W,PLATE_W,PLATE_T]);
 translate([CX,CY,PLATE_Z-0.1]) cylinder(d=WOOD_PORT_D,h=PLATE_T+0.2);
}
if(SHOW_SUPPORT_MARKERS)
 for(dx=[-SUPPORT_OFFSET,SUPPORT_OFFSET],dy=[-SUPPORT_OFFSET,SUPPORT_OFFSET])
  color([0.95,0.7,0.05]) translate([CX+dx,CY+dy,PLATE_Z+PLATE_T]) cylinder(d=2,h=0.4);
if(SHOW_PORT_AXIS)
 color([1,0.1,0.1,0.3]) translate([CX,CY,137]) cylinder(d=WOOD_PORT_D,h=8);
