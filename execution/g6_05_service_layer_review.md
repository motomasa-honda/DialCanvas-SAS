# G6-05 7-axis wiring and service overlay (review only)

D7 coordinates in mm; +Z is rearward. Source: execution/cassettes/seven_axis_conditional_layout.json.

axis,x_mm,y_mm,connector,logical_pins,service_retract_plus_z_mm
G1,85,40,J_M1_G1,1-6,55
G2,55,140,J_M1_G2,1-6,55
G3,135,140,J_M1_G3,1-6,55
G4,225,130,J_M1_G4,1-6,55
G5,140,85,J_M1_G5,1-6,55
G6,50,85,J_M1_G6,1-6,55
G7,140,40,J_M1_G7,1-6,55

Layer AXIS_CENTER: seven source centers above.
Layer SERVICE_SWEEP_CANDIDATE: +Z 55mm each axis, unverified tool/cable clearance.
Layer LOGICAL_BRANCH: pins 1-4 PH0-PH3, pin 5 axis fused 5V, pin 6 GND. Exact 42-branch source: execution/g6_06_build_service_sequence/branch_register_42.json.
Layer HOLD: physical module pins, connector dimensions/orientation, actual route, bend radius, wire length, crimps, strain relief all unresolved.

Keep other six axes, gears and P3 installed. Common rear cover and grille access only. Original fan relocation prerequisite is not thermally approved. NO G5 BACK_WOOD cutting.

G6-05 remains OPEN: this is a review overlay, not a printable fabrication routing layer. eFuse EN LOW, no power, cutting, procurement or main merge.
