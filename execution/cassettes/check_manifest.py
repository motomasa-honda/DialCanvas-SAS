#!/usr/bin/env python3
"""Audits MATERIALIZED review solution; original D7 1774-solid recompute is separate and retained in handoff ZIP.
PASS != native CAD re-run, 55mm real harness or physical service acceptance.
"""
import json,math
from pathlib import Path
d=json.loads((Path(__file__).parent/"seven_axis_conditional_layout.json").read_text())
assert d["status"]=="CONDITIONAL_GEOMETRY_REVIEW_ONLY"
assert d["source_d7_assembly_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["source_solids"]==1774
assert d["grid_mm"]==5 and d["pcb_xy_mm"]==[40,31]
assert d["combined_reserved_xy_mm"]==[50,41]
assert d["per_side_reserved_xy_mm"]==5
assert d["axial_retraction_mm"]==55
assert d["panel_pocket_depth_mm_candidate_only"]==3
assert d["nominal_interference_with_rear_wood_mm"]==1
s=d["slots"]
assert len(s)==7 and sorted(x["axis"] for x in s)==list(range(1,8))
assert d["original_fan_60mm_case"]["candidate_grid_positions"]==74
assert not d["original_fan_60mm_case"]["seven_modules_feasible_on_grid"]
assert d["fan_relocation_case"]["candidate_grid_positions"]==321
assert d["fan_relocation_case"]["seven_modules_feasible_on_grid"]
assert d["fan_relocation_case"]["fixed_d7_swept_collision_count"]==0
for i,a in enumerate(s):
    assert a["swept_55mm_fixed_collision_count_after_explicit_removals"]==0
    x,y=a["x"],a["y"]
    assert x%5==y%5==0
    edge=min(x-25-13,257-(x+25),y-20.5-13,192-(y+20.5))
    assert abs(edge-a["minimum_outer_wood_margin_mm"])<1e-7 and edge>=5
    for b in s[i+1:]:
        # Envelope touching is prohibited: 10mm nominal board-board separation needed.
        assert abs(x-b["x"])>50 or abs(y-b["y"])>41
assert d["cooling_same_layer_nominal_free_candidate_centers"]=={"60.5x60.5":0,"40x40":0,"30x30":5,"25x25":29}
assert d["example_30x30_fan_center_xy"]==[95,90]
assert d["wood_fill_at_z137_5_pct"]==98.9
assert "original 60mm fan and mounting hardware relocated (alternative not yet thermally qualified)" in d["allowable_service_precondition"]
a=d["authorization"]
assert a["manufacturing_gates_closed"]==0 and a["sw_evidence_passed"]==11
assert a["motor_eFuse_en"]=="HELD_LOW"
assert a["native_kicad_erc"]=="NOT_RUN"
assert a["hardware_removal_test"]=="NOT_RUN"
assert not (a["machining_allowed"] or a["buying_allowed"] or a["main_merge_allowed"])
assert d["physical_integration_hold"] and d["other_six_modules_may_not_be_removed"]
print("PASS: reviewed 7 candidate positions, 5mm outer min, nonoverlapping 50x41 envelopes")
print("PASS: source-linked D7 static evidence retained, 55mm nominal sweep 7/7 only under removals/relocation")
print("PASS: original fan 7 infeasible on finite grid; 30mm alternate THERMAL NOT QUALIFIED")
print("PASS: physical safety / independent exchange / KiCad ERC / release remain BLOCKED, 0/6")
