# Forest Guardian — independent secondary keeper for all seven M1 drive cassettes

**Review only. Initial candidate dated 2026-10-16; X-layout revision dated 2026-10-19.** D7 design original remains unchanged, 7 independently removable modules preserved (A-plan). The previous 14 rigid bayonet keys can lock axially, but could be undone by unintended **-Y 2.5mm** slide. This engineering increment adds **one headless M2×5mm set-screw candidate per axis**, placed beside the Y-return corridor. Removing only that axis's screw allows reverse Y then individual 55mm +Z service.

### What is physically modeled and calculated

- Immutable canonical 1,774 D7 solid original SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`. Its actual 65MB CAD file was checked against the earlier boss revision; the 2026-10-19 seat/bore candidate has separate source-bound evidence for its exact seven seat and bore positions (1,774 solids). That screen is not a physical wood cut or fan relocation, and CI does not redo the full source intersection. Structural installation remains unqualified.
- Current seven-axis candidate places seven M2×5mm *headless* screws at `(x+22.95,y-1.1)`, upper surface Z139.35. Seven 3.3×3.95mm fixed bosses at X `(x+21.3)..(x+24.6)` (Z134–138) have reviewed 2.05mm bores; the bore is NOT a manufactured tap or a qualified thread. Bosses remain inside the nominal ±25mm reserved width. Screws cannot be claimed as captive or vibration-resistant.
- Locked bar occupies Y `+0.5..+4.5mm`. Installed screw occupies Y `-2.1..-0.1mm`. **0.6mm nominal clearance** when locked; trying to move the bar in -Y contacts the screw after 0.6mm, **before the 2.5mm travel needed to unlock**. Remove screw to unlock. This is *positive geometry*, not mechanical endurance proof.
- New screw bosses would obstruct the old cassettes **7/7 axes during full +Z55mm withdrawal**. The current candidate creates a **1.9×4.85mm through-height window in the removable 44×35mm cassette wall**, and retains the original bar, two rigid guide keys and P3 intact.
- Full D7-derived generator, **714 position stage checks**, engineering load/tolerance and actual A3 1:1 PDF/DXF plus preview and a watertight single-boss STL in the companion ZIP. Github houses a compact native [7-axis OpenSCAD model](M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad), [screw and dimensions contract](design_contract.json) and [independent nominal 714-stage CI model](check_motion.py).

### Initial X-layout finding (2026-10-16; superseded by the 2026-10-19 candidate below)

The original 40mm *conservative* board envelope had only 0.3mm clearance to the through-height cassette notch and failed the assumed ±0.2mm two-part X tolerance screen by 0.1mm. That baseline geometry is superseded. No board dimension was reduced; the revised candidate retains the conservative 40mm envelope and shifts the fixed boss outward. The MTR-09-024 listing remains unmeasured and is not used as an acceptance substitute.

Other blockers: M2 tap/engagement material and prevailing torque, screw self-loosening, corner/shear, shell warp, heat creep, rearwood pocket Z140 gives just 0.65mm nominal headless clearance, fan relocation/airflow, electrical independent eFuse latch/PG/STOP bench proof.

**Project ledger at 2026-10-19 continuation:** 21/48 narrowly scoped done, 8 working, 15 open, 4 hardware-wait; manufacturer gates **0/6**, software evidence **11/14**. These counts are cross-checked against `execution/tasks.csv` and `execution/progress.json`. U7 motor eFuse EN held LOW; no manufacturing, drilling, purchasing, energizing, flashing or merging `main`. PR stays Draft.

The hardware design remains **NOT ACCEPTED**. The same-dimension relief candidate is now integrated into the keeper SCAD as optional separate cutter geometry and reconciled by `check_motion.py`; the immutable source screen records the axis-5 fan overlap. Next tasks are fan relocation, source-bound integrated model verification, measured module dimensions/process capability, anti-loosening and structural fixture tests.

## 2026-10-19 — current outboard boss checked against the complete source D7

The source audit now rehashes the canonical 65,483,374-byte `assembly.json` (SHA256 above; 1,774 solids) and intersects the current X/Y/Z boss envelope against every XY, XZ, and YZ source prism. Reproduce with:

```sh
python3 execution/secondary_keeper_2026-10-16/audit_full_d7_clearance.py /path/to/CANONICAL_D7/cad/assembly.json --output execution/secondary_keeper_2026-10-16/evidence/full_d7_shifted_boss_intersections.json
```

The same checker now accepts candidate bounds relative to each axis and can enforce zero boss/source intersections:

```sh
python3 execution/secondary_keeper_2026-10-16/audit_full_d7_clearance.py /path/to/CANONICAL_D7/cad/assembly.json --x-offset 21.5 24.8 --y-offset -3.75 0.2 --z-range 134 138 --require-clear
```

`--require-clear` exits nonzero if any source solid intersects a boss. Each reported collision carries the source array index as well as the solid ID because the canonical D7 includes duplicate IDs. A clear boss-volume result still says nothing about tool corridors, service sweep, tolerances, strength, fan airflow, or physical fit. Geometry helper tests that do not need the 65MB source run with `python3 execution/secondary_keeper_2026-10-16/test_clearance_audit.py`.

The historical shifted-boss audit also checks each installed M2 stud's **vertical centerline** at the former contract location `(axis_x+23.15, axis_y−1.1)`, Z134.35..139.35. This is a necessary-path check only: a hit proves the stud crosses source material; a clear centerline would not prove radial or driver-tool clearance. Reproduce via the same command; the report's `stud_centerline` section lists exact source solid indices and Z overlap.

**FAIL for the unmodified D7 layout:** all seven current bosses overlap existing `BACK_WOOD` by 13.035mm³ each; axis 5 additionally overlaps `FAN_MAX_BODY` by 26.07mm³ and `FAN_GASKET` by 13.035mm³. No other source solids intersect these boss envelopes in this audit. The rear wood must be relieved or the boss redesigned, and the axis-5 fan must be relocated or that boss redesigned. These interferences invalidate clearance for this candidate until a revised source-bound audit passes. The 2.4mm tool corridor, module dimensions, process tolerances, fastening strength, vibration retention, and physical 55mm exchange remain unverified. This report is not a woodworking approval and does not change G2-07 OPEN / G3-04 WORKING or any manufacturing gate.

**Additional independent blocker:** all seven stud centerlines cross existing `BACK_WOOD` for 2.35mm of their 5mm modeled length; axis 5 additionally crosses the fan body for 1.65mm and gasket for 1.0mm. Therefore shortening the rectangular boss to stop at Z137 does not resolve the keeper: it leaves the stud path through unmodified back wood, and the axis-5 fan clash remains. This is a source-geometry finding, not a proposed cut. Any backwood relief, new access bore, relocation, or retention redesign needs its own wall-strength, fan, tool-access, and full-envelope verification.

## 2026-10-19 — conditional X-layout candidate (overall HOLD)

The initial X-layout above is superseded. Moving each fixed boss outward from X `20.5..24.0` to `21.5..24.8` and shifting the screw center from `22.25` to `23.15` retains a nominal **0.625mm** minimum bore-to-boss wall and stays within the ±25mm reserved width. A through-height cassette notch at X `20.6..22.5` gives 0.6mm nominal clearance to the conservative 40mm board envelope, or **0.2mm worst-case X clearance** under the stated ±0.2mm two-part tolerance assumption. The notch extends past the cassette wall edge at X22 by 0.5mm nominal (0.1mm worst-case under the same two-part screen). The screw still overlaps the 48mm lock bar by 1.85mm nominal and retains the nominal 0.6mm Y travel-to-contact stop before the 2.5mm unlock travel.

The original candidate's Y-notch margin was only 0.15mm each side of the boss and the bar-to-sled Z gap was 0.05mm; both fail the assumed ±0.2mm-per-part screen. The current parametric revision extends the notch to Y `−4.2..+0.65` and raises the bar from Z `138.05` to `138.6`. The nominal two-part screen then yields 0.45mm Y clearance each side and 0.5mm Z clearance, or **0.05mm Y and 0.1mm Z worst-case** after applying the assumed ±0.2mm per-part stack. These are small calculated margins, not demonstrated manufacturing capability. Full-D7 shifted-boss clearance, the measured PCB/fastener, strength, vibration and physical 55mm service remain unverified. The prior full-D7 zero-collision result applies only to the previous boss position and is not carried forward. Manufacturing remains blocked pending full-geometry and physical evidence.

## 2026-10-19 — candidate local rear-wood seats and tool bores (not released; now modeled with the keeper)

The full-D7 source supports a localized machining candidate rather than a broad rear panel pocket. Proposed revision shifts each boss/screw X center inward by 0.2mm (boss X `21.3..24.6`, screw center X `22.95`) while retaining the modeled 0.625mm minimum boss wall. It adds seven **4.1×4.75×1.6mm** shallow seats at Z `137..138.6`, centered at axis offset `(22.95, −1.775)`, plus seven **Ø3.2mm** rear tool/fastener clearance bores centered at `(22.95, −1.1)` through the `BACK_WOOD` thickness. The cut-box margin to the modeled boss is 0.4mm per side; the candidate seat stays within the ±25mm X reservation and existing cassette notch envelope.

Source-bound screen against all 1,774 canonical D7 solids reports all seven seats wholly within existing wood; the conservative 3.2mm square bore envelope meets only full wood or full existing void at each original slice; the closest seat edge is 1.5542mm from an existing D7 material boundary (axis 5). The 3.2mm square driver corridor has no fixed nonwood collisions after accounting for the common removable rear grille, which the G6-06 sequence removes before access. **This is a machining geometry screen only:** the X shift and the candidate cutters have now been integrated as optional geometry in `M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad` and reconciled against the same-dimension source screen; the SCAD does not subtract material from the D7 wood solid. The axis-5 boss still intersects the original fan/gasket, and no wood strength/grain, process tolerance, fit, fastener load, tool-handle or physical service test has passed. The original fan relocation must be integrated. No broad G5 pocket is proposed.

Reproduce with `python3 execution/secondary_keeper_2026-10-16/audit_keeper_wood_reliefs.py /path/to/CANONICAL_D7/cad/assembly.json --output execution/secondary_keeper_2026-10-16/evidence/keeper_wood_relief_candidate.json`. The keeper SCAD defaults `SHOW_WOOD_CUTTER_OVERLAY=false`; set it true to view the seven local seats and rear clearance bores in registration with the keeper. This remains review geometry, not a machining release. Do not manufacture from it. G2-07 remains OPEN and G3-04 remains WORKING.

## 2026-10-19 — conditional Y/Z tolerance candidate (overall HOLD)

Updated native CAD and the independent checker now include the Y/Z screen. The through-height relief is `1.9×4.85×15.2mm`; lock bar and guide crossbars are shifted upward 0.55mm while retaining 0.75mm nominal vertical overlap with the installed stop screw. The checker derives worst-case Y notch clearance (0.05mm each side) and cassette-to-bar Z clearance (0.1mm) from the stated assumed ±0.2mm per-part tolerance. This is a mathematical stack only: no process capability, dimensional measurement, full D7 recheck, physical fit or load test is represented. Current candidate remains **CAD_CANDIDATE_NOT_FOR_MANUFACTURE**.


## 2026-10-19 — keeper CAD integration review

`M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad` now uses the screened inward 0.2mm boss/stud shift (`x+21.3..24.6`, screw `x+22.95`) and contains a default-off `SHOW_WOOD_CUTTER_OVERLAY` for the seven 4.1×4.75×1.6mm seats and Ø3.2mm rear access bores. The overlay is intentionally separate because this lightweight model does not contain the canonical D7 wood solid; it must not be mistaken for an actual boolean-machined back panel. `evidence/integrated_keeper_wood_relief_review.json` reconciles the model dimensions to the prior full-source candidate screen.

The existing candidate screen reports all seven seats fully inside existing wood, each conservative bore envelope is full wood or full void on every slice, zero fixed-part driver corridor intersections after removing the specified rear grille, and 1.5542mm minimum seat-to-wood boundary distance. Existing axis-5 fan/gasket intersections remain. The local dimensional screen also retains assumed worst-case clearances X=0.2mm, Y=0.05mm, Z=0.1mm, and models 0.425mm worst-case radial bore wall under the assumed ±0.2mm/part tolerance. These are geometry/tolerance calculations, not process capability.

Run the keeper motion/parameter reconciliation with `python3 execution/secondary_keeper_2026-10-16/check_motion.py`; render the keeper candidate with `openscad -o /tmp/keeper.csg execution/secondary_keeper_2026-10-16/M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad`. The optional cutter overlay can be enabled using OpenSCAD's `-D SHOW_WOOD_CUTTER_OVERLAY=true`. G2-07 remains OPEN, G3-04 WORKING, release gates 0/6.


## 2026-10-19 — conditional axis-5 fan relocation geometry candidate

The earlier source audit reports an axis-5 boss collision because it tests the **unmodified** D7 with the original FAN_MAX_BODY/FAN_GASKET installed. A new 1,774-solid source review models that original `FAN_*` assembly as relocated and screens a 30×30×10mm external fan envelope at XY(220,40), a 45mm adapter envelope and conservative square through-port path. The fan, plate and nonwood duct checks have zero fixed-source intersections; the square path also misses the modeled rear grille at this site. It clears all seven conditional 50×41mm service reservations by at least 32.5mm. The 7-axis keeper can therefore proceed geometrically with the fan-relocation candidate, but the fan/keeper/new panel-hole system is not an accepted assembly. See [G3-06 source report](../fan_relocation_2026-10-19/README.md) and [full-source candidate audit](../fan_relocation_2026-10-19/evidence/candidate_source_audit.json). The relocation changes the existing rearwood and fan architecture, requires a new Ø29.7mm backwood vent and external grille/guard, and remains uncut, unpowered and thermally unqualified.
