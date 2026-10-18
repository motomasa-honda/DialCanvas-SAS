#!/usr/bin/env python3
"""G1-94 power source gap: match actual three unwaived power ERC blockers to KiCad terminals.
Do not mark any supply as fitted, measured or cleared.
"""
from pathlib import Path
import collections,copy,json,re,sys
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
def check_erc_identity(errors, expected):
    """Block if the exact three original supply-pin errors move or disappear.

    Counting ERC error TYPES alone is insufficient: three errors on entirely
    different pins could otherwise pass. Compare real KiCad9 JSON descriptions
    to the source-to-sink pin contract, preserving error severity.
    """
    actual=[]
    assert len(errors)==len(expected),(len(errors),len(expected))
    for issue in errors:
        assert issue["type"]=="power_pin_not_driven",issue
        assert issue["severity"]=="error",issue
        assert issue["description"]=="Input Power pin not driven by any Output Power pins",issue
        assert len(issue["items"])==1,issue
        desc=issue["items"][0]["description"]
        match=re.fullmatch(
            r"Symbol\s+(U\d+)\s+Pin\s+(\d+)\s+\[[^\]]*Power input[^\]]*\]",
            desc,
        )
        assert match is not None,desc
        actual.append((match.group(1),int(match.group(2))))
    assert len(set(actual))==len(actual),("duplicate ERC findings",actual)
    assert set(actual)==set(expected),(actual,expected)
    return actual

if len(sys.argv)>1:
    out=Path(sys.argv[1])/"erc.json"
    violation=json.loads(out.read_text())
    errors=[v for sh in violation["sheets"] for v in sh["violations"]]
    expected_pins={(x["reference"],x["pin"]) for x in contract["outstanding_supply_source_issues"]}
    identified=check_erc_identity(errors,expected_pins)

    # Negatives retain THREE errors and therefore would defeat the old
    # count-only check. Prove exact-pin and severity checks reject them.
    for mutation in ("replaced_reference","duplicate_pin","downgraded_severity"):
        corrupt=copy.deepcopy(errors)
        if mutation=="replaced_reference":
            corrupt[0]["items"][0]["description"]=(
                corrupt[0]["items"][0]["description"].replace("Symbol U14 ","Symbol U99 ")
            )
        elif mutation=="duplicate_pin":
            corrupt[1]["items"][0]["description"]=corrupt[0]["items"][0]["description"]
        else:
            corrupt[2]["severity"]="warning"
        try:
            check_erc_identity(corrupt,expected_pins)
        except AssertionError:
            continue
        raise AssertionError("Expected fail-closed for ERC mutation: "+mutation)
    print("PASS exact real ERC identity and three negative mutations",sorted(identified))
print("PASS: three OPEN true power source/return ERC blockers mapped to physical U14.5/U14.8/U20.8, no fake power source")
print("HOLD: eFuse EN and 8/OE disabled; 20/48, 0/6 manufacturing; no hardware source or PCB release")
