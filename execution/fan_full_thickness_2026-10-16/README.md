# G3-06 source correction: 9-layer fan outlet obstructions (2026-10-16)

Legacy 30mm fan candidates at (95,90), (95,95), (95,100) were ONLY nominal 3mm body-clear checks. They are NOT exhaust installation designs. A new actual original-D7 audit (1774 solids, SHA256 20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f) re-read all 9 contiguous BACK_WOOD XY material slices from Z137 to 145mm.

The manufacturer's actual outlet diameter is 29.3mm (nominal 674.256mm²). Source nine-layer through-clear projections are **1.129 / 3.006 / 1.129 mm²**, or **0.167 / 0.446 / 0.167%**. Five other prior body-clear sites have 0mm². All eight original no-cut locations are **REJECTED AS UNMODIFIED-BACKWOOD EXHAUST**, not a ban on redesigned side-grille or certified new backwood vent.

Official Sunon 2026 30x30x10 catalog p22: https://www.sunon.com/jp/MANAGE/Docs/PRODUCT/325/504/DC%20Fan_20260210%28255-E%29.pdf ; 3 holes Ø3.2±0.3mm, 24±0.3mm hole pitch and case ±0.5mm. At most 2 of the 3 mounting points sit on outer original wood for any 3-of-4 candidate orientation, before fastener edge/grain checks.

SUNON's official 2026 catalogue lists V1 at 120mA, V2 at 80mA / 4.7CFM, and V3 at 45mA / 2.5CFM under catalogue test conditions; V1 exceeds the existing 100mA branch rating. The V2 92mA and V3 54mA individual maximum-current figures come from distributor-hosted manufacturer-format PDFs, not SUNON's primary domain. They are recorded as secondary-source values only, not guaranteed current limits. None of these catalogue values establishes startup/inrush, stall current, the complete branch load, or closed-case thermal performance. V3 remains a screening candidate only; no part selected or purchased. See source links and source-class qualifiers in `design_contract.json`.

**Source verification is not a mere JSON assertion:** delivered artifact ZIP contains nine exact full-original wood polygons (compressed), 72 independently recalculated layer intersections, 8 true through-area samples, 12 3-hole permutations and standalone Shapely verifier. The full 65MB source SHA is validated in the ZIP original-source rebuilding script; the GH CI does not rerun it.

ZIP: Forest_Guardian_G3-06_SUNON_FullThickness_Fan_Review_2026-10-16.zip, 524076 bytes, SHA256 73fc73fc528e95d175fc9a85f6c82cee7ea946d8206379008ebcdf78072ba852. Native 3-page A3 PDF and extracted polygon subset included.

G3-06 stays OPEN. 19/48 work done, manufacturer0/6, software11/14, motor eFuse EN LOW. No ordering, cutting, fan power, motor power, flashing or main merge.
