#!/usr/bin/env python3
"""TI TPS3808 DBV-6 candidate rail sense net review; never hardware approval."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXEC=HERE.parent
c=json.loads((HERE/"design_contract.json").read_text())
n=json.loads((HERE/"nets_16.json").read_text())["nets"]
prev77=json.loads((EXEC/"g1_phase77_140pins/nets_140.json").read_text())["nets"]
prev78=json.loads((EXEC/"g1_28phase_disabled/nets_208.json").read_text())["nets"]

def reverse(nets):
    seen={}
    for name,pads in nets.items():
        for pad in pads:
            assert pad not in seen,(pad,seen.get(pad),name)
            seen[pad]=name
    return seen

def check(candidate):
    p=reverse(candidate)
    assert len(candidate)==7 and len(p)==16
    assert {int(pin.split(".")[1]) for pin in p if pin.startswith("U_RAIL_SV.")}==set(range(1,7))
    groups=[
      ("U_RAIL_SV.6","R_RAIL_OK_PU.2","R_RAIL_MR_PU.2","C_RAIL_DEC.1"),
      ("U_RAIL_SV.2","R_RAIL_BOT.2","C_RAIL_DEC.2"),
      ("U_RAIL_SV.5","R_RAIL_TOP.2","R_RAIL_BOT.1"),
      ("U_RAIL_SV.1","R_RAIL_OK_PU.1"),
      ("U_RAIL_SV.3","R_RAIL_MR_PU.1"),
    ]
    for group in groups:
        assert len({p[k] for k in group})==1,group
    assert p["R_RAIL_TOP.1"]=="5V_MOTOR"
    assert p["U_RAIL_SV.4"]=="CT_OPEN_20MS_CANDIDATE"
    assert p["U_RAIL_SV.6"]=="3V3_AON" and p["U_RAIL_SV.2"]=="GND"
    assert p["R_RAIL_BOT.2"]=="GND"
    assert p["U_RAIL_SV.1"]=="RAIL_OK_N_SUPERVISOR"
    assert p["U_RAIL_SV.5"]=="RAIL_SENSE_DIV"
    assert not any("EFUSE_PG_OD"==name for name in candidate)
    return p

def trip_voltage(vit,rtop,rbot):
    assert vit>0 and rtop>0 and rbot>0
    return vit*(rtop+rbot)/rbot

p=check(n)
# Manufacturer package pin names, not an approved footprint/schematic.
assert c["device"]=="TPS3808G01DBVR"
assert c["pin_map"]=={"1":"RESET_OD_N","2":"GND","3":"MR_N","4":"CT","5":"SENSE","6":"VDD"}
r=c["resistor_candidate_ohms"]
assert all(r[k]==v for k,v in {
 "R_RAIL_TOP":100000,"R_RAIL_BOT":10000,
 "R_RAIL_OK_PU":10000,"R_RAIL_MR_PU":10000}.items())
assert abs(trip_voltage(0.405,100000,10000)-4.455)<1e-9
lo=trip_voltage(0.405,99000,10100)
hi=trip_voltage(0.405,101000,9900)
assert 4.37<lo<4.38 and 4.53<hi<4.54
# Inject individually moved pads and independently check failure.
for pad in (
    "U_RAIL_SV.1","U_RAIL_SV.2","U_RAIL_SV.3","U_RAIL_SV.4",
    "U_RAIL_SV.5","U_RAIL_SV.6","R_RAIL_TOP.1","R_RAIL_BOT.2",
    "R_RAIL_OK_PU.2","C_RAIL_DEC.1",
):
    bad={name:list(pads) for name,pads in n.items()}
    old=p[pad]
    bad[old].remove(pad)
    dst=next(name for name in bad if name != old)
    bad[dst].append(pad)
    try:
        check(bad)
    except AssertionError:
        continue
    raise AssertionError(f"failed to detect miswire {pad}")
assert set(prev77["U7_EN_CLAMPED_DISABLED"])=={"U7.1","R_EN_PD.1"}
assert "R_EN_PD.2" in prev77["GND"]
assert "U_ARM.5" in prev77["ARM_LATCH_Q_ISOLATED"]
assert "U7.3" in prev77["EFUSE_PG_OD"]
assert "U7.6" in prev77["5V_MOTOR"]
assert "U7.5" in prev77["5V_RAW"]
for i in range(1,5):
    assert all(f"U_BUF{i}.{pin}" in prev78["PHASE_OE_N_FIXED_HIGH"] for pin in (1,19))
assert (c["scope_done"],c["scope_total"],c["manufacturing_gates_closed"],c["software_evidence"])==(19,48,0,11)
assert c["efuse_enable"]=="UNCHANGED_10K_GND_ONLY"
assert c["outputs_28"]=="UNCHANGED_OE_FIXED_HIGH"
assert not any(c[x] for x in ("erc","pcb_drc","kicad_native","hardware_probed","footprint_approved"))
print(f"PASS: 16 candidate physical pads/7 isolated nets, TI DBV-6 pin mapping, 10 moved-pad injections")
print(f"Illustrative Vtrip @0.405V nominal: 4.455V (resistor-only 1% range {lo:.4f}..{hi:.4f}V; VIT tolerance excluded)")
print("HOLD: no EN/OE drive, no native KiCad, POR/analog/reverse-power/ERC/HIL not tested")
