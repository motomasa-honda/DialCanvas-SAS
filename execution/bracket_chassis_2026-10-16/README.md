# Seven-axis M1 individual cassette support engineering — 2026-10-16

**New real artifacts. NOT FOR FABRICATION.** This is a material increment toward G3-04/G3-05, not completed G3 manufacturing acceptance. D7 original 1,774-solid `assembly.json` SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f` remains unmodified.

## Verified historical failures
- A proposed full 48×39mm fixed platen at Z116–119 overlaps unchanged D7 hardware/motor/sensor volumes in **5/7 axes: G1/G2/G3/G4/G6**.
- Conservative Ø2.4mm straight P3 support post search Z98–123 has **no allowed discrete support location for G5/G7**. This disproves that scoped post scheme, NOT every alternative geometry.

## Generated engineering design

The included **native parametric OpenSCAD design** `M1_7_CASSETTE_SERVICE_CHASSIS.scad` (passed OpenSCAD syntax export) concretely models:
- 1 nominal shared peripheral 3mm-wide support ring at Z130–133 (4 bars), where D7 fixed geometry had zero projected interference;
- 7 *independently removable* 44×35×15mm sled candidates, one per axis, 40.8×31.8 inner envelope over assumed 40×31×15mm module;
- 14 fixed side guides Z123–136.5, 14 algorithmically routed nominal 1.92mm-wide support webs (0 collisions with source D7 at Z130–133 and zero source board/sled sweep obstruction), 21 source-chosen lower support tabs (3 per axis);
- 7 separate rear lock bars, requiring removal before pulling only that module +Z55mm.
- 7 redesigned 48×35mm by 3mm-deep rear-wood pocket screening zones, all nominal at least 8mm from external BACK_WOOD rectangle; physical thickness/strength and fastener-head clearance unproven.
- 14 independently accessible **2.6mm-diameter hypothetical tool corridors** clear of unchanged D7 swept geometry and the other 6 modules; real fastener, driver head, retention boss or torque not specified.

Rear removable panel also gets a **275mm nominal ~3mm-wide routed reinforcing rib**, fully above wood substrate at the canonical Z137.5 plane, with zero D7 fixed/7 pocket nominal intersections at Z135–137. This is a route **proposal** only; rear-panel laminate, adhesive, screw retention, actual wood thickness and strength have not been validated.

## Evidence, not claims

Companion handoff ZIP `Forest_Guardian_Seven_Axis_Bracket_And_Rearwood_Design_2026-10-16.zip` (SHA256 `edc01bb6f1ea5239329e0c210a8511c5ba3cc7c03511bf0c36457d50f6cd4b73`) contains **complete native .scad / editable .dxf / two actual 1:1 A3 .pdf/.svg** plus OpenSCAD preview PNG, 21-stop/14-web/14-tool/7-wood-pocket CSVs, D7 source regeneration/test scripts, 13-sheet existing tracker with additional engineering review tab, test evidence and SHA manifest.

**This GitHub tree holds only versioned machine-readable evidence plus review scope; the full native CAD files are in the verified downloadable user ZIP, NOT present in the GitHub branch.** Any GitHub CI for the JSON must be labeled **STATIC CONTRACT ONLY**; the **1,774-solid CAD computation was run separately in this development runtime** and source scripts are provided in the ZIP. Do not claim CAD was revalidated by GitHub Actions unless the original source and generator are added to CI later.

## Binding defects — safe parallel work

1. **Crucial:** The shared frame currently has no *verified mounting anchor to wooden casing*. A free-floating ring is not a completed support. Keep G3-04 WORKING.
2. Module vendor physical height/hole/connector positions and front underlip contact surfaces unknown. A 0.4mm nominal clearance is not a verified tolerance. Physical fastener bosses and locking screws do not yet exist.
3. The fan must relocate; thermal/pressure/electrical draw and new rear vent remain OPEN.
4. Rear wood 48×35mm relief/reinforcement introduces actual material/strength/connector risk; NO machining.
5. Continue hardware STOP/manual rearm/PG/independent watchdog safety design in parallel. Motor eFuse EN **LOW**, no power/flash/fabrication or purchase.
6. D7 main CAD, gears and P3, and the other six motor modules remain in place during independent replacement; user approved A-plan still first choice.

**Ledger unchanged:** 16/48 narrowly scoped jobs done (not a product completion percent), 8 working, 20 incomplete, 4 hardware-wait; manufacturing gates **0/6**, software evidence **11/14**. Keep Draft PR #2 and branch `review/forest-guardian-phase66-idf`; do not merge into main.

Next: solve **real 4-point chassis anchors** with actual case wood part geometry and native CAD, finish 14 screw bosses and tool-envelope check, verify actual module SKU and 3mm rear-cover pocket/tolerances, design qualified fan/vent. No Phase inflation.
