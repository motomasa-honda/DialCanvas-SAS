#!/usr/bin/env python3
"""G1-87 explicit delta of four old physical pins; exact 446-pad source contract."""
import json,re,subprocess,sys
from pathlib import Path
d=Path(__file__).resolve().parent
before=json.loads((d.parent/"g1_86_fault_latch/pin_map_404.json").read_text())
current=json.loads((d/"pin_map_446.json").read_text())
c=json.loads((d/"contract.json").read_text())
sch=(d/"forest_guardian_g1_87_release_qualified_review.kicad_sch").read_text()
assert len(before)==404 and len(current)==446
allowed={(x["ref"],x["pin"]):x["new_net"] for x in c["rewired"]}
differences={}
for orig,new in zip(before,current[:404]):
 assert orig["kicad_ref"]==new["kicad_ref"] and orig["source_pin"]==new["source_pin"]
 if orig["review_net"]!=new["review_net"]: differences[(new["kicad_ref"],new["source_pin"])]=new["review_net"]
assert differences==allowed,("unexpected parent pin change",differences)
assert len({(x["kicad_ref"],x["source_pin"]) for x in current})==446
assert len({x["kicad_ref"] for x in current})==124
assert len({x["review_net"] for x in current})==119
assert len(re.findall(r'\(wire \(pts',sch))==443
assert len(re.findall(r'\(label "',sch))==443
assert len(re.findall(r'\(no_connect ',sch))==3
for part in c["components"]:
 got=sorted((p for p in current if p["kicad_ref"]==part["ref"]),key=lambda v:v["source_pin"])
 assert [p["review_net"] for p in got]==part["pins"]
assert c["safety"]=={"eFuse_U7_EN":"GND through 10k","phase_28_OE":"HIGH DISABLED","fault_q":"STATUS ONLY","done_scope":19,"total_scope":48,"manufacturing":0}
assert next(x for x in current if x["group"]=="B77" and x["source_ref"]=="U7" and x["source_pin"]==1)["review_net"]=="B77__U7_EN_CLAMPED_DISABLED"
assert next(x for x in current if x["kicad_ref"]=="J18" and x["source_pin"]==2)["review_net"]=="3V3_AON"
assert next(x for x in current if x["kicad_ref"]=="U22" and x["source_pin"]==1)["review_net"]=="B87__CLEAR_QUALIFIED"
p=subprocess.run([sys.executable,"-m","unittest","discover","-s",str(d),"-p","test_controller.py","-v"],cwd=d)
if p.returncode:raise SystemExit(p.returncode)
print("PASS: 446 registered physical pads, 4 authorized rewires only, 12 new review parts")
print("PASS: 100k ideal boolean release-first rearm and held-clear fault recovery blocked")
print("HOLD: analog propagation / cold POR / mechanical debounce / PG/HIL / physical OE/EN")
