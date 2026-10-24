// FG-D01 front stack reference, mm. Conceptual envelope; not a fabrication drawing.
// z=0: rear surface of continuous front protective guard.
// Negative z: toward viewer. Positive z: into enclosure.
$fn=180;
show_guard=true;
show_ring=true;
show_display=true;
show_support=true;
module annulus(od,id,z0,h) {
  translate([0,0,z0]) difference(){
    cylinder(d=od,h=h);
    translate([0,0,-0.05]) cylinder(d=id,h=h+0.1);
  }
}
if(show_guard) color([0.65,0.85,0.9,0.35])
  translate([0,0,-3]) cylinder(d=180,h=3);
if(show_ring) color([0.67,0.41,0.15])
  annulus(119,113.4,-5,2);
if(show_display) {
  color([0.12,0.15,0.18,0.8])
    translate([0,0,1.5]) cylinder(d=115,h=15.5);
  color([0.25,0.4,0.5,0.7])
    translate([0,0,1.49]) cylinder(d=112.6,h=0.01);
}
if(show_support) color([0.5,0.6,0.65,0.4])
  annulus(175,119,29,8);
// Deliberately omitted: actual guard boundary, ring fasteners, carrier arms,
// cover retaining lip, physical tolerance and strain analysis.
