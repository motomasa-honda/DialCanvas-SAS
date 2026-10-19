# Forest Guardian — manufacturing readiness contract (2026-10-18)

## Objective and definition of design completion
Design is complete only when a fabricator/assembler can purchase, manufacture, wire, program and assemble one working desk clock without making unresolved engineering decisions. A review drawing, logical net, passing process guard, or scoped task count does not grant release.

## One source of truth
- `execution/tasks.csv`: 48 delivery work items and evidence paths.
- `execution/progress.json`: review-scope count, **not** manufacturing readiness.
- This file: release acceptance and critical path. Preserve existing task IDs; do not create new phases as substitutes for closing them.
- Manufacturing release: 0/6 until independently evidenced; no fabrication, ordering or energization authority from this contract.

## Critical path, in execution order
| Package | Required engineering output | Acceptance evidence | Depends on |
| --- | --- | --- | --- |
| 1. Motor and safety electrical | G1-05/06 integrated native KiCad schematic, latched STOP/FAULT, default-off eFuse EN, verified supply/driver ratings | native ERC clean; pin-to-datasheet review; safety truth table and independent fault tests on bench **before** motor enable | actual module connector pinout, safety IC and power design |
| 2. PCB and manufacturing | G1-07/08 and G4-03/05: native PCB with verified footprints, stackup, DRC, Gerber, drills, pick/place and fabrication notes | native DRC/ERC, gerber/drill re-import, footprint dimensions and netlist match; fabricator quote | package 1 |
| 3. Seven serviceable drives | G3-04/05/07 and G2-07: real 3D cassette, mounts, fasteners, extraction tool envelope, cooling relocation | exact vendor mechanical dimensions, source CAD interference/tolerance report, tool access and 55mm sweep; physical confirmation after prototype | real PCB outline/connectors and original CAD |
| 4. Harness | G2-03/04/05: 178 endpoints, 42 axis pins, 3D routed harness, cut lengths, connector series, crimps, strain relief | pin-1/orientation independent review, route and bend clearance, continuity traveler | packages 1–3 |
| 5. Wood/thermal/appearance | G3-06/07, G4-06, G6-04/08: complete cut/print/drill drawings, joints, fasteners, fan and airflow | full dimensioned CAD and 1:1 drawing inspection, adhesive/wood specifications, electrical fan branch budget and thermal verification plan | packages 2–4 |
| 6. Firmware, purchasing, release | G5-05/06/07, G4-04/07/08: flashable production build, security and rollback, complete purchasable BOM, assembly and inspection | reproducible builds, signed OTA and fail-safe tests, exact SKUs and costs, release manifest with hashes; HIL tests after physical build | packages 1–5 |

## Work-size rule
Choose the smallest missing **manufacturable** artifact, not another review phase. One work unit must include (a) source edit, (b) automated or independent check, (c) evidence path and residual blockers, (d) a GitHub commit. Prefer a whole task only when all its declared deliverables meet acceptance. Otherwise keep it WORKING/OPEN, and report the actual blocker rather than increase the numerator.

## Current blockers that cannot be silently assumed
1. M1 integrated schematic and independent safety circuit unfinished; motor eFuse EN held LOW. No power-up authorization.
2. Actual motor/driver connectors and mechanical dimensions unknown; logical 42-pin map is not a physical harness.
3. The 60mm fan conflicts with the seven-module layout; the prior 109mA candidate exceeds the 100mA branch. Thermal/electrical redesign required.
4. Original D7 CAD and exact supplier components must be available to generate and validate final fabrication geometry.
5. HTTPS pairing, signed OTA, UI/RTC/network and real-world failure injection still need integration evidence.
6. Real printing, continuity, thermal and mechanical acceptance require a prototype; separate these post-build checks from pre-build design completion, but do not declare production release before safety qualification.

## Reporting rule
Report a new **N/48** only when a task's real deliverable and evidence are complete. For other commits, report the actual manufactured artifact or specific blocker; never imply that 21/48 means 21 manufacture-ready packages. Avoid adding new review-only milestones unless they directly unblock a named manufacturing deliverable.
