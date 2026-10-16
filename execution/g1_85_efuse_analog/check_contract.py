#!/usr/bin/env python3
"""G1-85 review only: exact 374-label constraints, manufacturer pin and analytic screens."""
import json, math, re
from pathlib import Path

root=Path(__file__).resolve().parent
c=json.loads((root/"design_contract.json").read_text())
mapping=json.loads((root/"pin_map_374.json").read_text())
schematic=(root/"forest_guardian_g1_85_analog_review.kicad_sch").read_text()
base=json.loads((root.parent/"g1_82_integrated_review/pin_map_364.json").read_text())
assert len(base)==364 and len(mapping)==374
assert mapping[:364]==base
assert len({(x["kicad_ref"],x["source_pin"]) for x in mapping})==374
assert c["sku"]=="TPS259474LRPW" and c["pins"]=={
"1":"EN/UVLO","2":"OVLO","3":"PG","4":"PGTH","5":"IN","6":"OUT",
"7":"dVdt","8":"GND","9":"ILM","10":"ITIMER"}
assert c["components"]==103 and c["recorded_pads"]==374
old=[x for x in mapping if x["group"]=="B77" and x["source_ref"]=="U7"]
assert len(old)==10 and next(x for x in old if x["source_pin"]==1)["review_net"]=="B77__U7_EN_CLAMPED_DISABLED"
assert next(x for x in old if x["source_pin"]==9)["review_net"]=="B77__REQUIRES_ILIM_R"
for comp in c["review_components"]:
    pads=[x for x in mapping if x["group"]=="B85" and x["source_ref"]==comp["name"]]
    assert len(pads)==2 and {x["source_pin"] for x in pads}=={1,2}
    assert [x["review_net"] for x in sorted(pads,key=lambda x:x["source_pin"])]==comp["nets"]
    for x in pads:
        label=f'(label "{x["review_net"]}" (at {x["wire_end_x"]} {x["wire_end_y"]} 0)'
        assert schematic.count(label)>=1,(x,label)
assert len(re.findall(r'\(label "',schematic))==374
assert len(re.findall(r'\(wire \(pts',schematic))==374
assert len(re.findall(r'\(property "FG_Source_Ref"',schematic))==103
assert schematic.count('(lib_id "FG_TI:TPS259474LRPW")')==1
s=c["settings"]
v_nom=s["ovlo_threshold_rising_v_typ"]*(1+s["r_ovlo_upper_ohm"]/s["r_ovlo_lower_ohm"])
v_low=s["ovlo_threshold_rising_v_min"]*(1+s["r_ovlo_upper_ohm"]*.99/(s["r_ovlo_lower_ohm"]*1.01))
v_high=s["ovlo_threshold_rising_v_max"]*(1+s["r_ovlo_upper_ohm"]*1.01/(s["r_ovlo_lower_ohm"]*.99))
assert math.isclose(v_nom,5.9) and 5.72<v_low<5.73 and 6.10<v_high<6.12
assert 1.50<3334/s["r_ilm_ohm"]<1.52
assert 8.2<5*s["dvdt_cap_pf"]/2000<8.3
assert 1.84<s["itimer_delta_v_typ"]*s["itimer_cap_nf"]/s["itimer_sink_current_ua_typ"]<1.86
assert c["enable_status"]=="GROUNDED_10K_NO_CHANGE" and c["phase_gate"]=="ALL_28_OE_PULLUP_DISABLED"
assert c["manufacturing_gates"]==0 and c["done_scope"]==19 and not any(c[k] for k in ("manufacturer_erc_pass","pcb_drc","motor_hil"))
print("PASS: 364 unmodified parent pad mappings + 10 connected TPS259474L analog candidate pads")
print("PASS: actual manufacturer U7 pin9=ILM and U7.EN=10k GND, buffer OE disabled")
print(f"SCREEN-only OVLO trip nominal {v_nom:.3f}V, worst simplified {v_low:.3f}..{v_high:.3f}V")
print("HOLD: no motor-load/COUT/thermal/current measurement, no physical board/standalone latch")
