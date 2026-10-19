// Forest Guardian / Seeed 105990072
// Parametric datum plate candidate only; not released for manufacture.
// Units: mm. Orient the 35 mm motor fixing span along the 50 mm reservation.
plate_xy = [48, 39];                 // leaves 1 mm nominal per-side within 50 x 41 reserve
plate_thickness = 2;                 // screening value; material/process not selected
motor_hole_spacing_nominal = 35;
motor_hole_spacing_allowance = 0.4; // slot half-travel; covers drawing +/-0.2 mm
slot_width = 4.8;                    // candidate clearance, not selected fastener fit
boss_clearance_diameter = 10.0;      // motor boss max 9.2 mm; no shaft coupling represented
$fn = 96;

module fixing_slot(xc) {
    hull() {
        translate([xc - motor_hole_spacing_allowance, 0, 0])
            cylinder(d=slot_width, h=plate_thickness + 2, center=true);
        translate([xc + motor_hole_spacing_allowance, 0, 0])
            cylinder(d=slot_width, h=plate_thickness + 2, center=true);
    }
}

module plate() {
    difference() {
        cube([plate_xy[0], plate_xy[1], plate_thickness], center=true);
        cylinder(d=boss_clearance_diameter, h=plate_thickness + 2, center=true);
        for (x = [-motor_hole_spacing_nominal/2, motor_hole_spacing_nominal/2])
            fixing_slot(x);
    }
}

// Dashed bounding envelopes are separate datum solids, not a motor/PCB stack model.
module motor_plan_envelope() {
    color([0.72, 0.55, 0.24, 0.35])
        translate([0, 0, plate_thickness/2 + 0.1])
            cylinder(d=28.1, h=19.3, center=false);
}

plate();
// Set true only when visually inspecting the conservative motor body envelope.
show_motor_envelope = false;
if (show_motor_envelope) motor_plan_envelope();
