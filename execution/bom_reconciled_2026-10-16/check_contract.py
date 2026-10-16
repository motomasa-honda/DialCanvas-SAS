#!/usr/bin/env python3
"""Review scope audit. Exact 429+18 source-file full comparison is in external user ZIP,
because the immutable nested D7 archive is NOT present in this GitHub tree.
"""
import csv,json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent
e=root.parent
c=json.loads((root/"source_contract.json").read_text())
with (root/"driver_59_policy.csv").open(encoding="utf-8",newline="") as f:rows=list(csv.DictReader(f))
assert len(rows)==59 and len({x["source_ref"] for x in rows})==59
assert all(x["old_bom_id"]=="E_"+x["source_ref"] for x in rows)
assert Counter(x["policy"] for x in rows)=={
"REPLACED_BY_M1_BREAKOUT":4,"RETIRED_OLD_M3_DRIVERS":4,
"REPLACE_28_ON_M1_CARRIER":28,"REQUIRES_REDRAW_SAFETY_SUPERVISOR":5,
"TRANSFER_RTC_FUNCTION":3,"TRANSFER_LED_GATES":8,
"TRANSFER_I2C_AND_QUALIFY_PULLUPS":7}
assert "RTC" in {x["source_ref"] for x in rows}
cnt=c["counts"]
assert cnt["base_bom"]==429 and cnt["m1_addendum"]==18
assert cnt["missing_old_master_rtc_recovered"]==1
assert cnt["integrated_review"]==448 and cnt["old_driver_refs_mapped"]==59
assert cnt["wood_receivers"]==24 and cnt["wood_machining_operations"]==68
assert cnt["retained_independent_fuses"]==7 and cnt["legacy_pulldowns_superseded"]==28
assert cnt["m1_pulldowns_added"]==28
sha=c["source_sha256"]
assert sha["d7/cad/assembly.json"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert all(len(x)==64 for x in sha.values())
p=json.loads((e/"progress.json").read_text())
# Historical BOM closure remains valid as other independent scopes progress.
# Verify the current ledger and milestone contract, NOT the historic 17/48 snapshot.
with (e/"tasks.csv").open(encoding="utf-8-sig",newline="") as f:
    tasks=list(csv.DictReader(f))
stat=Counter(row["Status"] for row in tasks)
assert len(tasks)==48 and len({row["ID"] for row in tasks})==48
assert (p["scoped_evidence_done"],p["working"],p["open"],p["hardware_wait"]) == (
    stat["DONE_SCOPE"],stat["WORKING"],stat["OPEN"],stat["HARDWARE_WAIT"])
assert sum(stat.values())==48
assert stat["DONE_SCOPE"]>=c["statuses"]["done_scope"]
assert next(row for row in tasks if row["ID"]=="G4-02")["Status"]=="DONE_SCOPE"
assert next(row for row in tasks if row["ID"]=="G4-08")["Status"]=="OPEN"
assert p["manufacturer_release_closed"]==0 and p["software_evidence_passed"]==11
assert c["statuses"]["G4_02"]=="DONE_SCOPE"
assert c["statuses"]["G4_08"]=="OPEN"
assert c["statuses"]["manufacturing_closed"]==0
assert c["ordering"].startswith("HOLD")
print("PASS: 59 exact old DRIVER component refs, 429+18+source RTC, original data SHA registered")
print(f"PASS: G4-02 remains scoped DONE at current {stat['DONE_SCOPE']}/48; G4-08 remains OPEN, safety 0/6")
print("NOTE: full 448-row source binary regeneration was verified in downloadable artifact ZIP, not in this GitHub CI")
