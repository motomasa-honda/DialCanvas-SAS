#!/usr/bin/env python3
"""Source-pinned Phase72 pin contract and review-only boolean interlock checks.
NOT a KiCad ERC, silicon timing simulation or power enable circuit.
"""
import json, pathlib, itertools, csv, hashlib
root = pathlib.Path(__file__).resolve().parent
p = root / "vendor_contract.json"
data = json.loads(p.read_text())
expected = {
"U7": ("EN/UVLO","OVLO","PG","PGTH","IN","OUT","DVDT","GND","ILM","ITIMER"),
"U_WD": ("VDD","CWD","EN","GND","SET1","WDI","WDO","ENOUT"),
"U_EDGE": ("CLK","D","Q_N","GND","Q","CLR_N","PRE_N","VCC"),
"U_RUN": ("CLK","D","Q_N","GND","Q","CLR_N","PRE_N","VCC"),
"U_HB_INV": ("NC","A","GND","Y","VCC"),
"U_POR": ("RESET_N","GND","MR_N","CT","SENSE","VDD")}
assert set(data["parts"]) == set(expected)
for name,pins in expected.items():
    part=data["parts"][name]
    assert tuple(part["pins"])==pins, f"Vendor pad order changed: {name}"
    assert data["datasheets"][part["sku"]].startswith("https://www.ti.com/lit/ds/")
assert "FLT" not in data["parts"]["U7"]["pins"],"TPS259474 has PG/PGTH, NOT FLT"
w=data["watchdog"];s=data["safety_hold"];m=data["motor_modules"];e=data["evidence"]
assert (w["falling_edge_ms_min"],w["falling_edge_ms_typ"],w["falling_edge_ms_max"]) == (170,200,230)
assert (w["reset_ms_min"],w["reset_ms_max"]) == (170,230)
assert w["en_tied_to_3v3"] and w["set1_tied_to_3v3"],"Firmware must not disable watchdog"
assert w["cwd_resistor_ohm"]==10000 and 1000<=w["wdo_pullup_ohm"]<=100000
assert s["efuse_en_pulldown_ohm"]==10000 and s["efuse_drive_source"]=="NONE__REQUIRES_APPROVED_LATCH"
assert not s["arm_direct_efuse_en"]
assert s["real_second_edge_qualifier"]=="NOT_BUILT" and s["required_heartbeat_edges"]==2
assert s["five_volt_supervisor"]=="NOT_BUILT" and s["pg_startup_blank_fault_latch"]=="NOT_BUILT"
assert s["physical_rearm"]=="NOT_BUILT" and s["external_fault_to_gpio22"]=="NOT_BUILT"
assert m["selected_sku"]=="MTR-09-024" and m["listed_mm"]==[35,31]
assert m["other_sku"]=="MTR-09-004" and m["other_listed_mm"]==[40,20]
assert m["conservative_pre_measurement_envelope_mm"]==[40,31]
assert m["independent_axes"]==7 and m["independent_fuses"]==7
assert m["removal_test_envelope_mm"]==55 and not m["dimensions_measured"]
# PGTH divider is a calculated candidate, never proof that PG is a full FAULT output.
pg=data["pgth_candidate"]
assert (pg["top_ohm"],pg["bottom_ohm"],pg["pg_pullup_ohm"]) == (47000,17400,47000)
assert pg["tolerance_each"]==0.01
assert pg["pg_is_low_before_power_good"] and pg["pg_does_not_signal_all_transient_overcurrent"]
assert not pg["approved_for_board"]
assert pg["qualification"]=="CALCULATION_ONLY_PG_NOT_COMPREHENSIVE_FAULT_SIGNAL"
def vtrip(v,top,bottom):
    return v*(top+bottom)/bottom
typ_rise=vtrip(pg["pgth_rise_v"]["typ"],pg["top_ohm"],pg["bottom_ohm"])
typ_fall=vtrip(pg["pgth_fall_v"]["typ"],pg["top_ohm"],pg["bottom_ohm"])
assert abs(typ_rise-pg["calculated_rise_output_v"]["typ"])<1e-10
assert abs(typ_fall-pg["calculated_fall_output_v"]["typ"])<1e-10
assert 4.40<typ_rise<4.50 and 4.0<typ_fall<4.10
t=pg["tolerance_each"];top=pg["top_ohm"];bottom=pg["bottom_ohm"]
rise_min=vtrip(pg["pgth_rise_v"]["min"],top*(1-t),bottom*(1+t))
rise_max=vtrip(pg["pgth_rise_v"]["max"],top*(1+t),bottom*(1-t))
fall_min=vtrip(pg["pgth_fall_v"]["min"],top*(1-t),bottom*(1+t))
fall_max=vtrip(pg["pgth_fall_v"]["max"],top*(1+t),bottom*(1-t))
assert 4.30<rise_min<rise_max<4.61
assert 3.90<fall_min<fall_max<4.21
assert e["manufacturing_gates_closed"]==0 and e["software_evidence_closed"]==11
assert e["kicad_erc"]=="NOT_RUN" and e["pcb_drc"]=="NOT_RUN"
# 2^9 combinations times both initial trip states. Not an asserted physical implementation.
states=0
for vals in itertools.product((False,True), repeat=9):
    supply,supervisor,stop,wd,edges,arm,short,rearm,old_latched=vals
    bad=not(supply and supervisor and stop and wd and edges) or short
    latched=old_latched or bad
    if rearm and not arm and not bad: latched=False
    permit=not latched and not bad and arm
    assert not permit or supply and supervisor and stop and wd and edges and arm and not short
    assert not (permit and old_latched and arm)
    states+=1
assert states==512
# A real fail-closed power-up test must NOT inherit this abstract permitted state:
assert not data["release"] and data["safety_hold"]["efuse_drive_source"].startswith("NONE")
out=pathlib.Path("phase72-evidence");out.mkdir(exist_ok=True)
report={"status":"PASS_DATASHEET_PAD_STATIC_AND_512_ABSTRACT_STATES",
        "vendor_verified_part_instances":len(expected),
        "vendor_verified_pads":sum(map(len,expected.values())),
        "abstract_states":states,
        "pgth_rise_v_typ":round(typ_rise,4),"pgth_fall_v_typ":round(typ_fall,4),
        "pgth_rise_min_v":round(rise_min,4),"pgth_rise_max_v":round(rise_max,4),
        "pgth_fall_min_v":round(fall_min,4),"pgth_fall_max_v":round(fall_max,4),
        "physical_eFuse_power_enable":"INHIBITED",
        "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "manufacturing_gates_closed":0,"software_evidence_closed":11,
        "kicad_erc":"NOT_RUN","hardware_test":"NOT_RUN"}
(out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
