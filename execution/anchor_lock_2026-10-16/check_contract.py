#!/usr/bin/env python3
"""Only verifies REVIEW MANIFEST's internal consistency. No native D7 CAD, no mechanical proof."""
import json
from pathlib import Path
d=json.loads((Path(__file__).parent/"contract.json").read_text())
assert d["source_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["solid_count"]==1774
anchors=d["four_anchors"]
assert len(anchors)==4
assert {(a["side"],a["center_y"]) for a in anchors}=={("L",30),("L",170),("R",30),("R",170)}
for a in anchors:
    x0,y0,z0,x1,y1,z1=a["foot_xyz_bbox"]
    assert (x1-x0,y1-y0,z1-z0)==(9,18,10)
    assert z0==126 and z1==136
    assert (x0,x1)==((12,21) if a["side"]=="L" else (249,258))
p=d["eight_blind_wood_axes"]
assert p["per_anchor"]==2 and p["nominal_blind_depth_mm"]==6
assert p["nominal_remain_wood_skin_mm"]==6 and p["source_fixed_d7_collision_count"]==0
assert p["drill_pilot_size"]=="NOT_APPROVED"
slots=d["separate_axis_slots"]
assert len(slots)==7 and sorted(x["axis"] for x in slots)==list(range(1,8))
m=d["rejected_m2_proposal"]
assert m["disposition"]=="REJECT_ALL_14_NOT_FABRICABLE_AS_DRAWN"
assert m["ear_seats"]==m["violations_5mm_reserved_envelope"]==m["violations_original_48x35_rearwood_relief"]==14
c=d["conditional_clip_proposal"]
assert c["retainer_count"]==14 and c["per_axis"]==2 and c["finger_width_x_mm"]==1.7
assert c["violations_5mm_reserved_envelope"]==0 and c["violations_original_48x35_rearwood_relief"]==0
assert c["spring_stress"]=="NOT_TESTED" and c["long_term_latch_strength"]=="NOT_TESTED"
a=d["acceptance"]
assert (a["scoped_complete"],a["scope_total"])==(16,48)
assert (a["manufacturer_gate_closed"],a["manufacturer_gate_total"])==(0,6)
assert (a["software_review_pass"],a["software_review_total"])==(11,14)
assert a["motor_eFuse_en"]=="LOW"
assert all(a[k] for k in ("no_fabrication","no_purchase","no_flash","no_main_merge"))
assert d["ci_claim_scope"].startswith("Static review")
print("PASS: 4 side cleats; 8 blind axes; 7 modules; 14 M2 failures are NOT falsely passed")
print("PASS: 14 in-band clip volume candidates only; spring/tolerance/HIL absent; manufacturing 0/6")
