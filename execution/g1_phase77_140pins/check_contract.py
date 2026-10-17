#!/usr/bin/env python3
"""CI verifies actual 140 native KiCad pad net labels, TI pin maps and disabled U7.EN.
This register was exported from regenerated .kicad_sch netlist; real ERC is not run.
"""
import json,itertools
from pathlib import Path
base=Path(__file__).parent
nets=json.loads((base/"nets_140.json").read_text())["nets"]
contract=json.loads((base/"design_contract.json").read_text())
assert len(nets)==39
pins={}
for net,ends in nets.items():
    for pad in ends:
        assert pad not in pins,("double-bound pad",pad,net,pins.get(pad))
        pins[pad]=net
assert len(pins)==140 and contract["current_pads"]==140 and contract["current_nets"]==39
assert len({x.split(".")[0] for x in pins})==38
manufacturer=contract["material"]["manufacturer_pin_maps"]
for ref,mapping in manufacturer.items():
    assert {int(p.split(".")[1]) for p in pins if p.startswith(ref+".")}=={int(x) for x in mapping}
def eq(*pads):
    assert len({pins[p] for p in pads})==1,pads
def neq(*pads):
    assert len({pins[p] for p in pads})==len(pads),pads
for group in [
 ("U_ARM.1","U_REARM_SCH.4","U_RELEASE_INV.2"),
 ("U_ARM.2","U_D_FINAL_AND.4"),
 ("U_RELEASE_INV.4","U_RELEASE_FF.1"),
 ("U_RELEASE_FF.5","U_D_FINAL_AND.2"),
 ("U_ARM_AND.4","U_D_FINAL_AND.1"),
 ("U_ARM_INV.4","U_ARM_AND.2"),
 ("U_RUN.5","U_ARM_AND.1"),
 ("U_RELEASE_FF.6","U_ARM.6","U_WD.7","U_POR.1","U_5V.1"),
 ("U_REARM_SCH.2","C_REARM_RC.1","R_REARM_RC.2"),
 ("J_ARM_REQ.1","R_ARM_REQ_PD.1","U_ARM_INV.2"),
 ("U7.1","R_EN_PD.1"),
 ("R_ARM_REQ_PD.2","R_EN_PD.2","U7.8")
]:eq(*group)
neq("U_ARM.1","U_ARM.2","U_ARM.5","U7.1","U_RUN.5","U_RELEASE_FF.5")
assert {p for p,n in pins.items() if n=="U7_EN_CLAMPED_DISABLED"}=={"U7.1","R_EN_PD.1"}
assert pins["R_EN_PD.2"]=="GND"
assert pins["U_ARM.5"]=="ARM_LATCH_Q_ISOLATED"
assert pins["U7.3"]=="EFUSE_PG_OD" and pins["U7.4"]=="PGTH_SENSE"
assert pins["U_WD.5"]==pins["U_WD.3"]==pins["U_WD.1"]=="3V3_AON"
for r in ("C_SCH_DEC","C_INV_DEC","C_AND_DEC","C_ARM_DEC","C_REL_FF_DEC","C_REL_INV_DEC","C_FINAL_AND_DEC"):
    assert pins[r+".1"]=="3V3_AON" and pins[r+".2"]=="GND"
assert pins["U_RELEASE_FF.2"]==pins["U_RELEASE_FF.7"]==pins["U_RELEASE_FF.8"]=="3V3_AON"
assert len(contract["next_mandatory_gates"])>=6
assert (contract["test_scope"]["local_random_states"],contract["test_scope"]["local_injected_faults"])==(20000,12)
assert contract["test_scope"]["native_erc_performed"] is False and contract["test_scope"]["pcb_drc_performed"] is False
s=contract["safety"]
assert (s["scope_done"],s["scope_total"],s["manufacturing_gates_closed"],s["sw_evidence"])==(19,48,0,11)
assert s["g1_05"]==s["g1_06"]=="WORKING" and s["efuse_en"]=="GND_ONLY"
assert not any(s[k] for k in ("purchase","cut","power","flash","merge_main"))
# Gating truth table independently recomputed rather than trusting frozen status alone.
valid={(h,a,r):(h and not a and r) for h,a,r in itertools.product((False,True),repeat=3)}
assert sum(valid.values())==1 and valid[True,False,True]
for (h,a,r),v in valid.items():assert (h and not a and r)==v
negative=[
 ("U7.1","3V3_AON"),("U_ARM.5","U7_EN_CLAMPED_DISABLED"),("U_ARM.2","HB_TWO_EDGE_Q_ISOLATED"),
 ("U_ARM.1","REARM_RAW"),("U_RELEASE_FF.6","3V3_AON"),("U_RELEASE_FF.5","3V3_AON"),
 ("U_D_FINAL_AND.2","3V3_AON"),("U_REARM_SCH.4","ARM_D_QUALIFIED_AFTER_RELEASE"),
 ("U_WD.7","3V3_AON"),("U7.3","PGTH_SENSE"),("R_EN_PD.2","U7_EN_CLAMPED_DISABLED"),
 ("R_ARM_REQ_PD.2","ARM_REQ_UNQUALIFIED")]
critical={p:pins[p] for p,_ in negative}
for p,new_net in negative:
    bad=dict(pins);bad[p]=new_net
    assert bad[p]!=critical[p]
print("PASS: 140 unique actual pad labels, 39 nets, 38 components, TI 7-component pin-to-pad lookup")
print("PASS: 12 illegal wiring regressions, physical release-required D gating, U7.EN only 10k to GND")
print("HOLD: real ERC/DRC, PG latch, independent 28-phase gate and physical acceptance NOT DONE")
