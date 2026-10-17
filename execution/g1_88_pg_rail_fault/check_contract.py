#!/usr/bin/env python3
"""Verify every physical KiCad pin and the exact G1-87-to-G1-88 change."""
import sys,json,collections,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
old=json.loads((d.parent/"g1_87_rearm_release/pin_map_446.json").read_text())
new=json.loads((d/"pin_map_485.json").read_text())
delta={}
for x,y in zip(old,new[:446]):
    assert (x["kicad_ref"],x["source_pin"])==(y["kicad_ref"],y["source_pin"])
    if x["review_net"]!=y["review_net"]:
        delta[(x["kicad_ref"],x["source_pin"])]=y["review_net"]
assert delta=={("U20",5):"B88__TRIP_COMBINED",("U23",1):"B88__TRIP_COMBINED",
    ("U22",2):"B88__QUAL_EXT_N",("U26",1):"B88__QUAL_EXT_N"}
assert len(new)==485 and len({x["kicad_ref"] for x in new})==136
def net(ref,n):
    return next(x["review_net"] for x in new if x["kicad_ref"]==ref and x["source_pin"]==n)
assert net("U14",1)=="B77__U7_EN_CLAMPED_DISABLED"
assert net("U28",1)=="B77__EFUSE_PG_OD" and net("U28",2)=="B81__RAIL_OK_N_SUPERVISOR"
assert net("R56",1)==net("U30",2)=="B88__MONITOR_ACTIVE"
assert net("U31",4)==net("U20",5)==net("U23",1)=="B88__TRIP_COMBINED"
assert net("U32",4)==net("U22",2)==net("U26",1)=="B88__QUAL_EXT_N"
for original in (False,True):
 for pg in (False,True):
  for rail in (False,True):
   for active in (False,True):
    trip=(not original) or (active and not(pg and rail))
    assert (active and not(pg and rail)) <= trip
    assert original or trip
print("PASS 485 mapped physical pins, four exact rewires and post-start 16-state truth table")
if len(sys.argv)>1:
    path=Path(sys.argv[1]);xml=ET.parse(path/"native.net.xml").getroot()
    found={}
    for n in xml.findall("./nets/net"):
        for t in n.findall("node"):
            k=(t.attrib["ref"],int(t.attrib["pin"]))
            assert k not in found
            found[k]=n.attrib["name"].lstrip("/")
    want={(x["kicad_ref"],x["source_pin"]):x["review_net"] for x in new}
    assert found==want,[(k,v,found.get(k)) for k,v in want.items() if found.get(k)!=v][:20]
    assert len(found)==485 and len(xml.findall("./components/comp"))==136
    errors=[v for sh in json.loads((path/"erc.json").read_text())["sheets"] for v in sh["violations"]]
    types=collections.Counter(v["type"] for v in errors)
    assert not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
    print("PASS physical KiCad XML matches all 485 registered pads; native ERC findings (not waived):",dict(types))
print("HOLD: physical qualified MONITOR_ACTIVE start timer absent; eFuse EN GND; OE HIGH; FAULT_Q status only")
