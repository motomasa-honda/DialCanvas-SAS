#!/usr/bin/env python3
"""GitHub rechecks D7 section audit metadata and 18/48 progress, not all 1774 CAD solids.
Full original SHA and 7 native drawings are independently verifiable in user handoff ZIP.
"""
import json
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
assert d["canonical_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["canonical_d7_solids"]==1774 and d["original_wood_operations"]==68
assert d["new_m1_overlay_candidates"]==15 and d["operation_register_entries"]==83
p=d["sections"];assert len(p)==7 and len({x["name"] for x in p})==7
assert sum(x["old_wood_ops"] for x in p)==68
assert sum(x["m1_overlays"] for x in p)==15
assert set(x["plane"] for x in p)=={"XY","XZ","YZ"}
assert {x["name"]:x["old_wood_ops"] for x in p}=={"P3":0,"TRAY":0,"BACK_WOOD":0,"WOOD_SIDE_LEFT":22,"WOOD_SIDE_RIGHT":22,"WOOD_BOTTOM":16,"WOOD_TOP":8}
assert d["delivery"]["a3_pdf"]==7 and d["delivery"]["editable_dxf"]==7 and d["delivery"]["joined_pdf_pages"]==7
g=d["g5_rearwood"]
assert g["decision"]=="REJECT_IDENTICAL_G1_TO_G7_POCKET_MACHINING"
assert abs(g["wood_present_percent"]+g["existing_void_percent"]-100)<1e-6
assert abs(g["wood_present_area_mm2"]+g["existing_void_area_mm2"]-1680)<0.001
assert g["wood_present_percent"]<25
assert d["eight_anchors"]["min_nominal_distance_to_original_68_operation_aabb_mm"]>=5
assert d["eight_anchors"]["screw_drill_diameter"]=="NOT_APPROVED"
s=d["acceptance"]
assert (s["done_scope"],s["working"],s["open"],s["hardware_wait"])==(18,6,20,4)
assert s["g6_02"]=="DONE_SCOPE" and s["g6_08"]=="OPEN"
assert s["manufacturing_gates_closed"]==0 and s["software_evidence_passed"]==11
assert d["authorization"]=={"motor_efuse_en":"LOW","cutting":False,"purchasing":False,"flashing":False,"merging_main":False}
assert d["github_validation_scope"].startswith("Review metadata")
print("PASS: seven source section evidence records; 68 original + 15 M1 overlays; G5 existing opening 81.346% explicitly REDLINE")
print("PASS: scoped work increased to 18/48, G6 manufacturing full-release OPEN, all motor power OFF")
print("LIMITATION: original D7 1,774-solid CAD source checks run in deliverable ZIP, NOT in this metadata CI")
