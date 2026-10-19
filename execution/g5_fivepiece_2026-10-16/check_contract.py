#!/usr/bin/env python3
"""Static GitHub proof of G5 five-part decision integrity, NOT original D7/strength validation."""
import json
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
assert d["source_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["source_solids"]==1774
assert d["historical_members"]==13 and d["historical_positive_volume_overlap_joints"]==12
g=d["groups"]
assert {k:len(v) for k,v in g.items()}=={"CROSSBAR":1,"SIDE_LEFT":2,"SIDE_RIGHT":2,"G5_LEFT":3,"G5_RIGHT":5}
names=sum(g.values(),[])
assert len(names)==13 and len(set(names))==13
assert len(d["original_bounding_cuboids"])==13
assert [p["part"] for p in d["parts"]]==list(g)
assert d["grouped_3d_union_equal_original_13_across_all_z_intervals"]
assert d["new_independent_part_3d_positive_volume_intersection_count"]==0
assert d["source_d7_fixed_hits_excluding_removable_cover_and_fan"]==0
assert d["independent_stl_is_watertight"]==[True]*5
assert sum(x["volume_mm3"] for x in d["parts"])==d["steel_volume_mm3"]==19560
assert abs(d["steel_volume_mm3"]*d["steel_generic_density_g_cm3"]/1000-d["steel_mass_g"])<1e-6
assert abs(d["steel_volume_mm3"]*d["aluminium_density_g_cm3"]/1000-d["aluminium_mass_g"])<1e-6
v=d["internal_butt_interfaces"]
assert len(v)==4 and [x["area_mm2"] for x in v]==[9,9,18,18]
assert all(x["qualification"]=="NOT_TESTED" for x in v)
h=d["physical_fastener_candidate"]
assert abs(h["assumed_M2_head_diameter_mm"]+2*h["assumed_each_side_tolerance_mm"]-h["required_width_mm"])<1e-9
assert abs(h["required_width_mm"]-h["material_width_mm"]-h["missing_width_mm"])<1e-9
assert h["disposition"].startswith("REJECT")
assert d["additional_external_joints"]=={"g5_fixed_side_guides":2,"sidewood_anchor_cleats":4,"min_count":6,"qualified":0}
assert len(d["structural_hold"])>=6
r=d["manufacturer_release"]
assert (r["done_scope"],r["total"],r["working"],r["open"],r["hardware_wait"])==(19,48,6,19,4)
assert r["g3_04"]==r["g3_05"]=="WORKING"
assert r["manufacturing_closed"]==0 and r["software_evidence"]==11 and r["motor_efuse_en"]=="LOW"
assert all(not r[k] for k in ("cutting","power","flash","purchase","merge_main"))
assert d["verification_boundary"].startswith("Full original 1774 D7")
print("PASS STATIC: G5 old 13-overlap members -> 5 separate CAD parts, 4 butt interfaces still unqualified")
print("PASS HOLD: direct M2 headed screw rejected, other 6 external joints unqualified; steel 153.546g")
print("PASS SAFE LEDGER: 19/48 only, physical production 0/6, motor eFuse EN LOW")
