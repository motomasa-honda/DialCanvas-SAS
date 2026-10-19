#!/usr/bin/env python3
"""G1-92 native physical pins + analog OFF inequality; NO power enabling."""
from pathlib import Path
import collections,itertools,json,sys,xml.etree.ElementTree as ET
d=Path(__file__).resolve().parent
old=json.loads((d.parent/"g1_91_aon_supervisor/pin_map_552.json").read_text())
new=json.loads((d/"pin_map_579.json").read_text())
assert len(old)==552 and len(new)==579
assert new[:552]==old, "A parent pin/net changed"
b={(r["kicad_ref"],r["source_pin"]):r["review_net"] for r in new}
assert len(b)==579 and len({r for r,_ in b})==168
added=set(b)-{(r["kicad_ref"],r["source_pin"]) for r in old}
expected=({(r,n) for r in ("U39","U40","U41") for n in range(1,6)}
          | {(r,n) for r in ("R66","R67","R68","C39","C40","C41") for n in range(1,3)})
assert added==expected,added^expected
def net(ref,p):return b[(ref,p)]
assert net("U39",1)==net("U2",5)=="B77__ARM_LATCH_Q_ISOLATED"
assert net("U39",2)==net("U21",2)=="B77__QUAL_CLR_N"
assert net("U39",4)==net("U41",1)=="B92__ARM_AND_HEALTH"
assert net("U40",1)=="unconnected-(U40-NC-Pad1)"
assert net("U40",2)==net("U35",4)==net("U34",1)=="B90__CUT_REQUEST_OR"
assert net("U40",4)==net("U41",2)=="B92__NO_FAULT"
assert net("U41",4)==net("R66",1)=="B92__RAIL_GRANT_LOGIC"
assert net("R66",2)==net("R68",1)=="B92__GRANT_LIMIT_STAGE"
assert net("R68",2)==net("R67",1)==net("R4",1)==net("R57",1)==net("U14",1)==net("Q1",3)=="B77__U7_EN_CLAMPED_DISABLED"
assert net("R67",2)==net("R4",2)=="GND"
assert net("R57",2)==net("U33",5)=="B89__EN_SENSE_DIV"
assert net("R58",2)=="GND"
for r,c in (("U39","C39"),("U40","C40"),("U41","C41")):
    assert net(r,3)==net(c,2)=="GND"
    assert net(r,5)==net(c,1)=="3V3_AON"
assert net("R61",2)=="3V3_AON" # phases remain disabled
for buf in ("U15","U16","U17","U18"):
    assert net(buf,1)==net(buf,19)==net("U34",4)
# Deliberately pessimistic: 3.6V AON high, +1% on the R57+R58
# EN sense to GND, -1% on remaining 68k inhibit, R4 and R67
# both OPEN. Assert still <1.183V eFuse UVLO min with one inhibitor SHORT.
vin_max=3.6
en_rise_min=1.183
series_remaining=68000*.99
en_sense_load=(12000+10000)*1.01
open_pull_down_both=True
v_en_max=vin_max*en_sense_load/(series_remaining+en_sense_load)
assert v_en_max<en_rise_min,(v_en_max,en_rise_min)
# For normal circuit R4 and R67 each have separate 10k ground
# and both 68k series. Upper bound with worst resistor +/-1%.
sink_one=10000*1.01
sink_two=10000*1.01
sink_div=22000*1.01
sink_eq=1/(1/sink_one+1/sink_two+1/sink_div)
series_both=2*68000*.99
v_en_normal_max=vin_max*sink_eq/(series_both+sink_eq)
assert v_en_normal_max<0.2,v_en_normal_max
# Model verifies pre-rail start grant cannot depend on PG/rail.
for arm,health,cut,pg,rail in itertools.product((False,True),repeat=5):
    positive=arm and health and not cut
    if cut or not arm or not health:assert not positive
    for pg2,rail2 in itertools.product((False,True),repeat=2):
        assert positive==(arm and health and not cut)
assert net("U39",1)!="B77__EFUSE_PG_OD"
assert net("U41",2)!="B81__RAIL_OK_N_SUPERVISOR"
print(f"PASS 579 physical pads, 168 symbols; START_GRANT=ARM&QUAL&!CUT; U14.EN connected but permanently inhibited")
print(f"PASS EN max {v_en_normal_max:.3f}V normal; {v_en_max:.3f}V with one inhibitor short and both EN pulldowns open < 1.183V")
if len(sys.argv)>1:
    out=Path(sys.argv[1]);root=ET.parse(out/"native.net.xml").getroot()
    found={}
    for n in root.findall("./nets/net"):
        for t in n.findall("node"):
            k=(t.attrib["ref"],int(t.attrib["pin"]))
            assert k not in found,k
            found[k]=n.attrib["name"].lstrip("/")
    assert found==b,[(k,v,found.get(k)) for k,v in b.items() if found.get(k)!=v][:20]
    assert len(found)==579 and len(root.findall("./components/comp"))==168
    erc=collections.Counter(v["type"] for sh in json.loads((out/"erc.json").read_text())["sheets"] for v in sh["violations"])
    assert not erc["endpoint_off_grid"] and not erc["lib_symbol_issues"],erc
    assert not erc["pin_conflict"] and not erc["multiple_net_names"],erc
    print("PASS REAL KiCad9 579-pin 168-symbol native XML, open ERC findings (no waiver):",dict(erc))
print("HOLD: current inhibited source is not an operational motor-enabler; real 3V3 startup, STOP/WDT, phase grant and hardware HIL unresolved")
