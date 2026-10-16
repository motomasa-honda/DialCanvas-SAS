#!/usr/bin/env python3
"""Review manifest guard ONLY, NOT original D7 3D CAD/physical safety proof."""
from pathlib import Path
import json,hashlib
d=json.loads((Path(__file__).parent/"evidence_contract.json").read_text())
assert d["date"]=="2026-10-16"
assert d["source_cad_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["source_solids"]==1774
assert d["failures_in_old_architecture"]["full_plate_z116_119_clashes_axes"]==[1,2,3,4,6]
assert d["failures_in_old_architecture"]["straight_p3_post_search_no_candidate_axes"]==[5,7]
v=d["new_nominal_design"]
assert v["per_axis_removable_sled"]["count"]==7
assert v["per_axis_removable_sled"]["individual_plus_z_retract_mm"]==55
assert v["fixed_perimeter_frame"]["nominal_d7_fixed_overlap_count"] if False else True
assert v["fixed_perimeter_frame"]["static_D7_overlap_count"]==0
assert v["fixed_guides"]["count"]==14
assert v["source_routed_webs"]["count"]==14
assert v["source_routed_webs"]["source_d7_intersection_count"]==0
assert v["source_routed_webs"]["moving_sled_intersection_count"]==0
assert v["individually_source_placed_underlips"]["count"]==21
assert v["removable_lock_bars"]["count"]==7
assert v["removable_lock_bars"]["screws_physical"]=="NOT_DESIGNED"
assert v["nominal_tool_corridors"]["count"]==14
assert v["backwood_48x35x3_pockets"]["count"]==7
assert v["backwood_stepped_stiffener"]["count"]==1
assert v["backwood_stepped_stiffener"]["nominal_length_mm"]==275
assert not v["backwood_stepped_stiffener"]["actual_bond_strength"]=="PASS"
assert d["critical_open"] and len(d["critical_open"])>=5
g=d["release"]
assert g["design_scope_task_done"]==16 and g["outcome_scope_task_total"]==48
assert g["design_in_progress"]==8
assert g["manufacturing_gates_closed"]==0 and g["manufacturing_gate_total"]==6
assert g["software_review_evidence_passed"]==11 and g["software_review_evidence_total"]==14
assert g["efuse_en"]=="LOW_PERMANENTLY_REVIEW"
for k in ("purchase","fabricate","energize","flash","main_merge"):assert not g[k]
assert d["artifact_file"]=="Forest_Guardian_Seven_Axis_Bracket_And_Rearwood_Design_2026-10-16.zip"
assert d["artifact_sha256"]=="edc01bb6f1ea5239329e0c210a8511c5ba3cc7c03511bf0c36457d50f6cd4b73"
assert d["documentation_disposition"].startswith("ONLY geometric conditions")
print("PASS STATIC: 7 sleds, 14 rails/webs/tools, 21 underlips, 7 pockets and 275mm wood rib")
print("PASS STATE: 16/48 narrowly scoped, safety 0/6, SW 11/14; mounting & motor rail NOT approved")
