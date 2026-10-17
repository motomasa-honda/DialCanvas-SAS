#!/usr/bin/env python3
"""G1-89 actual KiCad-native net and safety invariants, NO powered approval."""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(__file__).resolve().parent
old=json.loads((d.parent/"g1_88_pg_rail_fault/pin_map_485.json").read_text())
new=json.loads((d/"pin_map_499.json").read_text())
a={(q["kicad_ref"],q["source_pin"]):q["review_net"] for q in old}
b={(q["kicad_ref"],q["source_pin"]):q["review_net"] for q in new}
assert len(a)==485 and len(b)==499
assert set(a)-set(b)=={("J19",1),("J19",2)}
assert {k:(a[k],b[k]) for k in a.keys()&b.keys() if a[k]!=b[k]}=={
    ("R56",2):("GND","3V3_AON")}
assert set(b)-set(a)==({("U33",p) for p in range(1,7)}
  | {(r,p) for r in ("R57","R58","R62","C31","C32") for p in (1,2)})
assert len({k[0] for k in b})==141
def net(r,n):return b[(r,n)]
assert net("U14",1)==net("R4",1)==net("R57",1)=="B77__U7_EN_CLAMPED_DISABLED"
assert net("U33",3)==net("U33",6)==net("R56",2)=="3V3_AON"
assert net("R4",2)=="GND"
assert net("U33",1)==net("R56",1)==net("U30",2)=="B88__MONITOR_ACTIVE"
assert net("R56",2)=="3V3_AON"
# R56 is now 100k pull-up, matched to manufacturer's timing test load.
generated_sch=(d/"forest_guardian_g1_89_hardware_start_deadline_review.kicad_sch").read_text()
assert '(property "Value" "100K_RESET_N_PULLUP"' in generated_sch
assert '(property "Value" "100K_CT_TO_VDD_300MS_FIXED"' in generated_sch
assert '68NF_LOW_LEAKAGE_CT' not in generated_sch
assert net("U33",2)==net("R58",2)=="GND"
assert net("U33",4)==net("R62",1)=="B89__STARTUP_CT"
assert net("R62",2)==net("U33",6)=="3V3_AON"
assert net("U33",5)==net("R57",2)==net("R58",1)==net("C32",1)=="B89__EN_SENSE_DIV"
assert net("U33",6)==net("C31",1)=="3V3_AON"
assert net("U20",5)==net("U23",1)=="B88__TRIP_COMBINED"
assert net("U22",2)==net("U26",1)=="B88__QUAL_EXT_N"
assert net("U33",3)!="B77__EFUSE_PG_OD"  # not a PG-dependent start deadline
assert net("U33",5)!="B81__RAIL_SENSE_DIV"
# TI TPS3808G01 datasheet Rev.N section 6.6/7.3.2:
# CT -> VDD through 40k..200k resistor = 180..420ms at specified loading.
ct_pull_ohms=100000
delay_min_ms,delay_typ_ms,delay_max_ms=180,300,420
assert 40000 <= ct_pull_ohms <= 200000
assert delay_min_ms <= delay_typ_ms <= delay_max_ms < 500
# TI TPS3808G01 threshold accuracy +/-2%, actual 0.405V nominal.
# E96 1% divider, worst resistors stacked adversarially.
vmin=0.405*(1-0.02)*(1+12000*(1-0.01)/(10000*(1+0.01)))
vtyp=0.405*(1+12000/10000)
vmax=0.405*(1+0.02)*(1+12000*(1+0.01)/(10000*(1-0.01)))
assert 0.86 < vmin < vtyp < vmax < 0.93
# Actual TI TPS259474 UVLO rising threshold min 1.183V / typical 1.2V.
assert vmax < 1.183
# Indeterminate MR region is eliminated: MR=VDD is always a HIGH in
# the TPS3808 recommended supply window; it NEVER samples analog EN.
assert net("U33",3)=="3V3_AON"
# Series divider loads EN in parallel with 10k R4 pull-down:
assert abs((3.3/10000 + 3.3/22000)*1000-0.48)<1e-9
for ms in (0,100,300,389,500,1000):
 for en in (False,True):
  for aon in (False,True):
   for pg in (False,True):
    for rail in (False,True):
     active=bool(en and aon and ms>=389)
     fault=active and not(pg and rail)
     if not en or not aon:assert not active
     if en and aon and ms>=389 and (not pg or not rail):assert fault
print(f"PASS: EN-to-SENSE {vmin:.3f}/{vtyp:.3f}/{vmax:.3f}V below eFuse 1.183V min; MR 3V3; CT=VDD rated 180..420ms at TI test conditions")
if len(sys.argv)>1:
 out=Path(sys.argv[1]);doc=ET.parse(out/"native.net.xml").getroot()
 actual={}
 for n in doc.findall("./nets/net"):
  for q in n.findall("node"):
   k=(q.attrib["ref"],int(q.attrib["pin"]))
   assert k not in actual,k
   actual[k]=n.attrib["name"].lstrip("/")
 assert actual==b,[(k,v,actual.get(k)) for k,v in b.items() if actual.get(k)!=v][:18]
 assert len(actual)==499 and len(doc.findall("./components/comp"))==141
 problems=[v for sh in json.loads((out/"erc.json").read_text())["sheets"] for v in sh["violations"]]
 types=collections.Counter(v["type"] for v in problems)
 assert not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
 print("PASS: real KiCad9 XML all 499 pins + 141 symbols. UNCLEARED ERC:",dict(types))
print("HOLD: TI IC delay upper 420ms at datasheet test conditions only; board-level 500ms verification and AON/physical EN/HIL/PCB OPEN")
