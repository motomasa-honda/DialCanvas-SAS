# G1-90 — Fault latch physically connected to eFuse cutoff and 28-phase OE disable (UNPOWERED REVIEW)

## Actual connectivity added

**G1-90 hardening:** Added U35 (SN74LVC1G32DBVR, pins A1/B2/GND3/Y4/VCC5) and C34 (100nF decoupler). U35 inputs receive original `B86__FAULT_Q` and pre-latch `B88__TRIP_COMBINED`. U35 output `B90__CUT_REQUEST_OR` feeds both R59→Q1 power sink and U34→eight `/OE` disable pins. This closes the latch-propagation blind spot in the original version: **a directly asserted TRIP can demand motor cutoff even while FAULT_Q is still LOW**. It is NOT an independent safety channel (same AON rail and related gates), nor an analog timing/HIL proof. TI DBV pinout: https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf .

**Q1** is Infineon 2N7002 N-channel FET, physical PG-SOT23 pins 1 GATE, 2 SOURCE, 3 DRAIN (https://www.infineon.com/assets/row/public/documents/24/49/infineon-2n7002-ds-en.pdf). Q1 drain connects to **actual U14/U7 EN/UVLO** and source to GND. `CUT_REQUEST_OR` from U35.4 drives Q1 gate via R59=330Ω, with R60=100kΩ gate pull-down. FAULT_Q asserted HIGH makes Q1 pull eFuse EN LOW. EN's original independent R4 10kΩ **pull-down remains installed**, so this board is still NEVER approved to power a motor.

**U34** is TI SN74LVC1G32DBVR OR (A1, B2, GND3, Y4, VCC5; https://www.ti.com/product/SN74LVC1G32/part-details/SN74LVC1G32DBVR). Input A connects to the U35 combined request (FAULT_Q OR direct TRIP). Input B has R61 10kΩ pull-up to 3V3_AON, permanently requiring phase disable. Output Y connects to `B78__PHASE_OE_N_FIXED_HIGH`, shared by ALL 8 native /OE pins (U15-U18 pin1/pin19), with their original FOUR 3V3 pull-ups retained. Every phase therefore stays tri-stated. U34 bypass C33=100nF.

## Why this is progress and not manufacture approval

The fault latch is no longer just an isolated status indicator. In the real KiCad native netlist it is now connected to both power disable and 28-phase output disable hardware, but both output paths remain deliberately disabled for review. The design is a candidate and NOT a release circuit: Q1 on-resistance at only 3.3V Vgs, eFuse EN analog thresholds and transient leakage, logic-power loss, 3V3 cold POR state, gate output propagation and source protection all require worst-case design proof. The original fault latch's cold startup state is not yet unconditionally settled.

Future independent REARM permission and motor-enable request would need a guaranteed fail-closed path, cannot simply pull R4 out, and must account for eFuse EN undervoltage comparator thresholds and Q1 fault handling. `R61` must NOT be changed into a software-controlled line without verified power sequencing, STOP, watchdog, fault latch and independent hardware interlocks.

## CI and scope

Generator consumes original G1-89 native KiCad (which reproducibly generates G1-88) and adds 16 physical pads / 6 parts, without mutating 499 pre-existing endpoints. Actual KiCad9 XML/SVG/ERC compare every physical pad of 522 total, 149 parts and all eight 28-phase buffer OEs. No ERC warnings suppressed.

Scope G1-05/G1-06 stays WORKING, 20/48 formally done, 0/6 manufacturing gate. NO purchases, fabrication, power-on, flashing, or main merge. Always apply safety hold.

**Remaining power-sequencing safety gate:** TPS3808 RESET_N is undefined below its power-on-reset supply threshold; this logic OR does NOT make 3V3_AON missing safe by itself. U7 EN's unconditional R4 pull-down is the currently enforced no-power guarantee. Independent AON brownout-to-power shutdown, `FAULT_Q` latch settling, logic output contention, worst-case sink/driver thresholds, and hardware HIL remain blockers.
