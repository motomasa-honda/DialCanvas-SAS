# Phase71 — M1 external safety interlock (REVIEW ONLY)

**Not a fabrication release.** No physical motor power, real latch, PCB/copper, ERC, DRC, flashing or manufacturing gate closure.

### Material eFuse pin correction

Original M1 selected `TPS259474LRPW` (U7), an eFuse with **pin 1 EN/UVLO (active HIGH), pin 3 PG (power-good), pin 4 PGTH (analog power-good threshold), pin 5 IN, pin 6 OUT**. It **does not provide an FLT output**. The named P4 GPIO22 FAULT feedback must therefore come from a separate *qualified PG/latch/supervisor detection circuit*, never a fictional U7.FLT net. Do not confuse with TPS259470x which has an FLT variant output.

Official TI: https://www.ti.com/product/TPS25947

### Fail-closed requirements

- Motor rail: 5V_RAW -> U7 -> 5V_MOTOR -> F_M1..F_M7 -> each isolated motor-common net. 5V_SAFE for MCP expander must not backfeed motors.
- An **independent** pulse-sensitive hardware watchdog, power supervisor, physically latched trip, stop-loop and manual rearm must gate the eFuse EN. WDI stuck HIGH/LOW, MCU stuck, brownout, overcurrent, stop open => OFF until manual rearm. GPIO22 status is observability only.
- TPS3431 is an **unselected candidate**. WDI falling-edge pulses matter, WDO output is active-low open drain, and its EN=LOW can make WDO appear HIGH via pullup; the candidate alone is not proof of edge qualification. No firmware bypass may enable power.
- **CI PASS**: [Phase71 run 38743930006](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38743930006), 512 fail-closed abstract combinations, eFuse pin mapping and seven-axis fuse identities; evidence artifact ID **11976379862**.
- Companion review ZIP has 23 more-detailed Python tests PASS, 79-net interface model and **draft KiCad `.kicad_sch`** with 72 abstract symbols/244 pins. No KiCad GUI/CLI or actual ERC/DRC run; no real footprints assumed.
- Major open item **FG-P71-001**: source GPIO22 FAULT_N from a real external circuit, dimension/pinout confirmation MTR-09-024, physical watchdog/latch construction with no-auto-restart, 7-axis independence/55mm service CAD, and full power HIL.
- **Manufacturing gates remain 0/6, software evidence 11/14**. Original Phase70 and D7 untouched; Draft PR / main unchanged.
