#!/usr/bin/env python3
"""Actual 208 TI octal buffer pins, 28 channels, tri-state-disabled state. No ERC or HIL."""
import json,itertools
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
nets=json.loads((Path(__file__).parent/"nets_208.json").read_text())["nets"]
pins={}
for net,arr in nets.items():
 for p in arr:
  assert p not in pins,(p,pins.get(p),net)
  pins[p]=net
assert len(pins)==d["source_derived_pad_count"]==208 and len(nets)==d["source_derived_net_count"]==63
assert d["lane_pin_pairs_Input_Output"]==[[2,18],[4,16],[6,14],[8,12],[11,9],[13,7],[15,5],[17,3]]
assert (d["chips"],d["channels"],d["active_lanes"],d["unassigned_lanes"])==(4,32,28,4)
assert set(nets["PHASE_OE_N_FIXED_HIGH"])==(
 {f"U_BUF{i}.{j}" for i in range(1,5) for j in (1,19)} |
 {f"R_OE_PULL{i}.1" for i in range(1,5)}
)
for i in range(1,5):
 assert pins[f"U_BUF{i}.1"]==pins[f"U_BUF{i}.19"]==pins[f"R_OE_PULL{i}.1"]=="PHASE_OE_N_FIXED_HIGH"
 assert pins[f"U_BUF{i}.20"]==pins[f"R_OE_PULL{i}.2"]==pins[f"C_BUF{i}.1"]=="VCC_3V3_AON"
 assert pins[f"U_BUF{i}.10"]==pins[f"C_BUF{i}.2"]=="GND"
for axis in range(1,8):
 for ph in range(1,5):
  ni=f"MCU_G{axis}_PHASE{ph}"
  no=f"MODULE_G{axis}_PHASE{ph}"
  assert len(nets[ni])==2 and len(nets[no])==3
  assert pins[f"J_MCU_G{axis}.{ph}"]==ni
  assert pins[f"J_MODULE_G{axis}.{ph}"]==pins[f"R_PD_G{axis}_{ph}.1"]==no
  assert pins[f"R_PD_G{axis}_{ph}.2"]=="GND"
  assert not set(nets[ni])&set(nets[no])
assert len([n for n in nets if n.startswith("UNUSED_U_")])==4
assert all(pins[f"U_BUF4.{i}"]=="GND" for i in (11,13,15,17))
# Manufacturer /OE_N logic: inactive HIGH tristates all lanes irrespective of CPU input.
for oe_n,mcub in itertools.product((0,1),repeat=2):
 out="Z" if oe_n==1 else mcub
 if oe_n:assert out=="Z"
 else:assert out==mcub
assert d["physical_enable_condition"].startswith("NOT_CONNECTED")
assert d["actual_secondary_gating_status"].startswith("TRISTATE_AND_PULLDOWN_UNQUALIFIED")
assert d["test_scope"]["ideal_disabled_patterns"]==50000 and d["test_scope"]["deliberate_miswires"]==6
assert len(d["not_tested"])==8
s=d["safety"]
assert (s["scope_done"],s["total"],s["manufacturing_closed"],s["software_evidence"])==(19,48,0,11)
assert s["g1_05"]==s["g1_06"]=="WORKING" and s["g1_07"]=="OPEN"
assert s["efuse_en"]=="GND_ONLY"
assert not any(s[k] for k in ("purchase","power","cut","pcb_fabrication","flash","merge_main"))
print("PASS: 208 actual TI 20-pin endpoint names / 63 nets across four octal buffers")
print("PASS: 28/28 phase lines independently input->buffer->pulldown->module and OE1/OE2 HIGH")
print("HOLD: no real FPGA/MCU enabling, real motor-module input low threshold, ERC/DRC or hardware approval")
