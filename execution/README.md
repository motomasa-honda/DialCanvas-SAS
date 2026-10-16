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

## 7-axis rear-service layout — concrete CAD geometry (2026-10-16)

[Real geometry-derived engineering increment](cassettes/README.md) contains seven independently positioned modules with one A3 plan PDF/SVG, three editable DXFs (7 modules, rear wood pocket screening, fan alternative footprint), parametric 3D SCAD, Z-extraction section A3 PDF/SVG, and the source-verified XY/YZ/XZ 1774-solid collision audit in the companion conversation ZIP. **Seven modules achieve nominal 55mm rearward swept clearance only if the original fan assembly is redesigned/relocated and rear BACK_WOOD cover is removed before servicing.** Existing 60mm fan staying in place: no seven-module solution on the stated 5mm grid. Existing back panel Z137 overlaps assumed modules Z123–138 by 1mm; 3mm pocket is a proposed/unapproved woodworking revision, and vendor module height is unmeasured. A 30mm fan footprint has five 2D candidates but needs qualified cooling, power and an actual rear vent.

Reproducible GitHub [review CI run 38827856490](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38827856490) verifies the derived layout manifest, seven reservations, no unauthorized power, and preservation of 0/6. **The original full-D7 CAD recomputation is archived in the engineering ZIP, not re-run by this particular GitHub workflow.** Outcome-scoped tasks stay **16/48** because no complete 7-axis retention assembly/PCB/wood tool access has been approved.

## Tangible mechanical CAD increment: independent 7-axis sled support — 2026-10-16

New downloadable **source-based 3D** design and **rear wood** reinforcement artifacts, tracked in [review dossier](bracket_chassis_2026-10-16/README.md): per-axis 7 removable 44×35 sleds, 14 fixed guides, 14 perimeter-frame webs, 21 nominal source-clear lower stops, 7 detachable locking bars, 14 nominal tool corridors; expanded 7 backwood pocket outlines and a 275mm conceptual strengthening rib, each in native CAD. Actual D7 original solids (1,774) were checked at source SHA `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`; **do not misrepresent Github manifest checks as rerunning the original full CAD**. Previous full-plate scheme fails 5/7 axes; P3 straight anchors fail G5/G7 on the search grid; the new frame has no load-certified case anchors. Full native SCAD/DXF/PDF/regen code are in the companion engineer ZIP, not GitHub itself.

**Completion counts unchanged** because fixed frame mounting, true screw geometry, PCB SKU fit, thermal, wood strength and independent eFuse safety remain unapproved: **16/48 scoped artifacts**, manufacturing **0/6**, software **11/14**. No machine power, cutting or purchasing.

## Actual positive key mechanics, 14/14 — 2026-10-16

[Seven-axis bayonet native CAD + CI](bayonet_2026-10-16/README.md): replaced nonfunctional thin clip envelopes with matched rigid keys + fixed-rail entry slots and undercut guide lips on **both sides of all 7 axes**. Source-verified local D7 fixed-geometry audit PASS; 14/14 full entry-slide-capture-reverse NOMINAL kinematics PASS (3,416 sample states). **Run 38841326432 SUCCESS**, 42 injected geometry failures detected. But the **secondary reverse-slide keeper IS UNDESIGNED**, and min 0.60mm positive hook overlap / 0.95mm lip must be physically qualified. `G3-04` remains WORKING (not DONE_SCOPE) and `16/48`, manufacturing `0/6`, software `11/14` remain unchanged. Review sheet + native 3D & STL are in the user engineering ZIP; direct GitHub native CAD model is a small G1 and minimal 7-axis model, not the full source D7 project.
