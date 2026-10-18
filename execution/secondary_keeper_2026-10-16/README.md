# Forest Guardian — independent secondary keeper for all seven M1 drive cassettes

**Review only. Initial candidate dated 2026-10-16; X-layout revision dated 2026-10-19.** D7 design original remains unchanged, 7 independently removable modules preserved (A-plan). The previous 14 rigid bayonet keys can lock axially, but could be undone by unintended **-Y 2.5mm** slide. This engineering increment adds **one headless M2×5mm set-screw candidate per axis**, placed beside the Y-return corridor. Removing only that axis's screw allows reverse Y then individual 55mm +Z service.

### What is physically modeled and calculated

- Immutable canonical 1,774 D7 solid original SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`. Its actual 65MB CAD file was read and checked in the local generation harness against the **previous** boss positions and **7 Ø2.4mm/24mm nominal rear-tool corridors**; that revision had zero original fixed-body projected intersections after removing the common BACK_WOOD/grille and allowing the still-uncompleted original fan relocation. The 2026-10-19 boss shift has NOT been rechecked against full D7. **CI does not redo the 1,774-solid D7 intersection**, and the future structural installation is still unqualified.
- Current seven-axis candidate places seven M2×5mm *headless* screws at `(x+23.15,y-1.1)`, upper surface Z139.35. Seven 3.3×3.95mm fixed bosses at X `(x+21.5)..(x+24.8)` (Z134–138) have reviewed 2.05mm bores; the bore is NOT a manufactured tap or a qualified thread. Bosses remain inside the nominal ±25mm reserved width. Screws cannot be claimed as captive or vibration-resistant.
- Locked bar occupies Y `+0.5..+4.5mm`. Installed screw occupies Y `-2.1..-0.1mm`. **0.6mm nominal clearance** when locked; trying to move the bar in -Y contacts the screw after 0.6mm, **before the 2.5mm travel needed to unlock**. Remove screw to unlock. This is *positive geometry*, not mechanical endurance proof.
- New screw bosses would obstruct the old cassettes **7/7 axes during full +Z55mm withdrawal**. The candidate creates a **2×4.25mm through-height window in the removable 44×35mm cassette wall**, and retains the original bar, two rigid guide keys and P3 intact.
- Full D7-derived generator, **714 position stage checks**, engineering load/tolerance and actual A3 1:1 PDF/DXF plus preview and a watertight single-boss STL in the companion ZIP. Github houses a compact native [7-axis OpenSCAD model](M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad), [screw and dimensions contract](design_contract.json) and [independent nominal 714-stage CI model](check_motion.py).

### Initial X-layout finding (2026-10-16; superseded by the 2026-10-19 candidate below)

The original 40mm *conservative* board envelope had only 0.3mm clearance to the through-height cassette notch and failed the assumed ±0.2mm two-part X tolerance screen by 0.1mm. That baseline geometry is superseded. No board dimension was reduced; the revised candidate retains the conservative 40mm envelope and shifts the fixed boss outward. The MTR-09-024 listing remains unmeasured and is not used as an acceptance substitute.

Other blockers: M2 tap/engagement material and prevailing torque, screw self-loosening, corner/shear, shell warp, heat creep, rearwood pocket Z140 gives just 0.65mm nominal headless clearance, fan relocation/airflow, electrical independent eFuse latch/PG/STOP bench proof.

**Progress invariants:** 16/48 narrowly scoped done, 8 working, 20 open, 4 hardware-wait; manufacturer gates **0/6**, software evidence **11/14**. U7 motor eFuse EN held LOW; no manufacturing, drilling, purchasing, energizing, flashing or merging `main`. PR stays Draft.

The hardware design remains **NOT ACCEPTED**. Next tasks are full-D7 collision recomputation for the shifted boss, Y/Z tolerance analysis, measurement of the selected module, plus anti-loosening and structural fixture tests.

## 2026-10-19 — conditional X-layout candidate (overall HOLD)

The initial X-layout above is superseded. Moving each fixed boss outward from X `20.5..24.0` to `21.5..24.8` and shifting the screw center from `22.25` to `23.15` retains a nominal **0.625mm** minimum bore-to-boss wall and stays within the ±25mm reserved width. A through-height cassette notch at X `20.6..22.5` gives 0.6mm nominal clearance to the conservative 40mm board envelope, or **0.2mm worst-case X clearance** under the stated ±0.2mm two-part tolerance assumption. The notch extends past the cassette wall edge at X22 by 0.5mm nominal (0.1mm worst-case under the same two-part screen). The screw still overlaps the 48mm lock bar by 1.85mm nominal and retains the nominal 0.6mm Y travel-to-contact stop before the 2.5mm unlock travel.

This is only an **X-direction parametric screen**. Y/Z notch fit, actual machining tolerances, shifted-boss clearance against all 1,774 D7 solids, material/fastener strength, screw loosening, fit to a measured driver PCB and physical 55mm service are not verified. The prior full-D7 zero-collision result applies only to the previous boss position and is not carried forward. Manufacturing remains blocked pending full-geometry and physical evidence.
