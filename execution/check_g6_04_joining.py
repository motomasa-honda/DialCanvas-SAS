#!/usr/bin/env python3
"""G6-04 product joining completeness gate. No CAD/hardware claims."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "g6_04_panel_join_register_2026-10-18.csv"
REQUIRED = {
    "panel_id", "source_section_class", "source_geometry_evidence",
    "thickness_mm", "side_band_mm", "glue_tab_mm", "adhesion_target",
    "product_joint_qualified", "release_state",
}
INVALID = {"", "UNRESOLVED", "NOT_APPROVED", "TBD", "UNKNOWN", "N/A"}
with REGISTER.open(newline="", encoding="utf-8") as stream:
    reader = csv.DictReader(stream)
    assert REQUIRED.issubset(reader.fieldnames or []), "Missing joining fields"
    rows = list(reader)
assert len(rows) == 23, f"Expected 23 D7 panels, got {len(rows)}"
assert len({r["panel_id"] for r in rows}) == 23, "Duplicate panel identifier"
assert sum(r["source_section_class"] == "CONSTANT_SECTION" for r in rows) == 14
assert sum(r["source_section_class"] == "STEPPED_SECTION" for r in rows) == 9
missing = []
for r in rows:
    for key in ("thickness_mm", "side_band_mm", "glue_tab_mm", "adhesion_target"):
        if r[key].strip().upper() in INVALID:
            missing.append((r["panel_id"], key))
    if r["product_joint_qualified"].lower() != "true" or r["release_state"] != "ACCEPTED":
        missing.append((r["panel_id"], "qualification"))
if missing:
    print(f"G6-04 HOLD: {len(missing)} unresolved field/qualification checks across 23 panels")
    for panel, field in missing:
        print(f"  {panel}: {field}")
    raise SystemExit(2)
print("G6-04 register structurally complete; separate source/physical evidence review still required")
