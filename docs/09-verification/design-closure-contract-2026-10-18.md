# Forest Guardian — Design Closure Contract (2026-10-18)

Status: WORKING. This document defines a finite closure target, not an assertion of readiness.

## Scope freeze
Do not add phases or requirements solely to improve the progress count. Preserve the existing 48-item ledger and its source-of-truth statuses. Do not mark an item DONE without the evidence already required by that item. Keep the long-running review branch separate from main.

## Six deliverables for design closure
1. **Electrical:** one authoritative, editable KiCad schematic, manufacturer-verified pin mapping and ratings, reconciled ERC, motor power-off and re-arm interlock documented. Open safety-critical ERC errors block closure.
2. **PCB:** editable PCB matched to schematic, footprint and netlist cross-check, DRC report and manufacturing exports. Export existence alone is not approval to fabricate.
3. **Mechanical:** dimensioned housing, gear and display assembly, seven individually replaceable axes, front/rear service access, thermal outlet and interference evidence. Previously blocked rear-wood fan locations are not permitted without redesign and revalidation.
4. **BOM:** unique manufacturer part numbers, quantities, electrical/mechanical compatibility, source or substitution status, and unresolved procurement risks.
5. **Integration:** wiring/interfaces, firmware and web control behavior, boot/reset/STOP/watchdog/fault/re-arm states, and cross-domain consistency evidence.
6. **Handoff:** versioned drawings, source CAD, fabrication outputs, assembly instructions, verification plan, known risks and a sign-off checklist.

## Blocking dependencies — resolve before claiming closure
- Separate the MTR-09-024 / MTR-09-004 ULN2003 driver-board variants from the actual motor; identify the motor by attributable manufacturer/order code and verify its electrical and mechanical specifications.
- Record actual motor starting/stall/current envelopes and 5V supply/eFuse limits; assumed current cases are not measured acceptance.
- Validate true motor-rail fault sensing, independent power interruption, fault latching and safe re-arm at schematic level.
- Close actual KiCad ERC/PCB DRC, footprints, power integrity and thermals.
- Resolve rear-wood fan outlet blockage and mounting feasibility in the source geometry.
- Verify the complete seven-axis replacement path and enclosure/display interference.

## Non-negotiable safety gate
Until physical evidence and the existing manufacturing acceptance gates are satisfied: motor eFuse EN remains pulled LOW, motor phase outputs remain disabled, no motor energizing, no purchase/fabrication/cutting/flashing, and no merge to main. Design closure and hardware release are separate decisions.

## Minimal test policy
For each scoped change run directly affected checks plus the lightweight ledger/PR gate. Run complete integrated regression at the final design-closure candidate, or when shared infrastructure changes. Do not use simulated or ideal-logic results as proof of physical behavior.

## Completion reporting
Report only: (a) ledger DONE/48 from the source of truth, (b) manufacturing accepted/6, (c) the exact changed artifact/commit, (d) newly closed blockers, and (e) the next blocking dependency. Never count this planning document as an engineering item completed.
