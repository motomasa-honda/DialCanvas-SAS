# G3-06 external fan relocation candidate — 2026-10-19

**Geometry candidate only. NOT FOR CUTTING, PURCHASE, OR POWER.** This work replaces the previous unvented candidate position with a new rearwood exhaust-port site that is checked against the canonical D7 source and all nine original BACK_WOOD slices.

## Candidate architecture

Place a 30×30×10mm SUNON MF30100V3-1000U-A99-class axial fan on the exterior rear face, centered at `(220,40)` in D7 XY. A 45×45mm adapter plate envelope sits on the outside of BACK_WOOD. A new Ø29.7mm port is proposed through the original Z137..145mm wood strata. Fan inlet faces inward through the port; discharge faces rearward. The support center pattern is ±19mm in X/Y; hole diameter and fasteners are not yet assigned. The plate and SCAD are layout envelopes, not detailed part drawings.

The port is nominally 0.4mm larger in diameter than SUNON's catalog outlet Ø29.3mm. The full-source screen finds the aperture circle inside all nine wood layers, minimum center-to-existing-material-boundary distance 19.3318mm (4.4818mm remaining to the proposed aperture radius), and all four plate support centers within the wood. The fan body, adapter envelope, and square aperture corridor have no fixed nonwood D7 intersections. The corridor avoids the modeled REAR_GRILLE at this location. The adapter envelope remains clear of all seven conditional 50×41mm module-service reservations.

This is a new through-hole machining proposal and needs wood species/grain/edge-breakout review, actual fastener qualification, an adapter/gasket/guard detailed drawing, rear appearance review and intake-air design. No airflow inference is made from the port area.

## Part screening and electrical hold

SUNON's official 2026 DC fan catalog, p.22, lists the MF30100V3-1000U-A99 at 5V, 45mA rated, 2.5CFM free-air, 0.07in-H₂O static pressure, 30×30×10mm; it shows Ø29.3mm outlet, three Ø3.2±0.3 mounting holes on 24±0.3mm pitch. Source: <https://www.sunon.com/jp/MANAGE/Docs/PRODUCT/325/504/DC%20Fan_20260210%28255-E%29.pdf>. The individual stated maximum 54mA previously cited in the project comes from a distributor-hosted detailed PDF, not primary SUNON material; it is not a startup/stall guarantee. The 100mA branch budget, all other loads, startup and stall remain unverified. V3 is only the lowest-rated-current geometry/power screen; no SKU is selected, bought or enabled.

## Reproduce

```sh
python3 execution/fan_relocation_2026-10-19/audit_candidate.py /path/to/CANONICAL_D7/cad/assembly.json --output execution/fan_relocation_2026-10-19/evidence/candidate_source_audit.json
python3 -m unittest execution/fan_relocation_2026-10-19/test_candidate.py
openscad -o /tmp/fan_relocation.csg execution/fan_relocation_2026-10-19/FAN_RELOCATION_CANDIDATE.scad
```

The source must hash to `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f` and contain 1,774 solids. Remove all original `FAN_*` source volumes in the relocation scenario. Full validation still excludes hardware not in original D7 and does not establish thermal, acoustic, electrical or structural acceptance. `G3-06` remains OPEN, `G2-07` OPEN, `G3-04` WORKING, release gates 0/6 and motor eFuse EN LOW.
