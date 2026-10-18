#!/usr/bin/env python3
"""G1-95 strict source circuit and motor hard-off; no false ERC clearance."""
import json,sys,collections,xml.etree.ElementTree as ET
from pathlib import Path
D=Path(__file__).resolve().parent
orig=json.loads((D.parent/"g1_94_native_erc_cleanup/pin_map_618_clean.json").read_text())
rows=json.loads((D/"pin_map_648.json").read_text())
assert len(orig)==618 and len(rows)==648 and rows[:618]==orig
m={(z["kicad_ref"],z["source_pin"]):z["review_net"] for z in rows}
assert len(m)==648 and len({r for r,_ in m})==194
expected=({("U45",i) for i in range(1,9)}
 | {("J20",i) for i in (1,2)}
 | {(ref,i) for ref in ("L1","R76","R77","C46","C47","C48","C49","C50","C51","C52") for i in (1,2)})
assert set(m)-{(x["kicad_ref"],x["source_pin"]) for x in orig}==expected
def net(r,n):return m[r,n]
assert net("U45",1)=="unconnected-(U45-RT-Pad1)"
assert net("U45",2)==net("U45",3)==net("J20",1)==net("U14",5)=="B77__5V_RAW"
# Independent always-on rail regression guard: controller buck input MUST be
# upstream of the switched motor eFuse, not back-powered by motor 5V_MOTOR.
# Preserve physical isolation even when other 5V labels evolve later.
assert net("U45",3)!=net("U14",6)== "5V_MOTOR"
assert net("U45",4)==net("J20",2)=="GND"
assert net("U45",8)!="5V_MOTOR"
# Cross-stage physical power-domain invariant:
# G1-89/G1-91/G1-93 supervisors and the NOR fault latch MUST derive
# their VDD from the independent always-on buck output, not eFuse VOUT.
# A superficial test only on U45 input does not catch a later downstream
# rewire silently returning fault logic to switched 5V_MOTOR.
assert net("U14",6)=="5V_MOTOR"
assert net("U45",2)==net("U45",3)==net("U14",5)=="B77__5V_RAW"
for ref,pin in (("U20",8),("U33",6),("U36",6),("U42",6),("U43",5)):
 assert net(ref,pin)==net("L1",2)=="3V3_AON",(ref,pin,net(ref,pin))
assert net("U14",6)!=net("L1",2)
assert net("U14",6)!=net("J20",1)

assert net("U45",4)==net("J20",2)==net("R4",2)=="GND"
assert net("U45",5)==net("L1",1)==net("C50",2)=="B95__BUCK_SW"
assert net("U45",6)==net("C50",1)=="B95__BUCK_BST"
assert net("U45",7)==net("C51",1)=="B95__BUCK_SS"
assert net("U45",8)==net("R76",2)==net("R77",1)=="B95__BUCK_FB"
assert net("L1",2)==net("R76",1)==net("C48",1)==net("C49",1)==net("U20",8)=="3V3_AON"
assert net("R77",2)==net("C48",2)==net("C49",2)=="GND"
assert net("C46",1)==net("C47",1)==net("C52",1)=="B77__5V_RAW"
assert net("C46",2)==net("C47",2)==net("C52",2)=="GND"
assert net("C51",2)=="GND"
assert net("U14",1)==net("R4",1)==net("R67",1)==net("R68",2)
assert net("R4",2)==net("R67",2)=="GND"
assert net("R61",2)=="3V3_AON"
for buf in ("U15","U16","U17","U18"):
 assert net(buf,1)==net(buf,19)==net("U34",4)=="B78__PHASE_OE_N_FIXED_HIGH"
sym=(D/"FG_POWER.kicad_sym").read_text()
for n,name in enumerate(("RT","EN","VIN","GND","SW","BST","SS","FB"),1):
 assert '(name "'+name+'"' in sym and '(number "'+str(n)+'"' in sym
assert '(pin power_in line' in sym and '(pin power_out line' in sym
assert "PWR_FLAG" not in sym and "PWR_FLAG" not in (D/"forest_guardian_g1_95_aon_regulator_review.kicad_sch").read_text()
# TI 0.8V FB typical; 31.2k/10k E96 resistors yield 3.296V.
assert abs(0.8*(1+31200/10000)-3.296)<1e-12
# Crucial adverse scenario: motor eFuse current-limiting cannot be
# accepted from motor count alone. Existing TI RILM 2.21k gives typical
# 3334 / 2210 = 1.509 A. CONDITIONAL examples, NOT actual motor BOM.
provisional_limit=3334/2210
per_phase_one=provisional_limit/(7*2)
assert 0.10 < per_phase_one < 0.11
assert 7*2*.160>provisional_limit
# 3.3V regulator is upstream of the motor eFuse but adds load to 5V input.
print("PASS: genuine pins U45 1..8, upstream 5V input+return J20, 3V3 buck passives; 648/194; eFuse EN+OE OFF")
print(f"HOLD: R_ILM 2.21k sets motor current limit ~{provisional_limit:.3f}A typical; 7x2-phase threshold {per_phase_one*1000:.1f}mA/phase before headroom; actual motor peak UNKNOWN")
if len(sys.argv)>1:
 o=Path(sys.argv[1]);root=ET.parse(o/"native.net.xml").getroot()
 actual={}
 for n in root.findall("./nets/net"):
  for p in n.findall("node"):
   k=p.attrib["ref"],int(p.attrib["pin"])
   assert k not in actual,k
   actual[k]=n.attrib["name"].lstrip("/")
 assert actual==m,[(k,v,actual.get(k)) for k,v in m.items() if actual.get(k)!=v][:24]
 assert len(actual)==648 and len(root.findall("./components/comp"))==194
 issues=[z for sh in json.loads((o/"erc.json").read_text())["sheets"] for z in sh["violations"]]
 types=collections.Counter(z["type"] for z in issues)
 assert not types["label_dangling"] and not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
 assert not types["multiple_net_names"] and not types["pin_conflict"],types
 assert types["power_pin_not_driven"]>=3,types
 print("PASS real KiCad9 netlist 648/194; real ERC (not waived, power sources OPEN):",dict(types))
print("HOLD: product circuit full G1-05/06 WORKING, no real power source, supply current measurement, footprints/PCB/HIL")
