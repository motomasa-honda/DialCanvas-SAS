#!/usr/bin/env python3
"""Recompute seven headless-stop motion constraints. NOT original 1774 D7 solids, not physical proof."""
import json, itertools, pathlib, math
p=pathlib.Path(__file__).resolve().parent
a=json.loads((p/"design_contract.json").read_text())
s=a["per_axis"]; axes=a["axes"];v=a["kinematic_test"];h=a["tolerance_analysis"];r=a["controls"]
assert a["original_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert a["source_solid_count"]==1774
assert len(axes)==7 and sorted(z["axis"] for z in axes)==list(range(1,8))
assert len({(z["x"],z["y"]) for z in axes})==7
assert s["bayonet_keys"]==2 and s["independent_headless_stop_candidate"]=="M2x5"
assert (s["screw_radius_mm"],s["bar_reverse_unlock_travel_mm"])==(1,2.5)
assert s["screw_axis_xy_offsets"]==[22.25,-1.1]
assert s["counter_body_x_offsets"]==[20.5,24] and s["counter_body_y_offsets"]==[-3.75,0.2]
assert s["counter_body_z_mm"]==[134,138]
assert s["stud_installed_z"]==[134.35,139.35]
assert s["bar_z_mm"]==[138.05,139.35]
assert s["right_sled_entire_z_sweep_notch_x_offsets"]==[20.3,22.3]
assert s["right_sled_notch_y_offsets"]==[-3.9,0.35]
assert a["verified_with_full_d7_locally"]["fixed_core_boss_collisions"]==0
assert a["verified_with_full_d7_locally"]["fixed_core_tool_collisions"]==0
assert not a["verified_with_full_d7_locally"]["source_geometry_checked_in_Github"]
samples=0;blocked=0;released=0;clashes_without_notch=0
for axis in axes:
 x,y=axis["x"],axis["y"]
 # Locked bar lower edge Y=y+0.5. Stop-screw positive-Y extent y-1.1+1.0=y-0.1.
 gap=(y+s["locked_bar_y_offsets"][0]) - (y+s["screw_axis_xy_offsets"][1]+s["screw_radius_mm"])
 assert math.isclose(gap,.6,abs_tol=1e-8)
 tool_gap=.5-(-1.1+s["review_driver_tool_diameter_mm"]/2)
 assert math.isclose(tool_gap,.4,abs_tol=1e-8) # no tool collision at locked bar edge nominal
 assert (s["counter_body_x_offsets"][0]<22 and s["counter_body_y_offsets"][0]<0.35)
 assert s["right_sled_entire_z_sweep_notch_x_offsets"][0]<20.4
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
# Critical design failure must be persisted even when geometry checks pass.
assert h["conservative_board_width_mm"]==40
assert math.isclose(20.3-40/2,.3,abs_tol=1e-7)
assert math.isclose(.3-2*.2,-.1,abs_tol=1e-7)
assert h["worst_margin_with_two_parts_each_pm_0_2_mm"]<0
assert math.isclose(20.3-35/2-2*.2,2.4,abs_tol=1e-7)
trade=h["notch_only_feasibility_with_two_parts_each_pm_0_2_mm"]
tolerance=h["assumed_per_part_tolerance_mm"]
board_min=h["conservative_board_width_mm"]/2+2*tolerance
boss_max=s["counter_body_x_offsets"][0]-2*tolerance
assert math.isclose(board_min,20.4,abs_tol=1e-7)
assert math.isclose(boss_max,20.1,abs_tol=1e-7)
assert math.isclose(trade["board_edge_min_notch_x_offset_mm"],board_min,abs_tol=1e-7)
assert math.isclose(trade["fixed_boss_edge_max_notch_x_offset_mm"],boss_max,abs_tol=1e-7)
assert math.isclose(trade["gap_between_constraints_mm"],board_min-boss_max,abs_tol=1e-7)
assert not trade["feasible_interval"] and board_min>boss_max
assert trade["disposition"].startswith("NO_NOTCH_ONLY_SOLUTION")
small_board_min=h["alternate_catalog_board_width_mm"]/2+2*tolerance
assert math.isclose(small_board_min,h["alternate_board_tolerance_window_mm"][0],abs_tol=1e-7)
assert math.isclose(boss_max,h["alternate_board_tolerance_window_mm"][1],abs_tol=1e-7)
assert small_board_min<boss_max
assert h["actual_module_measurement"]=="NOT_AVAILABLE"
assert a["status_counts"]=={"done_scope":16,"all_scope":48,"manufacturing_done":0,"manufacturing_total":6,"software_passed":11,"software_total":14}
assert all(r[x] is False for x in ("purchase_allowed","manufacture_allowed","power_allowed","flash_allowed","merge_allowed"))
assert r["efuse_en"]=="LOW"
print("PASS nominal: 7 independent headless stop positions, 714 keyed locking states, 7 no-notch clashes")
print("FAIL design acceptance AS INTENDED: 40mm module x 2*0.2mm tolerances => -0.1mm clearance")
print("FAIL NOTCH-ONLY TOLERANCE WINDOW: 40mm board requires notch start >=20.4mm; fixed boss requires <=20.1mm; infeasible by 0.3mm")
print("BLOCKED: no physical screw vibration retention, real PCB, wood/fan, native D7 recompute, eFuse power")
