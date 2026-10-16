#!/usr/bin/env python3
"""Actual independent nominal seat fit, load arithmetic and source-tag integrity check.
No original 65MB CAD in repo; full 1774 source recompute is in user ZIP.
"""
import json,itertools,math
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
prev=json.loads((Path(__file__).parent.parent/"g5_fivepiece_2026-10-16"/"design_contract.json").read_text())
assert d["original_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["source_3d_solids"]==1774 and prev["source_solids"]==1774
parts=prev["groups"]
# Prior CAD register is a 7-item positional array [name,x0,y0,z0,x1,y1,z1], not a dictionary.
keys=("name","xlo","ylo","zlo","xhi","yhi","zhi")
boxes={row[0]:dict(zip(keys,row)) for row in prev["original_bounding_cuboids"]}
assert len(boxes)==13 and all(len(row)==7 for row in prev["original_bounding_cuboids"])
fix=d["fixture"];assert fix["base_mm"]==[270,190,8] and fix["global_min_z_reference_mm"]==116
seats=fix["eight_source_contact_datums"];assert len(seats)==8 and len({x["datum"] for x in seats})==8
for s in seats:
    assert s["part"] in parts
    x,y,z=s["x_mm"],s["y_mm"],s["z_mm"]
    assert 4<x<266 and 4<y<186
    assert math.isclose(s["wood_jig_spacer_mm"],z-116,abs_tol=1e-9)
    assert any(boxes[p]["xlo"]<x<boxes[p]["xhi"]
            and boxes[p]["ylo"]<y<boxes[p]["yhi"]
            and math.isclose(boxes[p]["zlo"],z)
            for p in parts[s["part"]]),s
assert sorted(x["wood_jig_spacer_mm"] for x in seats)==[0,0,11,11,11,14,14,14]
assert fix["accuracy_qualified"] is False and fix["joining_qualified"] is False
frame=d["frame"];assert frame["internal_joint_faces_mm2"]==[9,9,18,18]
assert frame["external_g5_guide_joints"]==2 and frame["external_sidewood_anchor_joints"]==4
assert frame["m2_head_direct_3mm_strip"]=="REJECTED"
m=d["load_matrix"];cases=list(itertools.product(m["payload_kg"],m["inertial_acceleration_g"],m["hypothetical_shared_joint_count"]))
assert len(cases)==m["rows_expected"]==24
for payload,g,n in cases:
    total=(payload+frame["assumed_steel_frame_mass_g"]/1000)*m["global_gravity_m_s2"]*g
    assert total>0 and 0<total/n/18<total/n/9
assert m["joint_strength"]=="NOT_COMPUTABLE_FROM_F_MEAN"
p=d["g6_04"]
assert p["all_panels"]==23 and len(p["constant_panels"])==14 and len(p["stepped_panels"])==9
assert len(set(p["constant_panels"]+p["stepped_panels"]))==23
assert p["bezel_source_z1_xy_contact_mm2"]=={"BOTTOM":810,"LEFT":567,"RIGHT":567,"TOP":810}
assert p["product_glue"]=="NOT_APPROVED" and p["task_status"]=="OPEN"
s=d["safety"]
assert (s["manufacture_gate"],s["scoped_done"],s["scoped_total"],s["software_review_pass"])==(0,19,48,11)
assert s["g3_04"]==s["g3_05"]=="WORKING" and s["g6_04"]=="OPEN"
assert s["electric_motor_efuse_en"]=="LOW"
assert all(s[k] for k in ["no_cut","no_purchase","no_power","no_flash","no_main_merge"])
print("PASS 8 source-member fit datum coordinates; 24 non-certifying load cases and 4 unqualified butt faces")
print("PASS 23 named D7 panels = 14 constant + 9 stepped, 4 source face contact areas")
print("HOLD manufacturing 0/6, scoped review 19/48, glue and weld strength NOT QUALIFIED")
