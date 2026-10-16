# D7 — seven-axis positive bayonet *kinematic* engineering increment

**Version:** 2026-10-16, REVIEW ONLY. All seven motor eFuse feeds remain inhibited. Manufacturer/process verification incomplete.

## Actual engineering progress

Unlike the previous 14 thin *spring clip volume placeholders*, this deliverable models an **engaging, reversibly removable rigid key AND its complementary stationary guide undercut**. Each axis uses two mirrored rails. The key is inserted from +Z via a local top-entry slot, lowered to Z135.0–135.5 and shifted +2.5mm along Y, so it seats below the 0.95mm fixed guide lip. Move the bar -2.5mm Y before reverse +Z removal. Original 5mm perimeter reservation and 48×35 backwood pocket remain respected **nominally**.

- 7 individually removable bars, **14 matched real key/notch pairs**.
- Actual manufacturer/D7 original geometry check was run in the artifact-generation runtime on all **1,774 solids**, SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`. Zero projected hits after explicitly removing the common BACK_WOOD/grille and relocating the original fan hardware, including local boss reinforcement.
- **14/14 actual reviewed kinematics PASS** at nominal dimensions: vertical insert, Y +2.5mm slide, +Z0.25mm positive capture, reverse release/extract. 14 × (71 insertion + 51 sliding + 51 reversing + 71 extraction) = **3,416 collision-free sampled states**, plus 14 deliberately blocked pull tests. See [`check_motion.py`](check_motion.py), which does recompute collision geometry from input dimensions (not merely inspect a string), and rejects 42 deliberately broken entry/window/lip cases.
- Nominal rail/key X overlap **0.60mm**, remaining boss width **1.15mm**, upper flange 0.95mm, slide minimum y-offset underlip 1.3mm, Z play0.2mm. The real source-based CAD+STL/DXF generation scripts and three-section A4 PDF are in the downloadable delta ZIP.

## Non-negotiable release blockers

1. **There is NO secondary keeper preventing unintended reverse Y sliding.** A vibration-induced -2.5mm translation could release the positive keys, enabling board withdrawal. **This mechanism is NOT safe or complete** until a true separate captive anti-slide device is designed with positive retention, then tested.
2. **Unknown real material, tolerance and shear strength.** ±0.2mm per part leaves only 0.2mm nominal hook overlap; at *assumed* 100g and 10g, one single key could face nominal 49MPa stress demand (not a failure prediction or certified test). Need vendor mechanical data, manufacturing process, measured masses, creep and temperature tests.
3. No real connector/pin/height measurement for MTR-09-024, no physical tool and 55mm harness trial; rearwood pocket/side cleat strength & original fan relocation unqualified.
4. All electrical stop/PG/independent supervisor gates remain OPEN, manufacturing **0/6**, SW evidence **11/14**, scoped completed tasks **16/48**. No purchases, machining, PCB fab, motor power, board flashing or `main` merge.

The Github [`design_contract.json`](design_contract.json) and [`check_motion.py`](check_motion.py) create reproducible **actual nominal kinematic verification in CI**. Source original **D7 collision projection was not rerun on GitHub**, since its 65MB CAD file is in the immutable handoff ZIP, not this branch. The full CAD is therefore in the companion local/source ZIP only. [Small native G1 test CAD](M1_G1_positive_key_unit.scad) is versioned in GitHub; full 7-axis model is included in the delta artifact. Keep PR #2 Draft.

**Tangible delta ZIP**: `Forest_Guardian_Seven_Axis_Bayonet_Engineering_2026-10-16.zip`, SHA256 `04f03536a38a58e73e8760b2124379ca5c5016e5002acc3e8d35d82095d7c4f2`. Native OpenSCAD full 7-axis and unit fixture, editable 1:1 DXF, A3 PDF/SVG, enlarged A4 key engagement drawing, watertight reference STL, geometry/kinematic/tolerance/anchor CSV, regenerate/verification Python, screenshots and hash manifest.

**Immediate next mechanical design step:** secondary captive anti-backslide stop that remains wholly within fixed 5mm reservation and rearwood pocket, with measurable release force and repairability for one axis without touching six others. In parallel qualify sidewood blind screw pullout, cooling/vent and independent electrical safety.

**Integrity update:** compact ZIP 24 files, 123,931 bytes, all 23 content files verified by included `VERIFY.py` SHA manifest (plus the manifest file itself). Complete-history archive `Forest_Guardian_Integrated_With_Bayonet_2026-10-16.zip`, 115,310,580 bytes, SHA256 `6126a4a35ea08dcdf312881cb0930f915c844fac88606dfa80b23a4582ed533b`. Both local ZIP archive integrity checks PASS.
