# G6-02 — seven authentic D7 interior A3 templates and M1 overlay (2026-10-16)

**Scoped engineering task G6-02 = DONE_SCOPE. NOT a manufacturing release.** Immutable 1,774-solid D7 `assembly.json` SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f` was read completely and rehashed in the **local source regeneration harness** shipped with this deliverable.

The original source-derived native planar contours of P3, TRAY, BACK_WOOD, WOOD_SIDE_LEFT, WOOD_SIDE_RIGHT, WOOD_BOTTOM and WOOD_TOP were selected at Z96, Z81, Z140.8, X6, X264, Y6, and Y199 respectively. Real output: **seven distinct A3 (420x297mm) 1:1 PDFs and seven editable DXFs** (separate `D7_SOURCE_CONTOUR`, `D7_SOURCE_OPERATIONS`, `M1_REVIEW_UNAPPROVED` layers), plus one complete **7-page A3 PDF book** and a source-sliced exact polygon geometry JSON allowing independent package inspection.

Authentic `wood-receiver-design.json` with **68 unchanged legacy woodworking operations** (22 LEFT, 22 RIGHT, 16 BOTTOM, 8 TOP) is preserved without silently editing original hole diameters. 8 proposed 6mm-blind sidewood fastener envelopes and 7 proposed 48x35x3mm BACK_WOOD relief *envelopes* are overlaid and audited, yielding 83 review trace rows. These 15 candidate marks **do not mean 15 approved cuts**; fastener pilot diameters are unqualified. Eight anchor-to-existing-machining 3D AABB checks show at least **5.014mm** nominal distance (not validated wood splitting edge distances, cutting tools, or torque).

## Critical new original-CAD defect identified

The **G5** 48×35mm rectangular backwood relief is already **81.346% vacant/open** at canonical BACK_WOOD Z140.8. Of total 1,680mm² candidate area, only **313.380mm² original source wood** exists; **1,366.620mm² is pre-existing opening**. It is therefore incorrect to treat G5 like six other standard recessed wood pockets. An extra `G5_BACKWOOD_SOURCE_MATERIAL_ONLY_REVIEW.dxf` isolates original wood remaining vs the existing opening. **Do not machine any of the seven reliefs until support, edge ligament, module and back-cover strength are rechecked.** Seven proposed rectangles do not overlap each other in the nominal XY comparison.

## Honest completion contract

- **G6-02**: YES, source-accurate seven-panel and M1 overlay review templates generated, A3 pages read back at 420×297mm, native editable DXFs reopened, source SHA and all 68+15 rows validated in independent source-driven Python. This is the *limited review drawing preparation task*.
- **G6-08**: still **OPEN**: front/back of all physical panels, sideband thickness, machining tool paths, adhesive tabs, 1:1 physical print test, assembly instructions, validation of G5 cutout, seven-axis servicing.
- **G3-05**: still **WORKING**: actual wood materials/holding fasteners, strength, tool radii, physical assembly/thermal still not approved.
- **G1 electrical safety**: EN remains **LOW**, independent trip latch and M1 KiCad native ERC/DRC unclosed. No purchase, cutting, power, flashing, main merge.

**Progress:** **18/48 DONE_SCOPE**, 6 WORKING, 20 OPEN, 4 HARDWARE_WAIT. **Manufacturing 0/6** and software review **11/14**.

## Reproducible delivery / limits of GitHub CI

Downloadable `Forest_Guardian_G6-02_A3_7Panels_18of48_2026-10-16.zip`: 1,023,062 bytes, SHA256 **`cb2fc157d257bc7009b1c554c89c4b53cb5c14e4b90118f91c8114c995dd5a36`**, 31 SHA-manifested files plus manifest. Contains original wood source copy, `D7_SEVEN_PANEL_EXACT_SECTION_PROVENANCE.json` with the **exact seven geometries extracted from the original CAD**, full-source generator and original SHA verifier, separate self-contained distributed-package verifier, PDFs, DXFs, 83-row trace CSV, eight anchor/7 pocket checks, six-sheet companion spreadsheet. Original 65MB full D7 CAD is already in historical baseline ZIP and is NOT redundantly duplicated in this small increment ZIP.

Complete-history `Forest_Guardian_Integrated_Handoff_18of48_2026-10-16.zip` 116,582,217 bytes SHA256 **`f500c5bf3a5f5456056cc23ff7079e22032acbae0bccebe2bba63bec825b54d9`** preserves prior complete 17/48 archive byte-for-byte and nests new artifact unchanged; both passed ZIP CRC and SHA manifest tests.

GitHub has this exact [scope contract](design_contract.json) and [metadata integrity test](check_contract.py), with a dedicated CI workflow. **GitHub CI does NOT regenerate the full 1,774-solid source or PDF/DXF because those source/assets are in the separately verified ZIP**; it only confirms metadata, critical G5 warning and correct task states.
