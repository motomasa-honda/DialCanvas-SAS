# Forest Guardian — Parallel Execution Board / v1.0 (2026-10-16)

**From now on measure completed artifacts, not Phase counts.** The approved 7-axis individual-replacement A plan, D7 CAD reference and conservative physical safety gate remain unchanged.

## Frozen task inventory
Exactly **48 independently scoped deliverables**: eight in each of the six D7 manufacturing gate disciplines. Details in [tasks.csv](./tasks.csv). Current counts:

| Scope | DONE_SCOPE | WORKING | OPEN | HARDWARE_WAIT | Gate |
|---|---:|---:|---:|---:|---|
| G1 Real electrical / PCB | 4 | 2 | 2 | 0 | OPEN |
| G2 Complete physical harness | 3 | 0 | 4 | 1 | OPEN |
| G3 Mechanical/wood/thermal | 3 | 2 | 2 | 1 | OPEN |
| G4 BOM, specs, fabrication drawings | 2 | 1 | 5 | 0 | OPEN |
| G5 Product SW integration | 4 | 1 | 2 | 1 | OPEN |
| G6 All A3 patterns and assembly sequence | 3 | 0 | 4 | 1 | OPEN |
| **TOTAL** | **19/48** | **6** | **19** | **4** | **0/6 closed** |

The current **19 scoped passes** include previous 16 reviewed milestones plus NEW G4-02 full original BOM reconciliation and NEW G6-02 seven-panel internal A3 review drawing set. These are **NOT 18 complete manufacturable assemblies** or a cleared hardware safety review. Software evidence **11/14**, remaining SW09, SW12, SW14.

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

## Confirmed new scoped completion G4-02 — 2026-10-16

**SOURCE RECOVERY BREAKTHROUGH**: The old 429-line `d7/bom/unified-bom.csv`, original 18-line `d7/bom/m1-module-bom-addendum.csv`, and 68 original wood machining operations were found INSIDE the nested `forest-guardian-chatgpt-handoff.zip` in the Phase67 legacy baseline. The contained 65,483,374-byte `d7/cad/assembly.json` was recomputed to the unchanged D7 SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`.

G4-02 is now **DONE_SCOPE**: every original DRIVER implementation line (**59**) mapped 1:1 into retired/replace/transfer/safety redesign; 28 old R_PD are superseded by exactly 28 M1-phase pull-downs, 4 old TBD drivers retired, 7 existing separate motor fuses retained and 2 MCP breakouts added with no duplicate original DIP28 purchase. The original master BOM omitted old RTC `U609 RX8900` despite the PCB assembly BOM listing it; its exact source line was **recovered**. Integrated audit = **429+18+1=448 source-based rows**, **NO manufacturing release**. The recovered 68 historical wood operations are indexed; their new M1 machining integration is still incomplete. See [full reconciliation and known source conflict](bom_reconciled_2026-10-16/README.md).

Counts now **17 DONE_SCOPE, 7 WORKING, 20 OPEN, 4 HARDWARE_WAIT** (48 unchanged), manufacturing **0/6**, software evidence **11/14**. Previous README historical first-baseline 16/48 description remains a historical milestone, not the latest state. All purchase, power, cutting, flash and main merge forbidden.

## NEW verified scoped completion: G6-02, seven actual internal source-CAD A3 sheets (2026-10-16)

[Detailed source-traced scope and G5 critical original-opening redline](g6_02_7panel_2026-10-16/README.md). All seven real internal D7 geometry sections were produced in **A3 PDF+DXF editable formats**, including the recovered 68 original machining operations without edit and eight nominal anchors/seven rearwood relief candidate overlays. D7 original SHA rechecked, 7 PDF physical media readbacks and DXF reopen checks PASS in companion ZIP. **G5 BACK_WOOD: 81.346% of proposed 48×35mm pocket is already OPEN in original**: do not perform seven uniform cuts. Only G6-02 is DONE_SCOPE; G6-08 and G3-05 remain incomplete. **18/48 done, 6 working, 20 open, 4 hardware wait; 0/6 manufacturing and 11/14 software.** No power, cutting, purchasing, fabrication, flash or main merge.

## G6-03 DONE_SCOPE — D7 all named interior/gear/lighting/sensor components, both real faces (2026-10-16)

**19/48 DONE_SCOPE** (G6-03 OPEN→DONE_SCOPE). Immutable actual D7 1,774 original solids were used locally to generate **80 uniquely identified physical panel/gear/LED/sensor/lighting components × LOW/HIGH = 160 distinct side projections** as 1:1 A3 PDFs and 160 native DXFs; matched 160-page A3 book, source face geometry JSON, physical page and 160 DXF source-area readback. [Full scoped evidence and engineering limitations](g6_03_80_source_faces/README.md). G5-back Z144.99 has **zero material** in the proposed pocket; new G5 2x steel3×6×65 support webs satisfy nominal source D7 clearance but actual strength/fatigue remain unqualified. M2 stop V2 improves conservative 40mm board worst clearance from -0.1 to +0.55mm with thread residual wall thickness <0.6mm **NOT strength accepted**. Manufacturing remains **0/6**, software review **11/14**, all motor eFuse EN LOW; G6-08/CNC/printing, G3 structure, G1 electrical stay OPEN. Deliverable ZIP source+all native drawings is linked in the conversation; GitHub static source-index check cannot substitute original D7 geometry recomputation.

## G5 support bracket geometry & G6-04 23 panel thickness review (2026-10-16)

[New actual G5 13-volume 3D frame and audit](g5_frame_2026-10-16/README.md) (source D7 1,774 original solids checked locally): replace flexible front 3x3 member by 6x9mm, route LEFT arm between G1/G7 service buffers, RIGHT arm Z116–123 below unchanged battery, then rise at Y93, avoiding all other six 50x41mm service buffers by >=1.0mm. **Original fan guard still clashes: relocation required**; 12 positive-volume joints physically unqualified. 23 panel stations audited for G6-04: 14 constant, 9 stepped, no glue or machine use approval. No formal 48-task closure: **19 DONE_SCOPE / 6 WORKING / 19 OPEN / 4 HARDWARE_WAIT**, manufacturing **0/6**, software **11/14**, eFuse EN LOW.
