#!/usr/bin/env python3
"""80-ID/160-face manufacturing-HOLD review contract; external PDF/DXF in verified user ZIP."""
import json,csv
from pathlib import Path
from collections import Counter
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
assert d["task"]=="G6-03" and d["status"]=="DONE_SCOPE_DRAWING_SOURCE_ONLY"
assert d["original_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["original_d7_solids"]==1774
groups=d["component_groups"]
assert {k:len(v) for k,v in groups.items()}=={"core":7,"bezel":8,"cover":8,"gear":7,"ledBoards":4,"leds":20,"sensor":14,"lightWood":12}
ids=sum(groups.values(),[])
assert len(ids)==80 and len(set(ids))==80
assert d["source_named_physical_component_count"]==80 and d["source_face_count"]==160
assert d["pdf_A3_count"]==d["editable_dxf_count"]==d["joined_A3_book_pages"]==160
assert d["g5"]["z140_8_existing_opening_pct"]>81 and d["g5"]["z144_99_wood_mm2"]==0
assert d["g5"]["decision"]=="NO_G5_BACKWOOD_CUT"
assert d["g5"]["physical_strength"]=="NOT_TESTED"
assert d["secondary_keeper_V2"]["previous_worst_clearance_mm"]<0
assert d["secondary_keeper_V2"]["new_worst_clearance_mm"]>.5
assert d["secondary_keeper_V2"]["thread_boss_left_meat_mm"]<.6
assert d["secondary_keeper_V2"]["retention_strength"]=="NOT_TESTED"
r=d["release"]
assert (r["scoped_done"],r["scoped_total"],r["working"],r["open"],r["hardware_wait"])==(19,48,6,19,4)
assert r["manufacturer_gates_closed"]==0 and r["software_evidence_passed"]==11
assert r["motor_power"]=="EFUSE_EN_HELD_LOW"
assert not any(r[k] for k in ("woodcutting","buying","pcb_fabrication","hardware_flash","merge_main"))
with (Path(__file__).resolve().parent.parent/"tasks.csv").open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
assert len(rows)==48
assert next(x for x in rows if x["ID"]=="G6-03")["Status"]=="DONE_SCOPE"
assert next(x for x in rows if x["ID"]=="G6-08")["Status"]=="OPEN"
assert len([x for x in rows if x["Status"]=="DONE_SCOPE"])>=19
print("PASS: 80 named D7 source objects, 160 independently drawn low/high native face records; project 19/48")
print("PASS: original G5 full void on last face, proposed 3x6 frame beam and M2 40mm +0.55 geometric review")
print("LIMITATION: actual PDF/DXF and full 1,774 D7 CAD recomputation are verified in delivered ZIP, NOT this CI")
