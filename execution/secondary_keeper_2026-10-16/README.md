# Forest Guardian — independent secondary keeper for all seven M1 drive cassettes

**Review only, dated 2026-10-16.** D7 design original remains unchanged, 7 independently removable modules preserved (A-plan). The previous 14 rigid bayonet keys can lock axially, but could be undone by unintended **-Y 2.5mm** slide. This engineering increment adds **one headless M2×5mm set-screw candidate per axis**, placed beside the Y-return corridor. Removing only that axis's screw allows reverse Y then individual 55mm +Z service.

### What is physically modeled and calculated

- Immutable canonical 1,774 D7 solid original SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`. Its actual 65MB CAD file was read and checked in the local generation harness against all seven stop-boss bodies (Z134–139.35) and **7 Ø2.4mm/24mm nominal rear-tool corridors**; zero original fixed-body projected intersections after removing the common BACK_WOOD/grille and allowing the still-uncompleted original fan relocation. **CI does not redo the 1,774-solid D7 intersection**, and the future structural installation is still unqualified.
- Seven M2×5mm *headless* screws at `(x+22.25,y-1.1)`, upper surface Z139.35. Seven 3.5×3.95mm fixed bosses (Z134–138) with reviewed 2.05mm bore; the bore is NOT a manufactured tap or a qualified thread. Screws cannot be claimed as captive or vibration-resistant.
- Locked bar occupies Y `+0.5..+4.5mm`. Installed screw occupies Y `-2.1..-0.1mm`. **0.6mm nominal clearance** when locked; trying to move the bar in -Y contacts the screw after 0.6mm, **before the 2.5mm travel needed to unlock**. Remove screw to unlock. This is *positive geometry*, not mechanical endurance proof.
- New screw bosses would obstruct the old cassettes **7/7 axes during full +Z55mm withdrawal**. The candidate creates a **2×4.25mm through-height window in the removable 44×35mm cassette wall**, and retains the original bar, two rigid guide keys and P3 intact.
- Full D7-derived generator, **714 position stage checks**, engineering load/tolerance and actual A3 1:1 PDF/DXF plus preview and a watertight single-boss STL in the companion ZIP. Github houses a compact native [7-axis OpenSCAD model](M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad), [screw and dimensions contract](design_contract.json) and [independent nominal 714-stage CI model](check_motion.py).

### Key **FAIL** (do not override)

The mandatory 40mm *conservative* board envelope lies **only 0.3mm from the new through-height cassette notch**. At assumed ±0.2mm tolerance on each of two parts, margin **0.3−0.2−0.2 = -0.1mm**. Thus the 40mm scenario FAILS even if the screw-stopper motion passed. The vendor's nominal 35×31mm MTR-09-024 dimensions would yield 2.8mm nominal, 2.4mm worst margin under the same assumptions, **but neither actual PCB width nor mounting pattern has been physically measured**, and no material or mechanical acceptance is closed. Do not reduce conservative footprint until real module measurement.

Other blockers: M2 tap/engagement material and prevailing torque, screw self-loosening, corner/shear, shell warp, heat creep, rearwood pocket Z140 gives just 0.65mm nominal headless clearance, fan relocation/airflow, electrical independent eFuse latch/PG/STOP bench proof.

**Progress invariants:** 16/48 narrowly scoped done, 8 working, 20 open, 4 hardware-wait; manufacturer gates **0/6**, software evidence **11/14**. U7 motor eFuse EN held LOW; no manufacturing, drilling, purchasing, energizing, flashing or merging `main`. PR stays Draft.

The hardware design remains **NOT ACCEPTED**. Next task is to eliminate the negative 40mm tolerance budget by redesigning the boss/holder or getting a measured MTR-09-024 board, then implement a retaining/captive solution that cannot self-unscrew and prove it in a printed/metal trial fixture.
