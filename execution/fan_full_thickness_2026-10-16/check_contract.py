#!/usr/bin/env python3
"""Enforce previously geometry-only fan spots remain NO-CUT ventilation REJECTED."""
import json, math
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
assert d["source_original_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["source_original_solid_count"]==1774
w=d["wood_z_layers"]
assert len(w)==9 and w[0][0]==137 and w[-1][1]==145
assert all(math.isclose(a[1],b[0]) for a,b in zip(w,w[1:]))
assert math.isclose(d["fan_outlet_area_mm2"],math.pi*(d["fan_outlet_diameter_mm"]/2)**2,abs_tol=.001)
a=d["candidate_data"]
assert len(a)==8 and len({(x["cx"],x["cy"]) for x in a})==8
assert [(x["cx"],x["cy"]) for x in a[:3]]==[(95,90),(95,95),(95,100)]
assert [round(x["through_mm2"],3) for x in a[:3]]==[1.129,3.006,1.129]
assert all(x["through_percent"]<.5 for x in a) and all(x["through_mm2"]==0 for x in a[3:])
h=d["mounting"]
assert h["manufacturer_holes"]==3 and h["max_three_hole_centers_on_original_outer_wood"]==2
assert h["fully_native_fastened_candidate"] is False
c=d["current_mA"]
assert c["V1_rated"]>c["branch_limit"]==100
assert c["V2_rated"]==80 and c["V2_individual_max_steady"]==92
assert c["V3_rated"]==45 and c["V3_individual_max_steady"]==54
assert "not retrieved from the SUNON primary domain" in d["individual_source_class"]
assert "not a guaranteed system bound" in c["V2_individual_max_source_class"]
assert "not a guaranteed system bound" in c["V3_individual_max_source_class"]
assert c["starting_peak_test"]==c["motor_stall_test"]==c["actual_closed_case_thermal"]=="NOT_DONE"
e=d["engineering"]
assert e["full_thickness_vent"]=="REJECT_ALL_8_PRIOR_SITES_AS_NO_CUT_EXHAUST"
assert (e["scoped_done"],e["scope_total"],e["manufacture_closed"],e["software_evidence"])==(19,48,0,11)
assert e["g3_06"]=="OPEN" and e["efuse_en"]=="LOW"
assert not any(e[k] for k in ("purchasing","cutting","power","flashing","main_merge"))
old=json.loads((Path(__file__).parent.parent/"g5_jig_g604_2026-10-16"/"design_contract.json").read_text())
assert old["fan_g3_06_source_screen"]["backwood_no_cut_vent"]=="REJECTED_ALL_THREE"
print("PASS: three D7 body-clear positions are NO-CUT airflow FAIL; all 8 candidate through apertures <0.5%")
print("PASS: manufacturer catalog ratings separated from distributor-hosted maximum-current listings")
print("PASS: G3-06 OPEN, manufacture0/6, 19/48, EN LOW; original 9-shape recompute in artifact ZIP")
