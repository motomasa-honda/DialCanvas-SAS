#!/usr/bin/env python3
"""G4-03 passive candidate contract; no electrical or release certification."""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXECUTION = ROOT.parent
with (ROOT / "passive_bom.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

expected = {
    "R50": ("47 kOhm", "ERJ3EKF4702V", "0.1 W; +/-1%; +/-100 ppm/K", "47k 1% CANDIDATE"),
    "R51": ("12 kOhm", "ERJ3EKF1202V", "0.1 W; +/-1%; +/-100 ppm/K", "12k 1% CANDIDATE"),
    "R52": ("2.21 kOhm", "ERJ3EKF2211V", "0.1 W; +/-1%; +/-100 ppm/K", "2.21k 1% CANDIDATE"),
    "C14": ("3.3 nF", "GRM1885C1H332JA01D", "50 Vdc; +/-5%; C0G/NP0", "3.3nF CANDIDATE"),
    "C15": ("2.2 nF", "GRM1885C1H222JA01D", "50 Vdc; +/-5%; C0G/NP0", "2.2nF CANDIDATE"),
}
assert len(rows) == 5 and {r["ref"] for r in rows} == set(expected)
for row in rows:
    value, mpn, rating, schematic_value = expected[row["ref"]]
    assert row["nominal_value"] == value
    assert row["manufacturer_part_number"] == mpn
    assert row["rating_or_tolerance"] == rating
    assert row["package"] == "0603 (1608 metric)"
    assert row["status"] == "selected candidate"
    assert row["source_url"].startswith("https://")
    host = "industrial.panasonic.com" if row["ref"].startswith("R") else "murata.com"
    assert host in row["source_url"]

schematic = (EXECUTION / "g1_85_efuse_analog" / "forest_guardian_g1_85_analog_review.kicad_sch").read_text(encoding="utf-8")
for ref, (_, _, _, schematic_value) in expected.items():
    assert f'(property "Reference" "{ref}"' in schematic
    start = schematic.index(f'(property "Reference" "{ref}"')
    block_start = schematic.rfind("  (symbol ", 0, start)
    block_end = schematic.index("\n  )", start)
    block = schematic[block_start:block_end]
    assert f'(property "Value" "{schematic_value}"' in block
    assert '(property "Footprint" ""' in block
    assert "(in_bom no) (on_board no)" in block

# TPS25947 Rev C typical equations. Bounds include only published VOV limits
# and resistor tolerance; they are not full system tolerances or safety limits.
vmin, vtyp, vmax = 1.183, 1.200, 1.223
rtop, rbot, tol = 47000.0, 12000.0, 0.01
nominal_ovlo = vtyp * (rtop + rbot) / rbot
worst_low = vmin * (rtop * (1 - tol) + rbot * (1 + tol)) / (rbot * (1 + tol))
worst_high = vmax * (rtop * (1 + tol) + rbot * (1 - tol)) / (rbot * (1 - tol))
assert math.isclose(nominal_ovlo, 5.9, abs_tol=1e-12)
assert 5.72 < worst_low < 5.73 and 6.10 < worst_high < 6.12
ilm_typical_a = 3334 / 2210
assert math.isclose(ilm_typical_a, 1.5085972851, rel_tol=1e-9)
assert math.isclose(2000 / 3300, 0.6060606061, rel_tol=1e-9)
assert math.isclose(5 / (2000 / 3300), 8.25, abs_tol=0.01)
assert math.isclose(1.51 * 2.2 / 1.8, 1.8455555556, rel_tol=1e-9)

# Release interlocks are invariants, not claims inferred from this selection.
contract = (EXECUTION / "g1_85_efuse_analog" / "design_contract.json").read_text(encoding="utf-8")
assert '"enable_status": "GROUNDED_10K_NO_CHANGE"' in contract
assert '"manufacturer_erc_pass": false' in contract
assert '"pcb_drc": false' in contract and '"motor_hil": false' in contract
assert "(in_bom no) (on_board no)" in schematic
print("PASS: 5 exact manufacturer candidates match G1-85 values, package/rating, sources and nominal equations")
print(f"SCREEN only: OVLO nominal {nominal_ovlo:.3f} V; resistor+VOV static range {worst_low:.3f}..{worst_high:.3f} V; ILM typical {ilm_typical_a:.3f} A")
print("HOLD: eFuse EN remains grounded; no BOM/footprint/PWB/ERC/DRC, current-minimum guarantee, thermal or HIL approval")
