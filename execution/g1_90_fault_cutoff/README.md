# G1-90 — Fault latch physically connected to eFuse cutoff and 28-phase OE disable (UNPOWERED REVIEW)

## Actual connectivity added

**G1-90 hardening:** Added U35 (SN74LVC1G32DBVR, pins A1/B2/GND3/Y4/VCC5) and C34 (100nF decoupler). U35 inputs receive original `B86__FAULT_Q` and pre-latch `B88__TRIP_COMBINED`. U35 output `B90__CUT_REQUEST_OR` feeds both R59→Q1 power sink and U34→eight `/OE` disable pins. This closes the latch-propagation blind spot in the original version: **a directly asserted TRIP can demand motor cutoff even while FAULT_Q is still LOW**. It is NOT an independent safety channel (same AON rail and related gates), nor an analog timing/HIL proof. TI DBV pinout: https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf .

**Q1** is now **Diodes Incorporated DMN2056U** N-channel FET, physical SOT23 pins 1 GATE, 2 SOURCE, 3 DRAIN (https://www.diodes.com/datasheet/download/DMN2056U.pdf). Original Infineon 2N7002 has no sufficiently specified RDS(on) for the intended 3.3V-supply logic. DMN2056U DS38480 specifies 45mΩ MAX at VGS=2.5V/ID=3.1A and 85mΩ MAX at VGS=1.5V/ID=2A, both at TA=25°C. This is an improvement in candidate evidence, NOT a board-level safe-off qualification. Q1 drain connects to **actual U14/U7 EN/UVLO** and source to GND. `CUT_REQUEST_OR` from U35.4 drives Q1 gate via R59=330Ω, with R60=100kΩ gate pull-down. FAULT_Q asserted HIGH makes Q1 pull eFuse EN LOW. EN's original independent R4 10kΩ **pull-down remains installed**, so this board is still NEVER approved to power a motor.

**U34** is TI SN74LVC1G32DBVR OR (A1, B2, GND3, Y4, VCC5; https://www.ti.com/product/SN74LVC1G32/part-details/SN74LVC1G32DBVR). Input A connects to the U35 combined request (FAULT_Q OR direct TRIP). Input B has R61 10kΩ pull-up to 3V3_AON, permanently requiring phase disable. Output Y connects to `B78__PHASE_OE_N_FIXED_HIGH`, shared by ALL 8 native /OE pins (U15-U18 pin1/pin19), with their original FOUR 3V3 pull-ups retained. Every phase therefore stays tri-stated. U34 bypass C33=100nF.

## Why this is progress and not manufacture approval

The fault latch is no longer just an isolated status indicator. In the real KiCad native netlist it is now connected to both power disable and 28-phase output disable hardware, but both output paths remain deliberately disabled for review. The design is a candidate and NOT a release circuit: Q1 on-resistance at only 3.3V Vgs, eFuse EN analog thresholds and transient leakage, logic-power loss, 3V3 cold POR state, gate output propagation and source protection all require worst-case design proof. The original fault latch's cold startup state is not yet unconditionally settled.

Future independent REARM permission and motor-enable request would need a guaranteed fail-closed path, cannot simply pull R4 out, and must account for eFuse EN undervoltage comparator thresholds and Q1 fault handling. `R61` must NOT be changed into a software-controlled line without verified power sequencing, STOP, watchdog, fault latch and independent hardware interlocks.

## CI and scope

Generator consumes original G1-89 native KiCad (which reproducibly generates G1-88) and adds 16 physical pads / 6 parts, without mutating 499 pre-existing endpoints. Actual KiCad9 XML/SVG/ERC compare every physical pad of 522 total, 149 parts and all eight 28-phase buffer OEs. No ERC warnings suppressed.

Scope G1-05/G1-06 stays WORKING, 20/48 formally done, 0/6 manufacturing gate. NO purchases, fabrication, power-on, flashing, or main merge. Always apply safety hold.

**Remaining power-sequencing safety gate:** TPS3808 RESET_N is undefined below its power-on-reset supply threshold; this logic OR does NOT make 3V3_AON missing safe by itself. U7 EN's unconditional R4 pull-down is the currently enforced no-power guarantee. Independent AON brownout-to-power shutdown, `FAULT_Q` latch settling, logic output contention, worst-case sink/driver thresholds, and hardware HIL remain blockers.

## G1-89電圧閾値是正の継承（2026-10-18）
本回路の親G1-89はMR=実eFuse EN直結の不整合を改修済み。U33.3 MRは3V3_AON、SENSEは実U14.1 ENの12k/10k分圧で、EN起動前に監視の開始条件を検出する。G1-90のeFuse ENシンクQ1も同一の実ENへ接続されており、故障時は監視SENSEも落ちる。逆にこれらは実運転許可、AON低下時の安全性、故障の全条件成立を証明しない。

## 起動監視タイマーの上限規格
親G1-89は68nFの公称389ms CT容量方式から、CTをR62=100kΩ経由でVDDへ接続するTIメーカー固定300ms方式に変更済み。TPS3808 Rev.N規定（指定電気試験条件）でRESET解除まで180～420ms。RESET_NプルアップR56も100kΩへ変更。ただし、この規格は実機全体の500ms立上り期限や3V3_AON喪失時の保証を意味しない。eFuse ENは依然R4プルダウンで強制禁止。

## Gate-drive sink element review update

Physical SOT23 G1/S2/D3 nets unchanged. DMN2056U's manufacturer-specified sub-3.3V gate RDS(on) replaces the 2N7002 guess. Thermal max, EN source max, 3V3 VOH min, AON loss, timing, hardware STOP and PCB all remain OPEN. R4 always holds eFuse EN LOW; all eight OEs are disabled. Never fabricate or energize.
