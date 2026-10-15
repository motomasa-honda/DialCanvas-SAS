# Forest Guardian — Parallel Execution Board / v1.0 (2026-10-16)

**From now on measure completed artifacts, not Phase counts.** The approved 7-axis individual-replacement A plan, D7 CAD reference and conservative physical safety gate remain unchanged.

## Frozen task inventory
Exactly **48 independently scoped deliverables**: eight in each of the six D7 manufacturing gate disciplines. Details in [tasks.csv](./tasks.csv). Current counts:

| Scope | DONE_SCOPE | WORKING | OPEN | HARDWARE_WAIT | Gate |
|---|---:|---:|---:|---:|---|
| G1 Real electrical / PCB | 4 | 2 | 2 | 0 | OPEN |
| G2 Complete physical harness | 3 | 0 | 4 | 1 | OPEN |
| G3 Mechanical/wood/thermal | 3 | 2 | 2 | 1 | OPEN |
| G4 BOM, specs, fabrication drawings | 1 | 2 | 5 | 0 | OPEN |
| G5 Product SW integration | 4 | 1 | 2 | 1 | OPEN |
| G6 All A3 patterns and assembly sequence | 1 | 1 | 5 | 1 | OPEN |
| **TOTAL** | **16/48** | **8** | **20** | **4** | **0/6 closed** |

These **16 scoped passes** include **15 prior source-evidenced partial deliverables plus one NEW document this turn (G2-06)**. DO NOT report them as 16 finished manufacturing assemblies, a 33% product completion metric, or a cleared hardware safety review. Software evidence **11/14**, remaining SW09, SW12, SW14.

## The change to execution
- **Build lane (primary):** progress actual engineering artifacts in G2/G3/G4/G5/G6 even if G1's physical latch is unfinished; next G4-02 M1 BOM, G3-05 wood machining/tool access, G6-02 interior templates.
- **Safety lane (concurrent):** finish G1-05/06 independent trip latch, NC-STOP failure/short policy, 3.3V/5V supervision, PG post-start fault and native KiCad ERC; preserve motor power OFF. Only gate dangerous actions, not design work.
- **Evidence lane:** whenever updating a row, provide the produced artifact + pass/fail scope + unresolved limits; run [guard.py](./guard.py). Do not split the frozen 48 tasks just to inflate progress. IDs are stable and revisions must disclose ID remapping.
- Scope values: `DONE_SCOPE` proves ONLY its named close condition within documented limits; `WORKING`, `OPEN`, and `HARDWARE_WAIT` do not count. Manufacturing gate OPEN until its entire original D7 completion contract passes.
- **NO PCB fabrication, purchase, flash, power enable or `main` merge** is authorized. Physical samples/timing/motor failures must be measured, not simulated away.

**New scoped deliverable:** G2-06, printable 7-module×6-pin preassembly continuity checklist. Original Phase67 D7 source branch CSV has 42 rows = 28 control + 7 fused motor commons + 7 GND. Carrier connector pins are traceable, but module physical pins, length, polarity/continuity test results are explicitly UNVERIFIED/TBD/NOT_TESTED.

Underlying source: `Forest_Guardian_Handoff_Phase67_2026-10-15.zip/CANONICAL_D7/completion-contract.md`; `remaining-work.csv`, `harness/m1-module-branches.csv`; and Phase74 manufacturing 6 gates + SW14 evidence tables. Full editable dashboard/7 sheets are in the companion user artifact.

**Release states:** manufacturing **0/6**, software **11/14**, all seven motors OFF; PR kept Draft and base `main` unchanged.

## Engineering production, not just task tracking — 2026-10-16

New separately downloadable **verified engineering assets**: P3 / TRAY / BACK_WOOD *nominal* CAD section planes each as 1:1 A3 PDF + editable SVG + DXF; 86 contour/hole analysis rows, 7 real gear-shaft datums, plus a 32-row M1 BOM delta and updated nine-sheet tracker Excel. The ZIP assets are distributed as a conversation handoff package and tied to the immutable D7 SHA; GitHub tracks their precise scope, SHA evidence, [engineering output report](increments/2026-10-16-engineering-output.md), [CAD slices](increments/2026-10-16-cad-register.csv) and [M1 quantity contract](increments/2026-10-16-m1-quantity-contract.json). Three drawing sets and one BOM set are **new intermediate artifacts**, not artificially four more `DONE_SCOPE` tasks: frozen 16/48 remains unchanged. Safety 0/6; 11/14. 
