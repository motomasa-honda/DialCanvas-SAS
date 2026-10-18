#!/usr/bin/env python3
"""G1-94 power source gap: match actual three unwaived power ERC blockers to KiCad terminals.
Do not mark any supply as fitted, measured or cleared.
"""
from pathlib import Path
import collections,json,sys
P=Path(__file__).resolve().parent
contract=json.loads((P/"power_source_blockers.json").read_text())
pins=json.loads((P/"pin_map_618_clean.json").read_text())
assert contract["status"]=="REVIEW_ONLY_NOT_MANUFACTURABLE"
assert len(pins)==618 and len({p["kicad_ref"] for p in pins})==182
assert len(contract["outstanding_supply_source_issues"])==3
actual={(p["kicad_ref"],int(p["source_pin"])):p["review_net"] for p in pins}
expected={("U14",5):"B77__5V_RAW",("U14",8):"GND",("U20",8):"3V3_AON"}
assert {(r["reference"],r["pin"]):r["net"] for r in contract["outstanding_supply_source_issues"]}==expected
for k,v in expected.items():assert actual[k]==v,(k,actual.get(k),v)
assert all(x["status"]=="OPEN" and x["acceptance"] and x["requirement"]
           for x in contract["outstanding_supply_source_issues"])
assert actual["U14",1]==actual["R4",1]==actual["R67",1]
assert actual["R4",2]==actual["R67",2]=="GND"
assert actual["R61",2]=="3V3_AON"
assert all(actual[x,1]==actual[x,19]==actual["U34",4]
           for x in ("U15","U16","U17","U18"))
assert contract["task_status"]=={"G1_05":"WORKING","G1_06":"WORKING","G1_07":"OPEN",
    "done_scope":20,"total":48,"manufacturer_gate_passed":0,"total_manufacturer_gates":6}
assert contract["physical_netlist_baseline"]["unresolved_erc_total"]==3
# Deliberate omission: never add PWR_FLAG for an unverified regulator or source.
if len(sys.argv)>1:
    out=Path(sys.argv[1])/"erc.json"
    violation=json.loads(out.read_text())
    errors=[v for sh in violation["sheets"] for v in sh["violations"]]
    counter=collections.Counter(e["type"] for e in errors)
    assert counter=={"power_pin_not_driven":3},counter
    assert len(errors)==3
print("PASS: three OPEN true power source/return ERC blockers mapped to physical U14.5/U14.8/U20.8, no fake power source")
print("HOLD: eFuse EN and 8/OE disabled; 20/48, 0/6 manufacturing; no hardware source or PCB release")
