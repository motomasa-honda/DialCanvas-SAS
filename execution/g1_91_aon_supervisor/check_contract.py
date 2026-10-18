#!/usr/bin/env python3
"""Verify true AON-to-fault native KiCad pin routing, no manufacturing clearance."""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
old=json.loads((d.parent/"g1_90_fault_cutoff/pin_map_522.json").read_text())
new=json.loads((d/"pin_map_552.json").read_text())
a={(x["kicad_ref"],x["source_pin"]):x["review_net"] for x in old}
b={(x["kicad_ref"],x["source_pin"]):x["review_net"] for x in new}
assert len(a)==522 and len(b)==552
delta={k:(a[k],b[k]) for k in a if a[k]!=b[k]}
assert delta=={key:("B88__TRIP_COMBINED","B91__TRIP_ALL")
               for key in (("U20",5),("U23",1),("U32",2),("U35",2))}
assert set(b)-set(a)==({("U36",n) for n in range(1,7)}
 | {("U37",n) for n in range(1,6)}
 | {("U38",n) for n in range(1,6)}
 | {(r,n) for r in ("R63","R64","R65","C35","C36","C37","C38") for n in (1,2)})
assert len({x[0] for x in b})==159
def net(r,p):return b[(r,p)]
assert net("U36",1)==net("U37",2)==net("R65",1)=="B91__AON_GOOD_N_RESET"
assert net("U36",2)=="GND" and net("U36",3)==net("U36",6)=="3V3_AON"
assert net("U36",4)=="unconnected-(U36-CT-Pad4)"
assert net("U36",5)==net("R63",2)==net("R64",1)==net("C36",1)=="B91__AON_SENSE_DIV"
assert net("R63",1)==net("R65",2)=="3V3_AON"
assert net("R64",2)=="GND"
assert net("U37",1)=="unconnected-(U37-NC-Pad1)"
assert net("U37",3)=="GND" and net("U37",5)=="3V3_AON"
assert net("U37",4)==net("U38",2)=="B91__AON_BAD"
assert net("U38",1)==net("U31",4)=="B88__TRIP_COMBINED"
for ref,n in (("U20",5),("U23",1),("U32",2),("U35",2)):
 assert net(ref,n)==net("U38",4)=="B91__TRIP_ALL"
assert net("R4",2)=="GND" and net("R4",1)==net("U14",1)==net("Q1",3)
for ref in ("U15","U16","U17","U18"):
 assert net(ref,1)==net(ref,19)==net("U34",4)
lo=.405*.98*(1+60400*.99/(10000*1.01))
typ=.405*(1+60400/10000)
hi=.405*1.02*(1+60400*1.01/(10000*.99))
assert 2.7<lo<typ<hi<3.135,(lo,typ,hi)
for prior_trip in (False,True):
 for aon_bad in (False,True):
  all_trip=prior_trip or aon_bad
  if aon_bad:assert all_trip
  for latch_q in (False,True):
   physical_cut=latch_q or all_trip
   if aon_bad:assert physical_cut
print(f"PASS 552 physical pins/159 symbols; AON threshold {lo:.3f}/{typ:.3f}/{hi:.3f} V and 4 TRIP rewires")
if len(sys.argv)>1:
 out=Path(sys.argv[1]);root=ET.parse(out/"native.net.xml").getroot()
 got={}
 for n in root.findall("./nets/net"):
  for t in n.findall("node"):
   k=(t.attrib["ref"],int(t.attrib["pin"]))
   assert k not in got,k
   got[k]=n.attrib["name"].lstrip("/")
 assert got==b,[(k,v,got.get(k)) for k,v in b.items() if got.get(k)!=v][:24]
 assert len(got)==552 and len(root.findall("./components/comp"))==159
 counter=collections.Counter(x["type"] for sh in json.loads((out/"erc.json").read_text())["sheets"] for x in sh["violations"])
 assert not counter["endpoint_off_grid"] and not counter["lib_symbol_issues"],counter
 assert not counter["multiple_net_names"] and not counter["pin_conflict"],counter
 print("PASS native KiCad9 XML all 552 pins/159 symbols; real ERC (NO waiver):",dict(counter))
print("HOLD: AON VDD below POR makes supervisor RESET unknown; no independent powered driver, HIL, ERC/PCB qualification")
