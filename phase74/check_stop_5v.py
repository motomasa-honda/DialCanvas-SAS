#!/usr/bin/env python3
"""Phase74 GitHub static contract: pad mapping and fail-closed *model*, not circuit ERC."""
from pathlib import Path
import itertools,json,copy,hashlib

HERE=Path(__file__).resolve().parent
d=json.loads((HERE/"stop-5v-contract.json").read_text())
old=json.loads((HERE.parent/"phase73/connectivity.json").read_text())["nets"]
assert d["sku"]=="TPS3808G50DBVR"
assert d["threshold_nominal_volts"]==4.65
assert [d["pins"][str(i)] for i in range(1,7)]==["RESET_N","GND","MR_N","CT","SENSE","VDD"]
assert d["pin_nets"]=={"1":"QUAL_CLR_N","2":"GND","3":"STOP_NC_SENSE",
                       "4":"U_5V_CT_NC","5":"5V_RAW","6":"3V3_AON"}
assert d["stop_connector"]["shorted_3v3_detectable"] is False
assert d["physical_manual_rearm_latch"]=="NOT_BUILT"
assert d["pg_post_start_latch"]=="NOT_BUILT"
assert d["physical_driver_isolation"]=="NOT_BUILT"
assert d["power_en"]=="HELD_LOW" and d["manufacturing_gates_closed"]==0
assert d["software_evidence_closed"]==11 and d["kicad_erc"]=="NOT_RUN"

def audit(override=None):
    newer={k:list(v) for k,v in old.items()}
    ext={
      "QUAL_CLR_N":["U_5V.1","R_5V_RST_PU.1"],
      "GND":["U_5V.2","R_STOP_PD.2"],
      "STOP_NC_SENSE":["U_5V.3","J_STOP.2","R_STOP_PD.1"],
      "U_5V_CT_NC":["U_5V.4"],
      "5V_RAW":["U_5V.5"],
      "3V3_AON":["U_5V.6","J_STOP.1","R_5V_RST_PU.2"]
    }
    if override is not None:ext=override
    for k,v in ext.items():newer.setdefault(k,[]).extend(v)
    seen={}
    for net,points in newer.items():
        for p in points:
            assert p not in seen,("duplicate",p)
            seen[p]=net
    required={
      "U_5V.1":"QUAL_CLR_N","U_5V.2":"GND","U_5V.3":"STOP_NC_SENSE",
      "U_5V.4":"U_5V_CT_NC","U_5V.5":"5V_RAW","U_5V.6":"3V3_AON",
      "R_5V_RST_PU.1":"QUAL_CLR_N","R_5V_RST_PU.2":"3V3_AON",
      "J_STOP.1":"3V3_AON","J_STOP.2":"STOP_NC_SENSE",
      "R_STOP_PD.1":"STOP_NC_SENSE","R_STOP_PD.2":"GND",
      "U_POR.1":"QUAL_CLR_N","U_WD.7":"QUAL_CLR_N",
      "U_EDGE.6":"QUAL_CLR_N","U_RUN.6":"QUAL_CLR_N",
      "U7.1":"U7_EN_CLAMPED_DISABLED"
    }
    for point,net in required.items():assert seen.get(point)==net,(point,seen.get(point),net)
    assert len(seen)==71 and len(newer)==24,(len(seen),len(newer))
    assert seen["U7.1"]!=seen["U_5V.1"]
    return 71,24

audit()
mutations=0
for from_net, pad in [("QUAL_CLR_N","U_5V.1"),("STOP_NC_SENSE","U_5V.3"),
                       ("5V_RAW","U_5V.5"),("3V3_AON","U_5V.6"),
                       ("STOP_NC_SENSE","J_STOP.2"),("GND","R_STOP_PD.2"),
                       ("QUAL_CLR_N","R_5V_RST_PU.1"),("3V3_AON","J_STOP.1")]:
    x={"QUAL_CLR_N":["U_5V.1","R_5V_RST_PU.1"],"GND":["U_5V.2","R_STOP_PD.2"],
       "STOP_NC_SENSE":["U_5V.3","J_STOP.2","R_STOP_PD.1"],
       "U_5V_CT_NC":["U_5V.4"],"5V_RAW":["U_5V.5"],
       "3V3_AON":["U_5V.6","J_STOP.1","R_5V_RST_PU.2"]}
    x[from_net].remove(pad);x["BAD_NET_"+str(mutations)]=[pad]
    try:audit(x)
    except AssertionError:mutations+=1
    else:raise AssertionError("missed mutation: "+pad)
assert mutations==8

# Exhaustive abstract protocol invariant. These Boolean cases test a proposed
# policy ONLY; no corresponding hardware fault latch has been wired.
cases=0
for v33,v5,wdo,stop,edges,arm,manual,pg,already_tripped in itertools.product((False,True),repeat=9):
    healthy=v33 and v5 and wdo and stop and edges
    trip=already_tripped or not healthy
    rearm=manual and not arm and healthy
    if rearm:trip=False
    permit=bool(not trip and healthy and arm and pg)
    assert not permit or (healthy and pg and not trip)
    assert not (already_tripped and arm and permit)
    cases+=1
assert cases==512
out=HERE/"evidence";out.mkdir(exist_ok=True)
report={
 "result":"PASS_5V_STOP_STATIC_AND_ABSTRACT_MODEL",
 "terminals":71,"nets":24,"fault_mutations_rejected":mutations,
 "boolean_invariants":cases,
 "source_sha256":hashlib.sha256((HERE/"stop-5v-contract.json").read_bytes()).hexdigest(),
 "manufacturer":d["supplier_source"],"physical_manual_rearm_latch":"NOT_BUILT",
 "single_NC_contact_welded_short_detectable":False,
 "electrical_5V_sense_VDD3V3":"UNVERIFIED",
 "motor_U7_EN":"CLAMPED_LOW","physical_power_test":"NOT_RUN",
 "native_kicad_erc":"NOT_RUN","manufacturing_gates_closed":0,
 "software_evidence_closed":11}
(out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
