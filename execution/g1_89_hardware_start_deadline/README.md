# G1-89 — Hardware startup deadline wired to PG/rail safety monitor (review only)

## Removed an unsafe bypass and filled the physical timer gap
G1-88 exposed MONITOR_ACTIVE on J19 and pulled it down permanently. This revision eliminates J19 entirely and rewires R56 as a TI-required 10k pull-up. The real open-drain reset output of U33 now drives MONITOR_ACTIVE. With U7 EN LOW, MONITOR_ACTIVE remains inactive, so no motor power is released.

U33 TI TPS3808G01DBVR physical pins: 1 RESET_N, 2 GND, 3 MR_N, 4 CT, 5 SENSE, 6 VDD. MR_N is connected to the ACTUAL eFuse U7 EN net, not software and not PG. The 68nF CT capacitor C30 gives nominal 68/175 + 0.0005 = ~0.389 seconds; the 64.9k/10k divider on 3V3_AON gives nominal detection threshold ~3.033V. C31 local 100nF decoupling, C32 1nF SENSE filter.

The timer does not wait for PG before starting: failure to establish PG can trip the already-connected G1-88 NOR fault latch at the deadline. PG loss after the deadline also trips. This is a conditional design: actual motor enable is still hard disabled. The real worst-case timer, capacitor tolerance, AON brownout and startup races are NOT proven.

Manufacturer basis: https://www.ti.com/lit/ds/symlink/tps3808.pdf and https://www.ti.com/product/TPS3808 . TPS3808 open-drain RESET_N requires 10k–1M pull-up; 68nF gives only a TYPICAL delay, not guaranteed <=500ms. Manufacturer DBV pinout verified, DRV pinout NOT substituted.

Reproducible: python3 execution/g1_89_hardware_start_deadline/build_review.py regenerates G1-88 as the exact base then actual native KiCad G1-89 and all 499 physical pads/141 symbols. CI exports genuine KiCad9 SVG/netlist/ERC and compares all pins. No native ERC warnings suppressed.

**Not done:** physical U7 EN cutoff and phase OE gates, independent real power sourcing, cold power-up fault latch POR, STOP-short monitor, PCB footprints/DRC, thermal load/HIL. Keep G1-05/06 WORKING, 20/48 DONE_SCOPE, manufacturing 0/6. Do not buy, power, fabricate, flash or merge main.
