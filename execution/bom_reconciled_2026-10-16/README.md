# G4-02 DONE_SCOPE — source-complete D7/M1 BOM reconciliation (2026-10-16)

**This is the first true increment of the frozen 48-item outcome ledger since G2-06.** G4-02 moved `WORKING→DONE_SCOPE`; the other 47 tasks kept their status. The broader *manufacturing BOM* `G4-08` remains **OPEN**.

## Critical provenance breakthrough

The primary D7 BOM was not missing. It is nested **three levels deep** inside the immutable previous Phase67 handoff:

`Forest_Guardian_Handoff_Phase67_2026-10-15.zip → BASELINE/Forest_Guardian_Handoff_2026-10-14.zip → BASELINE/forest-guardian-chatgpt-handoff.zip → d7/`.

Original material was **actually extracted, hashed, compared and regenerated locally** (separate full-source user ZIP, not available in this GitHub tree):
- `d7/bom/unified-bom.csv`: **429 rows**, SHA256 `b40a43a41eca06d83ffcf8b21378dbba6b64bdbb7a1244ed935baab4cf913879`.
- `d7/bom/m1-module-bom-addendum.csv`: **18 rows**, SHA256 `2aceeee4bbdf4b71263544423cca0a6037a791c476b2fff94ad0320265701c87`.
- `d7/bom/pcb-assembly-bom.csv`: **210 PCB assembly rows**, including **59 old DRIVER physical components**, SHA256 `0d5ca67721cd200cbb101e4b71566057cead4a104567650a7317db69fe3c42fd`.
- `d7/cad/wood-receiver-design.json`: **68 true existing woodworking operations** and **24 receiver instances**, SHA256 `3789fce2ab940a14d86987ecdac8365b57c9ae9816ea918ce8b41dcb77831da5`.
- Nested original **65,483,374-byte** `d7/cad/assembly.json` independently re-hashed to canonical D7 SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`.

## Actual reconciliation outcome

- **Full auditable merged review BOM: 448 rows = original 429 + source M1 addendum 18 + ONE recovered RTC source row**. Original fields for all 429 and 18 preserved losslessly, not merely guessed or rewritten.
- **IMPORTANT original BOM defect:** old master 429 has NO `E_RTC` row, although PCB assembly list contains DRIVER `U609: RX8900SA UA X1B000292000100` 1 unit. Exactly one `D7_PCB_ASSEMBLY_RECOVERY_1` row with explicit source recovers this and prevents silent omission. **No duplicate product purchase.**
- All **59** old DRIVER component refs are classified individually (GitHub [per-part list](driver_59_policy.csv)): 4 prior MCP+caps replaced by two new Adafruit MCP23017 breakouts; **4** old TBD driver ICs retired; **28** old pull-downs superseded by **28** M1 carrier pull-downs, not 56; **5** reset parts require actual new safety schematic; **7** I²C/level-shifter references transfer; **3** RTC and caps transfer; **8** LED drivers transfer.
- Preserve exactly **7 existing distinct fuse feeds** F_M1...F_M7; 7-module × 6 carrier contacts = **42**, plus 7-way feeder pair and their **14** contacts; logical wire and contact counts are different purchase units and are never blindly added.
- Original M1 addendum has a **driver-board SKU/link mismatch**: M1-02 names `MTR-09-024` while linking to the distinct `MTR-09-004` listing. ElectroPeak currently lists these as different ULN2003 driver boards (35×31mm vs 40×20mm nominal), not as motors. Keep the original source unchanged. Actual motor model/order code, motor electrical rating, board dimensions, connector placement, conservative board-clearance and secondary M2 keeper remain unresolved.

## What is complete, what is not

**G4-02 limited engineering integration is DONE_SCOPE**, proven by independent generator `build_reconciliation.py` and `verify_reconciliation.py` included in the downloadable full-source user ZIP. All 59 source refs and 68 woodworking processes are traceable, source and 448 merged row counts checked.

G4-08 manufacturing-grade BOM **remains OPEN** because M1 native PCB, safety latch, full SKU/orderability, all harness physical lengths, sample driver dimension, rear wood/fan geometry, prices and hardware qualifications are not resolved. The recovered **68 wood ops** belong to the historical D7, not the *additional* M1 4-cleat/7-pocket machining, so G3-05 and G6-02 remain WORKING. This is **not** authorization to cut or energize.

**Frozen ledger now 17/48 DONE_SCOPE, 7 WORKING, 20 OPEN, 4 HARDWARE_WAIT; manufacturing 0/6, software review 11/14.** No purchase, no fabrication, motor rail eFuse EN LOW, no hardware flash, and no merge to main. PR #2 stays Draft.

### Evidence location and CI limitations

- GitHub [59 source driver mapping](driver_59_policy.csv), [fixed source SHA and acceptance scope](source_contract.json), [static CI contract](check_contract.py). GitHub CI validates exact mapping counts and 17/48, **but it does not validate the original full 429 rows**, which are in the distributable source ZIP.
- Companion user artifact contains original extracted CSV+JSON source files, true `448-row` merged review CSV, 59 source-to-policy table, 68 woodworking-op register, new 48-task tracker, `verify_reconciliation.py`, a formula-backed **5-sheet** XLSX and file SHA manifest. This allows independent full-source local re-verification.

Next work should continue the **M1 PCB BOM manufacturer part numbers** and *real* 40mm clearance redesign concurrently with electrical safety; do not replace further design work with another phase summary.
