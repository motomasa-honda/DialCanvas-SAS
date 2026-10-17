#!/usr/bin/env python3
"""Review actual added physical fault-to-EN sink and all 8 OE gates.
No manufacturing, HIL or power enable qualification.
"""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
parent=json.loads((d.parent/"g1_89_hardware_start_deadline/pin_map_499.json").read_text())
pins=json.loads((d/"pin_map_515.json").read_text())
assert len(parent)==499 and len(pins)==515
for a,b in zip(parent,pins[:499]):
    assert a==b,("existing parent pin changed",a,b)
assert len({(p["kicad_ref"],p["source_pin"]) for p in pins})==515
assert len({p["kicad_ref"] for p in pins})==147
def net(ref,n):return next(x["review_net"] for x in pins if x["kicad_ref"]==ref and x["source_pin"]==n)
assert net("Q1",1)==net("R59",2)==net("R60",1)=="B90__FAULT_FET_GATE"
assert net("R59",1)==net("R54",1)==net("U20",6)==net("U34",1)=="B86__FAULT_Q"
assert net("Q1",2)==net("R60",2)=="GND"
assert net("Q1",3)==net("U14",1)==net("R4",1)==net("U33",3)=="B77__U7_EN_CLAMPED_DISABLED"
assert net("R4",2)=="GND"
assert net("U34",2)==net("R61",1)=="B90__OE_DISABLE_NOT_RELEASED"
assert net("R61",2)=="3V3_AON"
assert net("U34",3)==net("C33",2)=="GND"
assert net("U34",4)=="B78__PHASE_OE_N_FIXED_HIGH"
assert net("U34",5)==net("C33",1)=="3V3_AON"
for buf in ("U15","U16","U17","U18"):
    assert net(buf,1)==net(buf,19)==net("U34",4)
for pull in ("R14","R15","R16","R17"):
    assert net(pull,1)==net("U34",4) and net(pull,2)=="3V3_AON"
# Connectivity is real; current review always disables.
for fault in (False,True):
    for released in (False,True):
        # In delivered revision released is always False due physical 10k pull-up.
        disable=not released
        oe_n=bool(fault or disable)
        assert fault<=oe_n
        if not released:assert oe_n
print("PASS: one FAULT_Q-to-2N7002 gate/EN and FAULT_Q-to-8 buffer OE_N physical branch; OE hard disabled")
if len(sys.argv)>1:
    o=Path(sys.argv[1]);root=ET.parse(o/"native.net.xml").getroot()
    actual={}
    for netnode in root.findall("./nets/net"):
        for p in netnode.findall("node"):
            key=p.attrib["ref"],int(p.attrib["pin"])
            assert key not in actual,key
            actual[key]=netnode.attrib["name"].lstrip("/")
    expected={(p["kicad_ref"],p["source_pin"]):p["review_net"] for p in pins}
    assert actual==expected,[(k,v,actual.get(k)) for k,v in expected.items() if actual.get(k)!=v][:18]
    assert len(actual)==515 and len(root.findall("./components/comp"))==147
    errors=[e for sh in json.loads((o/"erc.json").read_text())["sheets"] for e in sh["violations"]]
    types=collections.Counter(e["type"] for e in errors)
    assert not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
    assert not types["multiple_net_names"] and not types["pin_conflict"],types
    print("PASS native KiCad9 actual pins and nets 515/147; uncleared ERC, no waivers:",dict(types))
print("HOLD: R4 EN pull-down still installed; U34 fixed disable HIGH; cold-start race, max sink, OE power-loss, full ERC/PCB/HIL not released")
