#!/usr/bin/env python3
"""G6-06: source-to-assembly and axis-to-service *review order*, never hardware clearance."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json
root=Path(__file__).resolve().parent
execution=root.parent
j=lambda n:json.loads((root/n).read_text())
source=json.loads((execution/"g6_03_80_source_faces/design_contract.json").read_text())
layout=json.loads((execution/"cassettes/seven_axis_conditional_layout.json").read_text())
ev=j("evidence_contract.json")
a=j("assembly_review.json")
service=j("service_review.json")
branches=j("branch_register_42.json")
parts=sum(source["component_groups"].values(),[])
assert len(parts)==80 and len(set(parts))==80
assert source["original_d7_sha256"]==ev["source_d7_sha256"]
assert source["original_d7_solids"]==ev["source_solids"]==1774
assert ev["assembly_steps"]==len(a)==17
assert [s["seq"] for s in a]==list(range(1,18))
idmap={s["id"]:s for s in a}
assert len(idmap)==17
for s in a:
 assert all(pr in idmap and idmap[pr]["seq"]<s["seq"] for pr in s["depends"])
 assert s["physical_status"]=="PROCEDURE_ONLY_NOT_ASSEMBLED"
 assert s["operation_authorized"] is False
assert Counter(p for s in a for p in s["source_parts"])==Counter(parts)
assert next(s for s in a if s["id"]=="A13")["source_parts"]==source["component_groups"]["gear"]
assert len(next(s for s in a if s["id"]=="A11")["source_parts"])==14
assert len(service)==105 and ev["service_steps_total"]==105
assert sorted({s["axis"] for s in service})==[f"G{i}" for i in range(1,8)]
slot_map={f'G{s["axis"]}':s for s in layout["slots"]}
assert ev["axial_retraction_mm_candidate_only"]==layout["axial_retraction_mm"]==55
assert not layout["original_fan_60mm_case"]["seven_modules_feasible_on_grid"]
assert layout["fan_relocation_case"]["seven_modules_feasible_on_grid"]
assert set(slot_map)=={f"G{i}" for i in range(1,8)}
must_steps={f"S{i:02}" for i in range(1,16)}
for axis,slot in slot_map.items():
 ss=[s for s in service if s["axis"]==axis]
 assert len(ss)==15 and {s["step"] for s in ss}==must_steps
 assert [s["order"] for s in ss]==list(range(1,16))
 assert all(s["axis_center_mm"]==[slot["x"],slot["y"]] for s in ss)
 assert all(s["required_retraction_plus_z_mm"]==55 for s in ss)
 assert all(s["other_axis_module_removal_allowed"] is False for s in ss)
 assert all(s["gears_or_p3_removed_allowed"] is False for s in ss)
 assert all(s["common_rear_cover_removed_allowed"] is True for s in ss)
 assert all(s["cutting_approval"] is False and s["actual_trial"]=="NOT_TESTED" for s in ss)
 if axis=="G5":assert all("DO NOT CUT" in s["wood_pocket_rule"] for s in ss)
assert len(branches)==42 and len({(b["axis"],b["pin"]) for b in branches})==42
with (execution/"m1_inspection_42.csv").open(encoding="utf-8-sig",newline="") as fh:
 original=list(csv.DictReader(fh))
for line in original:
 match=next(b for b in branches if b["axis"]==line["axis"] and b["pin"]==int(line["pin"]))
 assert match["connector"]==line["carrier_connector"]==f'J_M1_{line["axis"]}'
 assert match["signal"]==line["signal"]
 assert match["physical_pin"]==line["module_physical_pin"]=="UNVERIFIED"
 assert match["cut_length"]==line["cut_length_mm"]=="TBD"
 assert match["inspection"]==line["inspection"]=="NOT_TESTED"
assert ev["source_part_count"]==80 and ev["assembly_cover_exact"]==80
assert ev["branch_terminals_total"]==42 and ev["service_axes"]==7
assert ev["critical_constraints"]["original_fan_must_relocate"]
assert ev["critical_constraints"]["g5_machining_allowed"] is False
assert not ev["physical_verified"] and not ev["status_gate"]["power_allowed"]
assert ev["status_gate"]["manufacturing_gates_closed"]==0
assert not any(ev["status_gate"][p] for p in ("cut_allowed","pcb_fabrication_allowed","purchase_allowed","main_merge_allowed"))
with (execution/"tasks.csv").open(encoding="utf-8-sig",newline="") as fh: tasks=list(csv.DictReader(fh))
p=json.loads((execution/"progress.json").read_text())
assert len(tasks)==48 and len({x["ID"] for x in tasks})==48
assert next(row for row in tasks if row["ID"]=="G6-06")["Status"]=="DONE_SCOPE"
assert next(row for row in tasks if row["ID"]=="G6-07")["Status"]=="HARDWARE_WAIT"
assert next(row for row in tasks if row["ID"]=="G6-08")["Status"]=="OPEN"
assert next(row for row in tasks if row["ID"]=="G2-07")["Status"]=="OPEN"
# G6-06's historical completion remains true when later independent work starts.
# Validate the CURRENT 48-task arithmetic via guard.py, not frozen G6-06 snapshot.
from collections import Counter
states=Counter(x["Status"] for x in tasks)
assert p["scoped_evidence_done"]==states["DONE_SCOPE"]
assert p["working"]==states["WORKING"] and p["open"]==states["OPEN"]
assert p["hardware_wait"]==states["HARDWARE_WAIT"]==4
assert sum(states.values())==48
assert p["manufacturer_release_closed"]==0 and p["software_evidence_passed"]==11
print("PASS G6-06 actual completion: all 80 named source parts covered once, 17 topologically ordered assembly stages")
print("PASS seven independent 15-stage service travellers (105 actions), with exact 42 original 6-pin connection references")
print(f"PASS existing cooling/G5/55mm/other six axle and NO-PHYSICAL-FAB-HIL gates retained; project {states['DONE_SCOPE']}/48, manufacture 0/6")
