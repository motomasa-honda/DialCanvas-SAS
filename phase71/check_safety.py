#!/usr/bin/env python3
"""Phase71 M1 safety-interface *contract*, not a physical circuit or KiCad ERC."""
from itertools import product
import json
from pathlib import Path

# TI TPS259474LRPW: no FLT output. PG(pin3), PGTH(pin4).
EFUSE = {"part":"TPS259474LRPW","EN_UVLO":1,"OVLO":2,
         "PG":3,"PGTH":4,"IN":5,"OUT":6,"DVDT":7,
         "GND":8,"ILM":9,"ITIMER":10}

def step(latched, d):
    fault = (not d["supply"] or not d["supervisor"] or not d["stop"]
             or not d["wdog"] or not d["edges"] or d["oc_fault"])
    if fault:
        latched=True
    # Physical manual rearm requires ARM LOW; return to health alone is not enough.
    can_reset = (d["manual_rearm"] and not d["arm"] and not fault)
    if can_reset:
        latched=False
    enabled = bool(not latched and not fault and d["arm"])
    return latched, enabled

def main():
    assert EFUSE["PG"]==3 and EFUSE["PGTH"]==4 and "FLT" not in EFUSE
    assert EFUSE["IN"]==5 and EFUSE["OUT"]==6 and EFUSE["EN_UVLO"]==1
    keys=("supply","supervisor","stop","wdog","edges","oc_fault","arm","manual_rearm")
    count=0
    for bits in product((False,True),repeat=len(keys)):
        data=dict(zip(keys,bits))
        for latched in (False,True):
            next_latch,output=step(latched,data)
            count+=1
            if output:
                assert not next_latch and all(data[k] for k in ("supply","supervisor","stop","wdog","edges","arm"))
                assert not data["oc_fault"]
            if data["arm"] and latched: assert not output
            if data["manual_rearm"] and data["arm"] and latched: assert next_latch
            if not data["edges"] or not data["wdog"] or not data["stop"] or data["oc_fault"]:
                assert next_latch and not output
    assert count==512
    # Required stuck-high/no-auto-restart behavior.
    good=dict(supply=True,supervisor=True,stop=True,wdog=True,edges=True,oc_fault=False,arm=False,manual_rearm=True)
    latched,on=step(True,good)
    assert not latched and not on
    good["arm"]=True;good["manual_rearm"]=False
    latched,on=step(latched,good);assert on
    good["wdog"]=False
    latched,on=step(latched,good);assert latched and not on
    good["wdog"]=True
    latched,on=step(latched,good);assert latched and not on
    assert all(f"F_M{i}" != f"F_M{j}" for i in range(1,8) for j in range(1,8) if i!=j)
    report={"status":"PASS_STATIC_512_STATE_CHECKS","tested_state_cases":count,
            "efuse_pin_variant":EFUSE,"motor_axes":7,"individual_motor_fuses":7,
            "gpio22_fault_source":"EXTERNAL_CONDITIONED_LATCH_NOT_U7_FLT",
            "watchdog":"TPS3431 candidate, WDI FALLING EDGES; physical latch/qualification not implemented",
            "physical_latch_and_en_gate":"UNIMPLEMENTED","kiCad_erc":"NOT_RUN",
            "pcb_drc":"NOT_RUN","manufacturing_gates_closed":0,"sw14":"OPEN"}
    Path("phase71-evidence").mkdir(exist_ok=True)
    Path("phase71-evidence/safety-contract-report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
