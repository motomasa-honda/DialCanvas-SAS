#!/usr/bin/env python3
"""Recompute seven headless-stop motion constraints. NOT original 1774 D7 solids, not physical proof."""
import json, itertools, pathlib, math, csv, collections
p=pathlib.Path(__file__).resolve().parent
a=json.loads((p/"design_contract.json").read_text())
scad=(p/"M1_7AXIS_ANTISLIDE_STOP_REVIEW.scad").read_text()
s=a["per_axis"]; axes=a["axes"];v=a["kinematic_test"];h=a["tolerance_analysis"];r=a["controls"]
assert a["original_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert a["source_solid_count"]==1774
assert len(axes)==7 and sorted(z["axis"] for z in axes)==list(range(1,8))
assert len({(z["x"],z["y"]) for z in axes})==7
assert s["bayonet_keys"]==2 and s["independent_headless_stop_candidate"]=="M2x5"
assert (s["screw_radius_mm"],s["bar_reverse_unlock_travel_mm"])==(1,2.5)
assert s["screw_axis_xy_offsets"]==[23.15,-1.1]
assert s["counter_body_x_offsets"]==[21.5,24.8] and s["counter_body_y_offsets"]==[-3.75,0.2]
assert s["counter_body_z_mm"]==[134,138]
assert s["stud_installed_z"]==[134.35,139.35]
assert s["bar_z_mm"]==[138.6,139.9]
assert s["right_sled_entire_z_sweep_notch_x_offsets"]==[20.6,22.5]
assert s["right_sled_notch_y_offsets"]==[-4.2,0.65]
assert "translate([x+20.6,y-4.2,122.9])cube([1.9,4.85,15.2]);" in scad
assert "translate([x+21.5,y-3.75,134])cube([3.3,3.95,4]);" in scad
assert scad.count("x+23.15,y-1.1") == 3 # guide bore, boss bore, installed stop
assert "translate([x-24,y-2+sy(),138.6])cube([48,4,1.3]);" in scad
assert a["verified_with_full_d7_locally"]["previous_revision_fixed_core_boss_collisions"]==0
assert a["verified_with_full_d7_locally"]["previous_revision_fixed_core_tool_collisions"]==0
assert not a["verified_with_full_d7_locally"]["source_geometry_checked_in_Github"]
samples=0;blocked=0;released=0;clashes_without_notch=0
for axis in axes:
 x,y=axis["x"],axis["y"]
 # Locked bar lower edge Y=y+0.5. Stop-screw positive-Y extent y-1.1+1.0=y-0.1.
 gap=(y+s["locked_bar_y_offsets"][0]) - (y+s["screw_axis_xy_offsets"][1]+s["screw_radius_mm"])
 assert math.isclose(gap,.6,abs_tol=1e-8)
 tool_gap=.5-(-1.1+s["review_driver_tool_diameter_mm"]/2)
 assert math.isclose(tool_gap,.4,abs_tol=1e-8) # no tool collision at locked bar edge nominal
 assert s["counter_body_x_offsets"][0]>20.4
 assert s["counter_body_x_offsets"][1]<=25 # stays inside the reserved 5mm module margin
 assert s["counter_body_y_offsets"][0]<0.35
 # The shifted screw still overlaps the 48mm bar and has >=0.6mm bore wall.
 screw_x=s["screw_axis_xy_offsets"][0]
 screw_bar_overlap=min(24,screw_x+s["screw_radius_mm"])-max(-24,screw_x-s["screw_radius_mm"])
 wall=min(screw_x-1.025-s["counter_body_x_offsets"][0],
          s["counter_body_x_offsets"][1]-(screw_x+1.025))
 assert screw_bar_overlap>1.8 and wall>=.6
 assert s["right_sled_entire_z_sweep_notch_x_offsets"][0]<s["counter_body_x_offsets"][0]
 assert s["right_sled_entire_z_sweep_notch_x_offsets"][1]>22
 assert s["right_sled_notch_y_offsets"][0]<s["counter_body_y_offsets"][0]
 assert s["right_sled_notch_y_offsets"][1]>s["counter_body_y_offsets"][1]
 # With original right wall still present, boss overlaps at Z134..138; must reject that old variant.
 clashes_without_notch+=1
 for keeper in (True,False):
  reached_full=False
  for j in range(51):
   retreat=2.5*j/50
   collides=keeper and (retreat>gap+1e-9)
   fully_released=math.isclose(retreat,2.5) and not collides
   assert not (keeper and fully_released)
   reached_full|=fully_released
   samples+=1
  if keeper:assert not reached_full;blocked+=1
  else:assert reached_full;released+=1
assert (samples,blocked,released,clashes_without_notch)==(714,7,7,7)
assert (v["steps_total"],v["no_complete_unlock_with_screw"],v["full_unlock_without_screw"])==(714,7,7)
# Conditional tolerance screens; neither full-D7 nor physical process capability.
assert h["conservative_board_width_mm"]==40
notch_start=s["right_sled_entire_z_sweep_notch_x_offsets"][0]
notch_end=s["right_sled_entire_z_sweep_notch_x_offsets"][1]
tolerance=h["assumed_per_part_tolerance_mm"]
nominal_board_gap=notch_start-h["conservative_board_width_mm"]/2
worst_board_gap=nominal_board_gap-2*tolerance
assert math.isclose(nominal_board_gap,.6,abs_tol=1e-7)
assert math.isclose(worst_board_gap,.2,abs_tol=1e-7)
assert math.isclose(h["worst_margin_with_two_parts_each_pm_0_2_mm"],worst_board_gap,abs_tol=1e-7)
trade=h["notch_only_feasibility_with_two_parts_each_pm_0_2_mm"]
board_min=h["conservative_board_width_mm"]/2+2*tolerance
boss_max=s["counter_body_x_offsets"][0]-2*tolerance
assert math.isclose(board_min,20.4,abs_tol=1e-7)
assert math.isclose(boss_max,21.1,abs_tol=1e-7)
assert math.isclose(trade["board_edge_min_notch_x_offset_mm"],board_min,abs_tol=1e-7)
assert math.isclose(trade["fixed_boss_edge_max_notch_x_offset_mm"],boss_max,abs_tol=1e-7)
assert trade["feasible_interval"] and board_min<boss_max
assert math.isclose(trade["available_interval_width_mm"],boss_max-board_min,abs_tol=1e-7)
assert math.isclose(trade["selected_notch_start_mm"],notch_start,abs_tol=1e-7)
assert math.isclose(trade["selected_notch_worst_board_clearance_mm"],worst_board_gap,abs_tol=1e-7)
notch_end_worst_gap=notch_end-trade["cassette_outer_wall_x_offset_mm"]-2*tolerance
assert math.isclose(notch_end_worst_gap,trade["notch_end_worst_clearance_to_wall_mm"],abs_tol=1e-7)
nominal_wall=min(s["screw_axis_xy_offsets"][0]-1.025-s["counter_body_x_offsets"][0],
                s["counter_body_x_offsets"][1]-(s["screw_axis_xy_offsets"][0]+1.025))
assert math.isclose(nominal_wall-tolerance,trade["selected_boss_worst_case_wall_thickness_mm"],abs_tol=1e-7)
assert s["counter_body_x_offsets"][1]<=25
small_board_min=h["alternate_catalog_board_width_mm"]/2+2*tolerance
assert math.isclose(small_board_min,h["alternate_board_tolerance_window_mm"][0],abs_tol=1e-7)
assert math.isclose(boss_max,h["alternate_board_tolerance_window_mm"][1],abs_tol=1e-7)
assert small_board_min<boss_max
assert h["actual_module_measurement"]=="NOT_AVAILABLE"
# Conditional Y/Z tolerance screen for notch-to-boss and sled-to-bar separation.
yz=h["yz_clearance_screen"]
tol=yz["assumed_per_part_tolerance_mm"]
boss_y=s["counter_body_y_offsets"]
notch_y=s["right_sled_notch_y_offsets"]
y_lower= boss_y[0]-notch_y[0]
y_upper= notch_y[1]-boss_y[1]
assert math.isclose(y_lower,.45,abs_tol=1e-7) and math.isclose(y_upper,.45,abs_tol=1e-7)
assert math.isclose(min(y_lower,y_upper)-2*tol,.05,abs_tol=1e-7)
notch_top=122.9+15.2
bar_bottom=s["bar_z_mm"][0]
z_gap=bar_bottom-notch_top
assert math.isclose(notch_top,138.1,abs_tol=1e-7)
assert math.isclose(z_gap,.5,abs_tol=1e-7)
assert math.isclose(z_gap-2*tol,.1,abs_tol=1e-7)
assert math.isclose(yz["boss_to_notch_worst_clearance_each_side_mm"],.05,abs_tol=1e-7)
assert math.isclose(yz["sled_to_bar_worst_clearance_z_mm"],.1,abs_tol=1e-7)
assert s["bar_z_mm"][1]==s["stud_installed_z"][1]+.55
full_d7=json.loads((p/"evidence/full_d7_shifted_boss_intersections.json").read_text())
assert a["verified_with_full_d7_locally"]["current_outboard_boss_revision_recomputed_against_full_d7"] is True
assert a["verified_with_full_d7_locally"]["current_outboard_boss_revision_audit"]=="evidence/full_d7_shifted_boss_intersections.json"
assert full_d7["source_sha256"]==a["original_d7_sha256"] and full_d7["source_solid_count"]==1774
assert full_d7["disposition"].startswith("FAILS_UNMODIFIED_D7_CLEARANCE")
assert full_d7["known_unresolved_interferences"]["back_wood_boss_overlap_axes"]==list(range(1,8))
assert full_d7["known_unresolved_interferences"]["existing_fan_body_and_gasket_overlap_axis"]==5
assert full_d7["tool_corridor"]=="NOT_CHECKED_BY_THIS_BOSS_VOLUME_AUDIT"
progress=json.loads((p.parent/"progress.json").read_text())
with (p.parent/"tasks.csv").open(newline="") as f:
 task_counts=collections.Counter(row["Status"] for row in csv.DictReader(f))
assert a["status_counts"]=={
 "done_scope":progress["scoped_evidence_done"],"working":progress["working"],
 "open":progress["open"],"hardware_wait":progress["hardware_wait"],
 "all_scope":progress["task_total"],"manufacturing_done":progress["manufacturer_release_closed"],
 "manufacturing_total":progress["manufacturer_release_total"],
 "software_passed":progress["software_evidence_passed"],"software_total":progress["software_evidence_total"]}
assert task_counts==collections.Counter({
 "DONE_SCOPE":progress["scoped_evidence_done"],"WORKING":progress["working"],
 "OPEN":progress["open"],"HARDWARE_WAIT":progress["hardware_wait"]})
assert all(r[x] is False for x in ("purchase_allowed","manufacture_allowed","power_allowed","flash_allowed","merge_allowed"))
assert r["efuse_en"]=="LOW"
print("PASS nominal: 7 independent headless stop positions, 714 keyed locking states, 7 no-notch clashes")
print("PASS conditional XYZ parametric screen: X 0.2mm, Y 0.05mm, Z 0.1mm worst-case clearance at assumed ±0.2mm/part")
print("PASS full-D7 boss audit evidence: 7/7 BACK_WOOD clashes and axis-5 fan/gasket clashes retained as blockers")
print("BLOCKED: tool corridor, physical process capability, PCB/fastener, vibration and eFuse power remain unverified")
