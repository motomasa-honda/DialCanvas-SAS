# G1-88: Real PG and independent rail fault gate, review only

**Native circuit extension:** G1-87 446 physical pads to 485, 124 symbols to 136; four existing pad connections changed and all others preserved. The generator writes a genuine editable KiCad9 schematic and strict native pin correspondence. Does not alter G1-87.

**Why:** PG and rail RESET_N are LOW when the eFuse is intentionally disabled. Wiring these directly as a fault would prevent startup. The post-start fault must be qualified by an independent HARDWARE startup timer. That timer is NOT built.

U28 AND: PG and rail supervisor RESET_N. U29 INV: inverted joint health. U30 AND: MONITOR_ACTIVE and bad rail. U31 OR: original TRIP_ASSERT and post-start fault. U32 INV: combined qualification for clear. Rewire U20.5/U23.1 to combined trip and U22.2/U26.1 to combined qualification, to prevent fault clearance while the monitored rail is bad.

J19 is a review-only proposed input and R56 10k pulls MONITOR_ACTIVE LOW. It is NOT an approved timer interface; no software may drive it. New TI OR component SN74LVC1G32DBVR matches manufacturer DBV physical pins 1=A, 2=B, 3=GND, 4=Y, 5=VCC (https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf).

Run: python3 execution/g1_88_pg_rail_fault/build_review.py. CI exports physical KiCad9 XML/SVG/ERC and checks all pads, without hiding ERC warnings. Evidence only after CI success.

**HOLD:** physical startup deadline, cold POR, power-source validation, unambiguous asynchronous reset, logic propagation/ESD, actual U7 output interlock, actual phase OE gates, component footprints, complete ERC/DRC and HIL. G1-05/06 WORKING; 20/48 DONE_SCOPE; manufacturing 0/6; eFuse EN grounded; no purchasing, cutting, device power, flashing or main merge.
