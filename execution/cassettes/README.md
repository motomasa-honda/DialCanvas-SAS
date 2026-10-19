# Seven replaceable M1 cassette layout — tangible CAD engineering increment

**Source CAD:** `CANONICAL_D7/cad/assembly.json`, 1,774 solids, SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`. **NO D7 geometry was modified.**

## What the CAD calculation established
We screened the full D7 XY/XZ/YZ geometry projected onto Z123–137 using exact planar intersections and a 5mm-grid 0/1 mixed-integer layout solver. Seven separately assigned **40×31mm PCB conservative envelopes**, each within **50×41mm reservation (5mm/side)**. We repeated the swept check through Z193 corresponding to a full +55mm move from a nominal PCB body at Z123..138.

| Condition | Feasibility on this fixed 5mm grid |
|---|---|
| Back cover / grille / rear fasteners removed; **existing fan kept** | **INFEASIBLE**, 74 admissible XY points |
| Same, but original 60mm-class fan and all FAN_* mounting hardware relocated | **SEVEN CANDIDATES FOUND**, 321 admissible points, 7/7 conditional fixed-D7 solids sweep-clear |

The fan relocation is **a real design dependency, not a completed fix**. With seven modules allocated, the same rear-depth plane shows zero 60.5×60.5mm or 40×40mm candidate fan footprints, but five 30×30mm nominal points; that does not prove airflow/noise/supply performance. The sample 30mm XY site at (95,90) is **98.9% covered by original rear wood** at Z137.5, so a different grille/vent must also be designed. Candidate motor fan 109mA versus prior supply 100mA remains an unresolved safety/power issue.

## Seven axes, rear +Z motion (mm)

| M1 axis | X | Y | min visible backwood edge margin | motor-centre distance* |
|---|---:|---:|---:|---:|
| G1 | 85 | 40 | 6.5 | 40.0 |
| G2 | 55 | 140 | 17.0 | 27.61 |
| G3 | 135 | 140 | 31.5 | 24.0 |
| G4 | 225 | 130 | 7.0 | 25.68 |
| G5 | 140 | 85 | 51.5 | 95.0 |
| G6 | 50 | 85 | 12.0 | 25.5 |
| G7 | 140 | 40 | 6.5 | 57.76 |

*This is ONLY XY centre distance, **NOT** physical harness length. Same for 55mm, an extraction motion envelope, never a conductor cut-length requirement.*

**Hidden physical clash still OPEN**: assumed module height 15mm at Z123..138 overlaps original rear wood starting Z137 by 1mm. Proposed 3mm rear-side pocket yields nominal residual 5mm in locally continuous 8mm wood, but neither cut-out ligament, recessed screws, 7 independent module brackets, connector mating/bend radius, actual PCB thickness, thermal or strength has been qualified. Existing P3 and seven decorative gears MUST remain installed when swapping an individual driver; the same cover may be opened without removing other six modules.

## Produced design assets

Companion downloadable engineering ZIP includes 1:1 A3 PDF/SVG rear arrangement, original-D7-referenced editable DXF, a separate actual-layer BACK_WOOD seven-pocket **DO NOT CUT** DXF, parametric 3D `.scad`, 55mm section A3 PDF/SVG (explicitly schematic, NOT measured 1:1), fan space DXF, 7-axis service/wood thickness CSVs, full CAD source-recompute script and regression tests, and an updated 12-sheet workbook.

This GitHub review branch stores the transparent [7-axis layout JSON](seven_axis_conditional_layout.json) and [derived materialized-layout guard](check_manifest.py). **The GitHub guard does not re-run the 65MB D7 original CAD**, because the original is only in the separately SHA-pinned user handoff archive; the companion ZIP includes a reproducible recomputation script and physical geometry evidence. No additional 48-scope job is misleadingly declared completed by this limited design step.

**Current 48 tasks:** 16 DONE_SCOPE / 8 WORKING / 20 OPEN / 4 HARDWARE_WAIT; manufacturing gate **0/6**, SW **11/14**. 7-module placement is an engineering *candidate*, not an approved tool path. Electrical watchdog/trip latch, PG and 5V STOP HIL stay OPEN; **eFuse EN LOW**.

**No fabrication, no cut, no purchases, no power, no flashing, no merge to main.**
