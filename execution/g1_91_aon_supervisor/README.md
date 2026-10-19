# G1-91 AON voltage monitor and startup forced-fault (unpowered KiCad review)

U36 is an independent TI TPS3808G01DBVR supervisor for the always-on 3.3V rail. DBV pins RESET_N1/GND2/MR_N3/CT4/SENSE5/VDD6. MR_N and VDD go to 3V3_AON. R63 60.4k 1% and R64 10k 1% divide 3V3_AON into SENSE for an approximately 2.851V threshold; using +/-2% comparator and 1% resistor bounding gives about 2.75 to 2.96V. The regulator's actual tolerance and ramp remain NOT verified. CT is a genuine native KiCad no-connect to select the TI ~20ms fixed release delay. RESET_N has R65 100k pull-up; C35 100nF bypass; C36 1nF sense filter.

U37 TI SN74LVC1G04DBVR inverter turns active-low supervisor RESET_N into active-high AON_BAD. U38 TI SN74LVC1G32DBVR ORs the existing B88__TRIP_COMBINED with AON_BAD to make B91__TRIP_ALL. U20.5 (fault latch SET), U23.1 (rearm history TRIP), U32.2 (clear inhibit), and U35.2 (direct power and 8 /OE cut) are exactly the four existing pins rewired. Independent local 100nF C37/C38 are present for U37/U38. All other 518 original pads unchanged; +30 pads and +10 components gives 552 pins/159 real symbols.

When operating supply is present and AON has not met the sense threshold for ~20ms, AON_BAD demands fault state and inhibits release. A subsequent AON recovery does not automatically clear fault; a fresh switch-release then press remains required. This is a nominal functionality candidate, not validated hardware safety.

IMPORTANT: TPS3808 RESET output is undefined when its VDD is below POR, and LVC inverter/OR require powered supply. This design does not prove true AON power-loss shutdown. R4 permanently shorts the real U7 EN to GND via 10k and phase buffer enables remain pulled inactive. No motor supply enabling or fabrication is allowed.

CI regenerates full real KiCad9 source from G1-90, exports XML netlist/SVG/ERC and validates all 552 pads and exact only-four rewires with NO ERC suppression. G1-05 and G1-06 WORKING, 20/48 done_scope and 0/6 manufacturer gates. Open: independent motor enabling supply, AON source/load sequence, STOP/watchdog qualification, PCB, zero ERC, FET worst-case, physical motor HIL.

Manufacturer: https://www.ti.com/lit/ds/symlink/tps3808.pdf ; https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf ; https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf
