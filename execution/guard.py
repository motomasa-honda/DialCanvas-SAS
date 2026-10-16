#!/usr/bin/env python3
"""Review-tracker consistency only. Does NOT prove electrical safety."""
import csv,json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent
def load(p):
    with (root/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
t=load("tasks.csv");w=load("m1_inspection_42.csv")
p=json.loads((root/"progress.json").read_text())
assert len(t)==48 and len({x["ID"] for x in t})==48
assert Counter(x["Gate"] for x in t)=={f"G{i}":8 for i in range(1,7)}
counts=Counter(x["Status"] for x in t)
assert counts=={
    "DONE_SCOPE":p["scoped_evidence_done"],
    "WORKING":p["working"],
    "OPEN":p["open"],
    "HARDWARE_WAIT":p["hardware_wait"]
},counts
assert sum(counts.values())==48 and counts["DONE_SCOPE"]>=19
assert p["task_total"]==48
for key,state in [("scoped_evidence_done","DONE_SCOPE"),("working","WORKING"),("open","OPEN"),("hardware_wait","HARDWARE_WAIT")]:
    assert p[key]==counts[state]
assert all(x["Evidence"] and x["Limit"] for x in t)
assert p["new_this_turn"] and all(
    next(x for x in t if x["ID"]==tid)["Status"]=="DONE_SCOPE"
    for tid in p["new_this_turn"]
)
assert next(x for x in t if x["ID"]=="G2-06")["Status"]=="DONE_SCOPE"
assert next(x for x in t if x["ID"]=="G4-02")["Status"]=="DONE_SCOPE"
assert next(x for x in t if x["ID"]=="G6-02")["Status"]=="DONE_SCOPE"
assert next(x for x in t if x["ID"]=="G6-03")["Status"]=="DONE_SCOPE"
assert next(x for x in t if x["ID"]=="G6-08")["Status"]=="OPEN"
assert next(x for x in t if x["ID"]=="G4-08")["Status"]=="OPEN"
assert p["manufacturer_release_closed"]==0 and p["manufacturer_release_total"]==6
assert p["software_evidence_passed"]==11 and p["software_evidence_total"]==14
assert len(w)==42 and len({x["branch_id"] for x in w})==42
assert Counter(x["axis"] for x in w)=={f"G{i}":6 for i in range(1,8)}
assert Counter(x["pin"] for x in w)=={str(i):7 for i in range(1,7)}
for x in w:
    n=int(x["pin"]);a=x["axis"]
    assert x["carrier_connector"]==f"J_M1_{a}"
    assert (x["module_physical_pin"],x["cut_length_mm"],x["inspection"])==("UNVERIFIED","TBD","NOT_TESTED")
    assert x["signal"]==(f"PH{n-1}" if n<5 else (f"{a}_COMMON_FUSED_5V" if n==5 else "GND"))
print(f"PASS: 48 frozen tasks; {counts['DONE_SCOPE']} scoped only / {counts['WORKING']} working / {counts['OPEN']} open / {counts['HARDWARE_WAIT']} hardware wait")
print("PASS: seven isolated modules, 42 traceable unmeasured terminals")
print("PASS: manufacturing release 0/6; review software 11/14; NO power enable")
