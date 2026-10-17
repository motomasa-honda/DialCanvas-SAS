#!/usr/bin/env python3
"""Validate all 364 labelled physical pins and actual KiCad review drawing.
Parses only the structural subset authored here; NOT native KiCad ERC."""
import json
import re
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sch=(HERE/"forest_guardian_g1_82_review.kicad_sch").read_text()
contract=json.loads((HERE/"design_contract.json").read_text())
mapping=json.loads((HERE/"pin_map_364.json").read_text())
paths={
 "B77":ROOT/"g1_phase77_140pins/nets_140.json",
 "B78":ROOT/"g1_28phase_disabled/nets_208.json",
 "B81":ROOT/"g1_81_rail_supervisor/nets_16.json"}
source={}
for group,path in paths.items():
 source[group]=json.loads(path.read_text())["nets"]

def name(group,net):
 if net=="GND":return "GND"
 if net=="3V3_AON" or (group=="B78" and net=="VCC_3V3_AON"):return "3V3_AON"
 if net=="5V_MOTOR":return "5V_MOTOR"
 return f"{group}__{net}"

expect={}
for group,nets in source.items():
 for net,pads in nets.items():
  for pad in pads:
   key=(group,pad)
   assert key not in expect,("duplicate",key)
   expect[key]=(net,name(group,net))
actual={}
for item in mapping:
 key=(item["group"],f'{item["source_ref"]}.{item["source_pin"]}')
 assert key not in actual
 actual[key]=(item["source_net"],item["review_net"])
assert actual==expect,("source-nets mismatch",set(actual)^set(expect))
assert len(actual)==contract["pads"]==364
assert Counter(key[0] for key in actual)=={"B77":140,"B78":208,"B81":16}
assert len({item["kicad_ref"] for item in mapping})==contract["symbols"]==98
# Each registered physical pin has exactly 1 local label at its assigned
# endpoint and exactly one real wire linking that point to a symbol pin.
for item in mapping:
 label=item["review_net"]
 x=str(item["wire_end_x"]);y=str(item["wire_end_y"])
 labelpat=f'(label {json.dumps(label)} (at {x} {y} 0)'
 assert sch.count(labelpat)==1,(item["group"],item["source_ref"],item["source_pin"],labelpat)
 pinx=str(round(float(x)+5.08,3)).rstrip('0').rstrip('.') if '.' in str(round(float(x)+5.08,3)) else str(round(float(x)+5.08,3))
 wirepat=f'(wire (pts (xy {x} {y}) (xy {pinx} {y}))'
 assert sch.count(wirepat)==1,("wire missing",item)
assert len(re.findall(r'\(label "',sch))==364
assert len(re.findall(r'\(wire \(pts',sch))==364
assert len(re.findall(r'\(property "FG_Source_Ref"',sch))==98
assert sch.count('(on_board no)')>=98
assert '(paper "A0")' in sch and '(version 20250114)' in sch
assert '(generator "forest_guardian_g1_82_review_export")' in sch
uuids=re.findall(r'\(uuid "([a-z0-9-]+)"\)',sch)
assert len(uuids)==len(set(uuids)) and len(uuids)>=364*2+98
def balanced(src):
 depth=0;quoted=False;esc=False
 for ch in src:
  if quoted:
   if esc:esc=False
   elif ch=="\\":esc=True
   elif ch=='"':quoted=False
  elif ch=='"':quoted=True
  elif ch=='(':depth+=1
  elif ch==')':
   depth-=1
   assert depth>=0
 assert depth==0 and not quoted
balanced(sch)
pins={key[1]:net for key,(original,net) in actual.items() if key[0]=="B77"}
assert pins["U7.1"]==pins["R_EN_PD.1"]=="B77__U7_EN_CLAMPED_DISABLED"
assert pins["R_EN_PD.2"]=="GND"
assert pins["U_ARM.5"]=="B77__ARM_LATCH_Q_ISOLATED"
assert pins["U7.6"]=="5V_MOTOR"
assert next(v for k,(n,v) in actual.items() if k==("B81","R_RAIL_TOP.1"))=="5V_MOTOR"
for n in range(1,5):
 for p in (1,19):
  assert actual[("B78",f"U_BUF{n}.{p}")][1]=="B78__PHASE_OE_N_FIXED_HIGH"
assert len(set(item["review_net"] for item in mapping))==contract["merged_nets"]
assert contract["safety"]=={
 "done_scope":19,"total_scope":48,"manufacturing_closed":0,
 "efuse_en":"GND_ONLY","phase_oe":"FIXED_HIGH",
 "native_erc":False,"pcb_drc":False,"hardware":False}
print(f"PASS: {len(actual)} mapped/labelled/wired physical pads, 98 virtual symbol instances, {contract['merged_nets']} explicit nets")
print("PASS: source drift and duplicate pins rejected, U7.EN/G1-78 OE disabled, rail aliases explicit")
print("HOLD: NO KiCad CLI/ERC, manufacturer pin-electrical types, PCB DRC or powered motor hardware")
