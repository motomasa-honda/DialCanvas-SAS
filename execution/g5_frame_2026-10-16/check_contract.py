#!/usr/bin/env python3
"""Native 13-box positive-joint & hold-contract check; GitHub does NOT have the original 65MB D7 model."""
import json,csv,math
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
assert d["source_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["source_solids"]==1774
v=d["parts"]; assert len(v)==13 and len({a["name"] for a in v})==13
assert len(d["links"])==12
m={x["name"]:x for x in v}
def overlap(a,b):
    return math.prod(max(0,min(a[hi],b[hi])-max(a[lo],b[lo]))
      for lo,hi in (("xlo","xhi"),("ylo","yhi"),("zlo","zhi")))
assert all(overlap(m[x],m[y])>0 for x,y in d["links"])
assert (m["FRONT_CROSSBAR"]["ylo"],m["FRONT_CROSSBAR"]["yhi"],m["FRONT_CROSSBAR"]["zlo"],m["FRONT_CROSSBAR"]["zhi"])==(12,18,127,136)
assert m["RIGHT_LOWER_WEB"]["zhi"]==123
assert m["RIGHT_LOWER_WEB"]["zlo"]==116
assert m["RIGHT_REAR_Z_RISER"]["zhi"]==136
assert d["battery_left_source_footprint"]["zlo"]==125 and d["battery_left_source_footprint"]["zhi"]==137
assert d["fan_current_position_hits"]==["FAN_GUARD_TARGET","FAN_MAX_BODY"]
assert d["source_collision_count_EXCLUDING_REMOVABLE_COVER_AND_FAN"]==0
assert d["other_axis_reserve_min_xy_mm"]>=1
assert d["reserve_worst_two_pm0_2_mm"]>=.6-1e-6
j=d["beam_ASSUMPTION_ONLY"];assert j["old_3x3_crossbar_lateral_deflection_mm"]>.85 and j["new_6x9_crossbar_lateral_deflection_mm"]<.04
assert j["right_web_and_joint_deflection"]=="NOT_EVALUATED"
q=d["g6_04_panel_feasibility"];assert (q["panel_source_count"],q["constant_sections"],q["variable_with_low_high_difference"])==(23,14,9)
assert not q["manufacturing_glue_approved"]
assert d["manufacturing_gates_closed"]==0 and d["software_review_evidence_passed"]==11
assert d["done_scope"]==19 and d["total_scope"]==48
assert d["motor_efuse_en"]=="LOW"
assert all(d[k] is False for k in ("fabricate","purchase","power","flash","merge_main"))
assert len(d["remaining_unqualified"])>=5
print("PASS: 13 positive-volume joined frame components and 12 joints; 3D-source file audit external")
print("PASS: stop false claim of G5 structural acceptance: known fan hits and no real welded/bolted/wood proof")
print("PASS: 19/48 scoped review milestones, 0/6 manufacturing, G6-04 14 constant/9 variable OPEN")
