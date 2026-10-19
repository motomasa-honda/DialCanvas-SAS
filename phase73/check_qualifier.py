#!/usr/bin/env python3
"""Phase73 review-only manufacturer pad + dual-DFF contract. Never energize."""
import copy, hashlib, itertools, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"connectivity.json"
VENDOR=ROOT.parent/"phase72/vendor_contract.json"
RESISTORS=("R_EN_PD","R_WD_CWD","R_WDO_PU","R_POR_PU","R_PGTH_TOP","R_PGTH_BOT","R_PG_PU")

def audit(nets, vendor):
    pins={ref:{str(n) for n in range(1,len(part["pins"])+1)}
          for ref,part in vendor["parts"].items()}
    pins.update({r:{"1","2"} for r in RESISTORS})
    endpoints={}
    for label,entries in nets.items():
        assert entries,("empty",label)
        for entry in entries:
            ref,pin=entry.split(".")
            assert ref in pins and pin in pins[ref],("unknown",entry)
            assert entry not in endpoints,("duplicate",entry)
            endpoints[entry]=label
    assert len(endpoints)==sum(map(len,pins.values()))==59
    same=lambda *p:len({endpoints[x] for x in p})==1
    assert same("U_HB_INV.4","U_EDGE.1","U_RUN.1")  # same active edge clock
    assert same("U_WD.6","U_HB_INV.2")              # WDI original pulse
    assert same("U_EDGE.5","U_RUN.2")               # DFF1 Q->DFF2 D
    assert same("U_WD.7","U_POR.1","U_EDGE.6","U_RUN.6",
                "R_WDO_PU.1","R_POR_PU.1")         # open-drain reset and both CLEAR pins
    assert same("U_WD.1","U_WD.3","U_WD.5","U_EDGE.2","U_EDGE.7",
                "U_RUN.7","U_POR.3","R_WDO_PU.2","R_POR_PU.2") # no WDT bypass
    assert same("U7.1","R_EN_PD.1") and same("U7.8","R_EN_PD.2")
    assert nets[endpoints["U7.1"]]==["U7.1","R_EN_PD.1"] # EN remains unclimbable
    assert endpoints["U_RUN.5"] not in {endpoints["U7.1"],endpoints["U_EDGE.5"]}
    assert endpoints["U_POR.5"]==endpoints["U_POR.6"] # 3V3 only, not fake 5V
    assert vendor["parts"]["U_WD"]["pins"][6]=="WDO"
    assert vendor["parts"]["U_POR"]["pins"][0]=="RESET_N"
    assert vendor["parts"]["U_EDGE"]["pins"]==vendor["parts"]["U_RUN"]["pins"]
    assert vendor["parts"]["U7"]["sku"]=="TPS259474LRPW"
    assert "FLT" not in vendor["parts"]["U7"]["pins"]
    assert (vendor["parts"]["U7"]["pins"][2],vendor["parts"]["U7"]["pins"][3])==("PG","PGTH")
    return endpoints

class Shift2:
    def __init__(self): self.q1=self.q2=False
    def sample(self, edge=False, clear_n=True):
        if not clear_n:
            self.q1=self.q2=False
        elif edge:
            self.q1,self.q2=True,self.q1
        return self.q2

def transitions():
    total=0
    for vector in itertools.product((False,True),repeat=10):
        ff=Shift2()
        count=0
        for edge in vector:
            count+=int(edge)
            assert ff.sample(edge=edge)==(count>=2)
            total+=1
        assert not ff.sample(clear_n=False) and not ff.q1
        assert not ff.sample(clear_n=True) # WDO or POR returns high: no auto qualification
        assert not ff.sample(edge=True)
        assert ff.sample(edge=True)
    for q1,q2,edge,clear_n in itertools.product((False,True),repeat=4):
        ff=Shift2();ff.q1,ff.q2=q1,q2
        assert (ff.sample(edge,clear_n),ff.q1)==((False,False) if not clear_n else ((q1,True) if edge else (q2,q1)))
    return total

def main():
    contract=json.loads(SOURCE.read_text());vendor=json.loads(VENDOR.read_text())
    endpoints=audit(contract["nets"],vendor);vectors=transitions()
    r=contract["disposition"]
    assert contract["status"]=="REVIEW_ONLY_NO_MOTOR_ENABLE"
    assert r["number_of_heartbeat_edges"]==2 and r["gpio_heartbeat"]==28
    assert r["efuse_en_clamped_low"] and not r["mcu_arm_wire_to_efuse_en"]
    for k in ("stop_loop","manual_rearm_latch","five_volt_supervision","pg_fault_latch"):
        assert r[k]=="OPEN_NOT_IMPLEMENTED"
    assert r["kicad_erc"]=="NOT_RUN" and r["kicad_pcb_drc"]=="NOT_RUN"
    assert r["manufacturing_gates_closed"]==0 and r["software_evidence_closed"]==11
    mutations=[
      ("DFF2_CLK", "HB_FALL_EDGE_RISING","U_RUN.1"),
      ("DFF2_DATA","HB_EDGE1_Q","U_RUN.2"),
      ("DFF2_ASYNC_CLR","QUAL_CLR_N","U_RUN.6"),
      ("POR_ASYNC_CLR","QUAL_CLR_N","U_POR.1"),
      ("WDI_UNPLUGGED","GPIO28_HEARTBEAT","U_WD.6"),
      ("INVERTER_CLK_UNPLUGGED","HB_FALL_EDGE_RISING","U_HB_INV.4")
    ]
    for name,net,pad in mutations:
        bad=copy.deepcopy(contract["nets"]);bad[net].remove(pad)
        bad["MUTANT_"+name]=[pad]
        try:audit(bad,vendor)
        except AssertionError:pass
        else:raise AssertionError("Failed to reject "+name)
    result={"result":"PASS_LOGICAL_TWO_EDGE_REVIEW_ONLY","pins":len(endpoints),
            "nets":len(contract["nets"]),"vector_steps":vectors,
            "negative_mutations":len(mutations),
            "DFF2_Q_is_power_approval":False,"eFuse_EN":"HELD_LOW",
            "qualified_fault_latch":"NOT_IMPLEMENTED",
            "kicad_erc":"NOT_RUN","manufacturing_gates_closed":0,
            "software_evidence_closed":11,
            "input_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    out=ROOT/"evidence";out.mkdir(exist_ok=True)
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
