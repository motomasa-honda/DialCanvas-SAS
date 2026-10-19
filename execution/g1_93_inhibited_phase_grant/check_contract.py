#!/usr/bin/env python3
"""Exact G1-93 actual native KiCad phase grant; NO physical enable approval."""
import itertools,collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
old=json.loads((d.parent/"g1_92_inhibited_start_grant/pin_map_579.json").read_text())
new=json.loads((d/"pin_map_618.json").read_text())
assert len(new)==618 and new[:579]==old, "Any parent pin rewired: reject"
m={(z["kicad_ref"],z["source_pin"]):z["review_net"] for z in new}
assert len(m)==618 and len({r for r,n in m})==182
added=set(m)-{(z["kicad_ref"],z["source_pin"]) for z in old}
expected=({("U42",n) for n in range(1,7)}
          | {(ref,n) for ref in ("U43","U44") for n in range(1,6)}
          | {("Q2",n) for n in range(1,4)}
          | {(ref,n) for ref in ("R69","R70","R71","R72","R73","R74","C42","C43","C44","C45") for n in (1,2)})
assert added==expected,(added^expected)
def net(r,p):return m[(r,p)]
assert net("U42",1)==net("U44",1)==net("R71",1)=="B93__PG_RAIL_STABLE_N_RESET"
assert net("U42",2)=="GND" and net("U42",3)==net("U42",6)=="3V3_AON"
assert net("U42",4)=="unconnected-(U42-CT-Pad4)"
assert net("U42",5)==net("R69",2)==net("R70",1)==net("C45",1)=="B93__PG_RAIL_DIV"
assert net("R69",1)==net("U28",4)=="B88__PG_AND_RAIL_OK"
assert net("R70",2)==net("C45",2)=="GND"
assert net("U43",1)==net("U12",5)=="B77__HB_TWO_EDGE_Q_ISOLATED"
assert net("U43",2)==net("U41",4)=="B92__RAIL_GRANT_LOGIC"
assert net("U43",4)==net("U44",2)=="B93__RUN_AND_START"
assert net("U44",4)==net("R72",1)=="B93__PHASE_GRANT_LOGIC"
assert net("R72",2)==net("R73",1)=="B93__PHASE_LIMIT_STAGE"
assert net("R73",2)==net("R74",1)==net("Q2",1)=="B93__PHASE_FET_GATE"
assert net("R74",2)==net("Q2",2)=="GND"
assert net("Q2",3)==net("U34",2)==net("R61",1)=="B90__OE_DISABLE_NOT_RELEASED"
assert net("R61",2)=="3V3_AON"
assert net("U34",4)=="B78__PHASE_OE_N_FIXED_HIGH"
for ref in ("U15","U16","U17","U18"):
 assert net(ref,1)==net(ref,19)==net("U34",4)
for ref,cap in (("U42","C42"),("U43","C43"),("U44","C44")):
 assert net(ref,2 if ref=="U42" else 3)==net(cap,2)=="GND"
 assert net(ref,6 if ref=="U42" else 5)==net(cap,1)=="3V3_AON"
assert net("U14",1)==net("R4",1)==net("R67",1)==net("R68",2)
assert net("R4",2)==net("R67",2)=="GND"
# Delay CT open ~20ms TYPICAL ONLY, cannot certify 20ms minimum.
threshold=.405*(1+60400/10000)
assert 2.8<threshold<2.9
# Worst 3.6V, remaining 68k -1%, 1k gate pulldown +1%
# if one inhibitor shorts: nominal Q2 Vgs << 0.4V 25C min threshold.
gate_max=3.6*1010/(68000*.99+1010)
assert gate_max<0.06,gate_max
for run,grant,pg,rail,cut in itertools.product((False,True),repeat=5):
    stable=pg and rail
    phase_req=run and grant and stable
    if not run or not grant or not pg or not rail:assert not phase_req
    # Physical Q2 gate does NOT follow phase_req as strong voltage;
    # 1k pull-down and 2x 68k inhibit actual U34.B.
    for aon_high in (False,True):
      if not aon_high:continue # unpowered gates undefined: HIL BLOCKER
      assert gate_max < .06
print(f"PASS 618 pads/182 symbols; real PG+independent rail -> supervisor -> RUN/START -> Q2 on OE line; max Q2 gate {gate_max:.4f}V at 3.6V")
if len(sys.argv)>1:
 o=Path(sys.argv[1]);root=ET.parse(o/"native.net.xml").getroot()
 found={}
 for n in root.findall("./nets/net"):
  for v in n.findall("node"):
   key=(v.attrib["ref"],int(v.attrib["pin"]))
   assert key not in found,key
   found[key]=n.attrib["name"].lstrip("/")
 assert found==m,[(k,v,found.get(k)) for k,v in m.items() if found.get(k)!=v][:20]
 assert len(found)==618 and len(root.findall("./components/comp"))==182
 erc=collections.Counter(x["type"] for sh in json.loads((o/"erc.json").read_text())["sheets"] for x in sh["violations"])
 assert not erc["endpoint_off_grid"] and not erc["lib_symbol_issues"],erc
 assert not erc["multiple_net_names"] and not erc["pin_conflict"],erc
 print("PASS REAL KiCad9 XML all 618 pads/182 symbols; nonwaived ERC findings:",dict(erc))
print("HOLD: 20ms CT OPEN is typical not guaranteed minimum; OE and EN physically inhibited; full AON/5V/STOP HIL unverified")
