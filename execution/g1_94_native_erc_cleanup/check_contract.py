#!/usr/bin/env python3
"""G1-94: exact singleton NC transformation and uncompromised ERC3 supply blockers."""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
old=json.loads((d.parent/"g1_93_inhibited_phase_grant/pin_map_618.json").read_text())
new=json.loads((d/"pin_map_618_clean.json").read_text())
audit=json.loads((d/"nc_conversion_audit.json").read_text())
reg=json.loads((d.parent/"g1_87_rearm_release/erc_open_register.json").read_text())
assert len(old)==len(new)==618
assert len({x["kicad_ref"] for x in new})==182
assert len(audit)==16 and {z["old_net"] for z in audit}==set(reg["expected_label_nets"])
changes={(a["kicad_ref"],a["source_pin"]):(a["review_net"],b["review_net"])
         for a,b in zip(old,new) if a!=b}
assert set(changes)=={(x["ref"],x["pin"]) for x in audit},changes
for z in audit:
    o,n=changes[(z["ref"],z["pin"])]
    assert o==z["old_net"] and n==z["native_net"]
    assert n==f'unconnected-({z["ref"]}-P{z["pin"]}-Pad{z["pin"]})'
    assert z["evidence"].startswith("single physical terminal")
def net(r,n):
    return next(x["review_net"] for x in new if x["kicad_ref"]==r and x["source_pin"]==n)
assert net("U14",1)==net("R4",1)==net("R67",1)==net("R68",2)
assert net("R4",2)==net("R67",2)=="GND"
assert net("R61",2)=="3V3_AON"
for b in ("U15","U16","U17","U18"):
    assert net(b,1)==net(b,19)==net("U34",4)=="B78__PHASE_OE_N_FIXED_HIGH"
# Even one 68k limiter short and both EN GND pull-downs OPEN cannot
# permit eFuse UVLO. R57+58 =22k are STILL physically installed.
upper=3.6*(22000*1.01)/(68000*.99+22000*1.01)
assert upper<1.183,upper
# NC does not constitute manufacturing/footprint/ELECTRICAL approval.
print("PASS 16 intended NCs converted, 602 other pads unchanged; real 5V/AON drive open")
if len(sys.argv)>1:
    out=Path(sys.argv[1])
    root=ET.parse(out/"native.net.xml").getroot()
    got={}
    for netnode in root.findall("./nets/net"):
        for p in netnode.findall("node"):
            key=p.attrib["ref"],int(p.attrib["pin"])
            assert key not in got,key
            got[key]=netnode.attrib["name"].lstrip("/")
    expected={(x["kicad_ref"],int(x["source_pin"])):x["review_net"] for x in new}
    assert len(got)==len(expected)==618
    assert got==expected,[(k,e,got.get(k)) for k,e in expected.items() if got.get(k)!=e][:25]
    assert len(root.findall("./components/comp"))==182
    violations=[v for sh in json.loads((out/"erc.json").read_text())["sheets"] for v in sh["violations"]]
    types=collections.Counter(v["type"] for v in violations)
    assert len(violations)==3 and types=={"power_pin_not_driven":3},types
    # The 3 remain unwaived; they cannot be papered over with PWR_FLAG.
    print("PASS REAL KiCad9 XML 618 pads/182 parts; ERC 19 -> 3, remaining 3 UNSUPPRESSED power source blockers")
print("HOLD G1-05/06; 20/48 DONE_SCOPE; 0/6 manufacturing, no PCB/ERC power release")
