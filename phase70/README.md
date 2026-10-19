# Phase70 — XC Rev1.1 GPIO reconciliation and independent M1 logical net audit

**REVIEW ONLY. Do not flash, energize motors, fabricate PCB, or merge into main.**

Source for board wiring: [manufacturer XC Rev1.1 two-page schematic](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf), page 1; [manufacturer XC hardware audit](https://github.com/waveshareteam/ESP32-P4-WIFI6-Touch-LCD-XC/blob/main/docs/HARDWARE.md).

- XC ESP32-P4 to ESP32-C6: GPIO6, 14, 15, 16, 17, 18, 19, 54. Unlike a **different 4B board**, this Rev1.1 **XC** schematic does **not** show GPIO20/21/22 connected to C6; they appear on the J8 expansion interface.
- Preserved Phase67 candidate pin plan: ARM=32, HEARTBEAT=28, FAULT=22, SW1=29, SW2=30, MCP SDA=20, SCL=21. These do not statically collide with the reviewed XC C6 wiring; they still require actual PCB revision and 3.3V logic, 5V I2C level-shift, startup, wireless coexistence, watchdog and motor-safety measurements.
- `.github/workflows/phase70-xc-m1-static.yml` extracts SHA-pinned Phase67 firmware source, verifies the header SHA256, audits all seven GPIOs against reviewed C6/peripheral assignments, performs four rejection mutations, generates a **logical** seven-axis control/output/fused-supply netlist, and uploads an evidence artifact. It does NOT perform electrical ERC/DRC or manufacture an M1 PCB.
- M1 baseline: 2 MCP23017 breakouts (0x20, 0x21); 7 independently serviceable ULN2003 module candidates, 28 phases/pulldowns, 7 individual motor commons/fuses. Final driver-module physical pins, pad spacing, motor polarity, 55mm movement envelope, real 178-branch harness mapping, and independent watchdog are not validated.
- Previous Phase69 RAW/NVS safety improvement and candidate build remain independently verified, not in scope of this static GPIO/M1 check.

**State**: manufacturing 0/6 CLOSED; software evidence 11/14. Static XC net conflict sub-question resolved, but FG-P68-002 remains OPEN pending physical proof. M1 Gate1–3 remain OPEN.

The full Phase70 host netlist model, per-pin connector CSV, 11 negative/positive tests and reproducibility audit are preserved in the companion Phase70 handoff archive; CI has its own simpler, independent check.
