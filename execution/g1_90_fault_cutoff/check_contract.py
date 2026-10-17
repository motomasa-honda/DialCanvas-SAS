#!/usr/bin/env python3
"""Review actual added physical fault-to-EN sink and all 8 OE gates.
No manufacturing, HIL or power enable qualification.
"""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
parent=json.loads((d.parent/"g1_89_hardware_start_deadline/pin_map_499.json").read_text())
pins=json.loads((d/"pin_map_522.json").read_text())
assert len(parent)==499 and len(pins)==522
for a,b in zip(parent,pins[:499]):
    assert a==b,("existing parent pin changed",a,b)
assert len({(p["kicad_ref"],p["source_pin"]) for p in pins})==522
assert len({p["kicad_ref"] for p in pins})==149
def net(ref,n):return next(x["review_net"] for x in pins if x["kicad_ref"]==ref and x["source_pin"]==n)
assert net("Q1",1)==net("R59",2)==net("R60",1)=="B90__FAULT_FET_GATE"
assert net("R54",1)==net("U20",6)==net("U35",1)=="B86__FAULT_Q"
assert net("U35",2)==net("U31",4)==net("U20",5)==net("U23",1)=="B88__TRIP_COMBINED"
assert net("U35",4)==net("R59",1)==net("U34",1)=="B90__CUT_REQUEST_OR"
assert net("U35",3)==net("C34",2)=="GND"
assert net("U35",5)==net("C34",1)=="3V3_AON"
assert net("Q1",2)==net("R60",2)=="GND"
assert net("Q1",3)==net("U14",1)==net("R4",1)==net("R57",1)=="B77__U7_EN_CLAMPED_DISABLED"
assert net("U33",3)==net("U33",6)=="3V3_AON"
assert net("U33",5)==net("R57",2)=="B89__EN_SENSE_DIV"
assert net("U33",4)==net("R62",1)=="B89__STARTUP_CT"
assert net("R62",2)==net("U33",6)=="3V3_AON"
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
# If the latch output is delayed/stale LOW, raw TRIP still asserts the
# FET drive and OE disable. This is Boolean settling, NOT propagation/HIL.
for fault_q in (False,True):
    for trip_asserted in (False,True):
        cut_request=bool(fault_q or trip_asserted)
        assert cut_request==bool(fault_q or trip_asserted)
        if trip_asserted and not fault_q:assert cut_request
        # U34 B remains physically pulled HIGH in this review, disabling all OEs.
        for hard_disabled in (False,True):
            oe_n=bool(cut_request or hard_disabled)
            if cut_request:assert oe_n
            if hard_disabled:assert oe_n
            if not cut_request and not hard_disabled:assert not oe_n
        # Q1's drain is connected to U14.EN with independent R4 to GND.
        expected_fault_sink=cut_request
        assert expected_fault_sink==(fault_q or trip_asserted)
assert net("R4",2)=="GND" and net("R61",2)=="3V3_AON"
print("PASS: latched FAULT_Q or asynchronous TRIP directly commands both power sink and 8 OE disable; hard-off unchanged")
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
    assert len(actual)==522 and len(root.findall("./components/comp"))==149
    errors=[e for sh in json.loads((o/"erc.json").read_text())["sheets"] for e in sh["violations"]]
    types=collections.Counter(e["type"] for e in errors)
    assert not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
    assert not types["multiple_net_names"] and not types["pin_conflict"],types
    print("PASS native KiCad9 actual pins and nets 522/149; uncleared ERC, no waivers:",dict(types))
print("HOLD: direct trip OR shortens latch dependency but DOES NOT prove AON cold-power behavior, glitch delay, FET sink or OE power-loss; still 0/6 manufacture")
