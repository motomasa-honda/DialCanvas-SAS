#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys
here=Path(__file__).resolve().parent
base=json.loads((here.parent/"g1_85_efuse_analog/pin_map_374.json").read_text())
m=json.loads((here/"pin_map_404.json").read_text())
c=json.loads((here/"contract.json").read_text())
s=(here/"forest_guardian_g1_86_fault_latch_review.kicad_sch").read_text()
assert m[:374]==base and len(m)==404 and len({(p["kicad_ref"],p["source_pin"]) for p in m})==404
assert len({p["kicad_ref"] for p in m})==112 and len({p["review_net"] for p in m})==110
assert len(re.findall(r'\(wire \(pts',s))==403 and len(re.findall(r'\(label "',s))==403
for ref,nets in c["pin_nets"].items():
 got=sorted((p for p in m if p["kicad_ref"]==ref),key=lambda p:p["source_pin"])
 assert [p["review_net"] for p in got]==nets
assert "(no_connect (at 165.1 876.3)" in s
assert next(v for v in m if v["kicad_ref"]=="U21" and v["source_pin"]==1)["review_net"]=="unconnected-(U21-NC-Pad1)"
assert c["safety"]["manufacturer_gates_closed"]==0 and c["safety"]["done"]==19
assert c["safety"]["oe_28"]=="HIGH PULLED DISABLED"
assert next(p for p in m if p["group"]=="B77" and p["source_ref"]=="U7" and p["source_pin"]==1)["review_net"]=="B77__U7_EN_CLAMPED_DISABLED"
p=subprocess.run([sys.executable,"-m","unittest","discover","-s",str(here),"-p","test_controller.py","-v"],cwd=here)
if p.returncode:raise SystemExit(p.returncode)
print("PASS: 404 exact physical pin mappings, 112 review components, 110 nets; fault NOR latch deterministic logic")
print("HOLD: no fresh-release qualifier, no real PG monitor to latch, no power enable")
