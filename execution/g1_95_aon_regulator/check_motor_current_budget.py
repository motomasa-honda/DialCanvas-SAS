#!/usr/bin/env python3
"""G1-05/G1-06 power evidence intake, sizing and HARD safety HOLD.

Replace the previous anti-progress invariant (all measurements must FOREVER be
null) with a provenance-gated intake. No synthetic example is ever saved as
physical measurement. Being review-ready cannot energize a motor.
"""
import dataclasses
import hashlib
import itertools
import json
import math
import re
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EVIDENCE=HERE/"motor_current_acceptance.json"
FIELDS={
    "motor_sku":"str",
    "motor_peak_phase_current_a":"positive",
    "actual_driver_max_simultaneous_phases":"phases",
    "efuse_min_current_limit_a":"positive",
    "controller_3v3_peak_a":"positive",
    "buck_min_efficiency":"efficiency",
    "five_volt_supply_sku":"str",
    "five_volt_supply_min_current_a":"positive",
    "board_measured_peak_input_a":"positive",
    "board_measured_peak_motor_a":"positive",
    "five_volt_raw_min_during_transient_v":"positive",
}
RESERVE=.20
TPS62933_VIN_MIN_V=3.8
TPS62933_OUTPUT_MAX_A=3.0

@dataclasses.dataclass(frozen=True)
class Budget:
    limit_typ_a:float
    total_phase_current_a:float
    reserve_target_a:float
    per_phase_typ_a:float
    per_phase_reserve_a:float
    status:str

def evaluate(max_axes:int,phases_per_axis:int,phase_current_a:float,
             r_ilm_ohm:float=2210.0,headroom_fraction:float=RESERVE)->Budget:
    assert 1<=max_axes<=7 and 1<=phases_per_axis<=4
    assert 0<r_ilm_ohm and 0<phase_current_a<10
    assert 0<=headroom_fraction<1
    typical=3334/r_ilm_ohm
    total=max_axes*phases_per_axis*phase_current_a
    reserved=typical*(1-headroom_fraction)
    verdict=("FAIL_VS_TYP" if total>=typical else
             "FAIL_DESIGN_HEADROOM" if total>=reserved else "CONDITIONAL_ONLY")
    return Budget(typical,total,reserved,typical/(max_axes*phases_per_axis),
                  reserved/(max_axes*phases_per_axis),verdict)

def input_current_requirement(motor_a:float,aon_output_a:float,
                              buck_efficiency:float,v_motor:float=5.0,
                              v_aon:float=3.3,v_input:float=5.0)->float:
    assert motor_a>=0 and aon_output_a>=0 and 0<buck_efficiency<=1
    assert v_motor>0 and v_aon>0 and v_input>0
    return motor_a*v_motor/v_input+v_aon*aon_output_a/(v_input*buck_efficiency)

def validate_value(k,v):
    t=FIELDS[k]
    if t=="str":
        assert isinstance(v,str) and v.strip() and v==v.strip(),(k,v)
    elif t=="phases":
        assert type(v) is int and 1<=v<=4,(k,v)
    else:
        assert type(v) in (int,float) and math.isfinite(v) and v>0,(k,v)
        if t=="efficiency":assert v<=1,(k,v)

def check_artifact(record,verify_files=True):
    assert set(record)=={"file","sha256","instrument_or_vendor","recorded_utc"},record
    path=record["file"]
    sha=record["sha256"]
    assert isinstance(path,str) and path.startswith("execution/evidence/") and ".." not in Path(path).parts,path
    assert re.fullmatch("[0-9a-f]{64}",sha),sha
    assert isinstance(record["instrument_or_vendor"],str) and len(record["instrument_or_vendor"].strip())>=3
    assert isinstance(record["recorded_utc"],str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ",record["recorded_utc"])
    if verify_files:
        p=ROOT/path
        assert p.resolve().is_relative_to(ROOT.resolve()),path
        assert p.is_file(),"Evidence artifact not committed: "+path
        assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,"Evidence SHA mismatch: "+path

def validate_evidence(d,verify_files=True):
    assert d["scope"]=="G1-05/G1-06 design HOLD, never manufacturing approval"
    assert d["hardware_release"] is False and d["manufacturer_release_gates_closed"]==0
    assert d["assumptions"]["motor_axes"]==7
    assert d["assumptions"]["simultaneous_phases_per_axis"] in (1,2,3,4)
    assert d["assumptions"]["headroom_target_fraction"]==RESERVE
    assert set(d["unverified_field_values"])==set(FIELDS)
    assert isinstance(d["evidence_provenance"],dict)
    assert isinstance(d["physical_test_results"],dict)
    assert len(d["physical_tests_required"])==6
    # These fields must equal the CALCULATED decision, not a forever-null
    # placeholder. A complete provenance-backed file can progress to review.
    decision=engineering_review_readiness(d)
    status=("READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE"
            if decision=="READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE"
            else "NOT_READY_FOR_ENGINEERING_REVIEW")
    assert d["output"]==decision,(d["output"],decision)
    assert d["acceptance_status"]==status,(d["acceptance_status"],status)
    for field,value in d["unverified_field_values"].items():
        evidence=d["evidence_provenance"].get(field)
        if value is None:
            assert evidence is None,"Value missing but orphan evidence supplied: "+field
        else:
            validate_value(field,value)
            assert isinstance(evidence,dict),"No provenance for "+field
            check_artifact(evidence,verify_files)
    assert set(d["evidence_provenance"])<=set(FIELDS)
    for test_id,result in d["physical_test_results"].items():
        assert re.fullmatch(r"[0-5]",test_id),test_id
        assert isinstance(result,dict) and set(result)=={"status","evidence"},result
        assert result["status"] in ("PASS","FAIL","UNTESTED")
        if result["status"]=="UNTESTED":
            assert result["evidence"] is None
        else:
            assert isinstance(result["evidence"],dict)
            check_artifact(result["evidence"],verify_files)

def engineering_review_readiness(d):
    """A COMPLETE file may be review-ready, but NEVER an electrical release."""
    z=d["unverified_field_values"]
    missing=[k for k,v in z.items() if v is None]
    if missing:return "HOLD_MISSING_MEASUREMENTS"
    if any(d["physical_test_results"].get(str(i),{}).get("status")!="PASS"
           for i in range(6)):return "HOLD_MISSING_PHYSICAL_TESTS"
    if z["five_volt_raw_min_during_transient_v"]<TPS62933_VIN_MIN_V:
        return "FAIL_BUCK_INPUT_UNDERVOLTAGE"
    # Peak samples may not be simultaneous.
    # Use conservative combined source sizing; confirm with HIL traces.
    # Use the guaranteed eFuse minimum, not the typical estimate.
    motor_bound=7*z["actual_driver_max_simultaneous_phases"]*z["motor_peak_phase_current_a"]
    if z["board_measured_peak_motor_a"]>motor_bound:
        motor_bound=z["board_measured_peak_motor_a"]
    if motor_bound>=z["efuse_min_current_limit_a"]*(1-RESERVE):
        return "FAIL_EFUSE_MINIMUM_WITH_HEADROOM"
    if z["controller_3v3_peak_a"]>=TPS62933_OUTPUT_MAX_A*(1-RESERVE):
        return "FAIL_BUCK_3V3_WITH_HEADROOM"
    theoretical=input_current_requirement(
        motor_bound,z["controller_3v3_peak_a"],z["buck_min_efficiency"],
        v_input=z["five_volt_raw_min_during_transient_v"])
    required=max(theoretical,z["board_measured_peak_input_a"])/(1-RESERVE)
    if required>=z["five_volt_supply_min_current_a"]:
        return "FAIL_5V_SOURCE_MINIMUM_WITH_HEADROOM"
    return "READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE"

class Contract(unittest.TestCase):
    def baseline(self):
        return json.loads(EVIDENCE.read_text(encoding="utf-8"))
    def test_blank_evidence_can_be_genuinely_filled_later(self):
        d=self.baseline()
        validate_evidence(d)
        self.assertEqual(engineering_review_readiness(d),"HOLD_MISSING_MEASUREMENTS")
        # In contrast to the old all-null permanent guard, future numeric
        # data with a valid evidence record is explicitly allowed.
        example=self.mock_complete(d)
        validate_evidence(example,verify_files=False)
        self.assertEqual(engineering_review_readiness(example),
                         "READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE")
        self.assertFalse(example["hardware_release"])

    def mock_complete(self,d):
        # Used IN MEMORY ONLY. Not a simulated real measurement artifact.
        z=d["unverified_field_values"]
        z.update(motor_sku="DEMO_ONLY_NOT_A_PRODUCT",
                 motor_peak_phase_current_a=.065,
                 actual_driver_max_simultaneous_phases=2,
                 efuse_min_current_limit_a=1.5,
                 controller_3v3_peak_a=.4,
                 buck_min_efficiency=.85,
                 five_volt_supply_sku="DEMO_ONLY_NOT_A_PRODUCT",
                 five_volt_supply_min_current_a=3.,
                 board_measured_peak_input_a=1.5,
                 board_measured_peak_motor_a=.92,
                 five_volt_raw_min_during_transient_v=4.7)
        provenance=dict(file="execution/evidence/EXAMPLE_NEVER_COMMITTED.csv",
             sha256="a"*64,instrument_or_vendor="TEST ONLY, NOT INSTRUMENT",
             recorded_utc="2026-10-18T00:00:00Z")
        d["evidence_provenance"]={k:provenance.copy() for k in z}
        d["physical_test_results"]={str(i):dict(status="PASS",evidence=provenance.copy()) for i in range(6)}
        d["output"]=engineering_review_readiness(d)
        d["acceptance_status"]="READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE"
        return d

    def test_missing_provenance_is_rejected(self):
        d=self.mock_complete(self.baseline())
        d["evidence_provenance"].pop("motor_sku")
        with self.assertRaises(AssertionError):validate_evidence(d,verify_files=False)
    def test_forbidden_uncommitted_file_is_rejected(self):
        d=self.mock_complete(self.baseline())
        with self.assertRaises(AssertionError):validate_evidence(d,verify_files=True)
    def test_tampered_or_broken_provenance_is_rejected(self):
        d=self.mock_complete(self.baseline())
        d["evidence_provenance"]["motor_sku"]["sha256"]="nothex"
        with self.assertRaises(AssertionError):validate_evidence(d,verify_files=False)
    def test_physical_failure_is_not_review_ready(self):
        d=self.mock_complete(self.baseline())
        d["physical_test_results"]["4"]["status"]="FAIL"
        d["output"]=engineering_review_readiness(d)
        d["acceptance_status"]="NOT_READY_FOR_ENGINEERING_REVIEW"
        validate_evidence(d,verify_files=False)
        self.assertEqual(d["output"],"HOLD_MISSING_PHYSICAL_TESTS")
    def test_voltage_brownout_is_rejected(self):
        d=self.mock_complete(self.baseline())
        d["unverified_field_values"]["five_volt_raw_min_during_transient_v"]=3.5
        self.assertEqual(engineering_review_readiness(d),"FAIL_BUCK_INPUT_UNDERVOLTAGE")
    def test_160ma_two_phase_motor_exceeds_efuse(self):
        d=self.mock_complete(self.baseline())
        d["unverified_field_values"]["motor_peak_phase_current_a"]=.160
        self.assertEqual(engineering_review_readiness(d),"FAIL_EFUSE_MINIMUM_WITH_HEADROOM")
    def test_underpowered_five_volt_adapter_is_rejected(self):
        d=self.mock_complete(self.baseline())
        d["unverified_field_values"]["five_volt_supply_min_current_a"]=1.8
        self.assertEqual(engineering_review_readiness(d),"FAIL_5V_SOURCE_MINIMUM_WITH_HEADROOM")
    def test_3v3_overload_is_rejected(self):
        d=self.mock_complete(self.baseline())
        d["unverified_field_values"]["controller_3v3_peak_a"]=2.5
        self.assertEqual(engineering_review_readiness(d),"FAIL_BUCK_3V3_WITH_HEADROOM")
    def test_margins_and_illustrative_current_equations(self):
        self.assertEqual(evaluate(7,2,.080).status,"CONDITIONAL_ONLY")
        self.assertEqual(evaluate(7,2,.100).status,"FAIL_DESIGN_HEADROOM")
        self.assertEqual(evaluate(7,2,.160).status,"FAIL_VS_TYP")
        self.assertTrue(2.27<input_current_requirement(1.5,1.,.85)<2.28)
    def test_never_auto_release(self):
        d=self.mock_complete(self.baseline())
        self.assertFalse(d["hardware_release"])
        self.assertEqual(d["manufacturer_release_gates_closed"],0)
        self.assertNotIn("RELEASE",engineering_review_readiness(d).replace("_NOT_POWER_RELEASE",""))
        self.assertEqual(d["output"],"READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE")
        self.assertEqual(d["acceptance_status"],"READY_FOR_ENGINEERING_REVIEW_NOT_POWER_RELEASE")

if __name__=="__main__":
    evidence=json.loads(EVIDENCE.read_text())
    validate_evidence(evidence)
    print("G1-05 live evidence decision:",engineering_review_readiness(evidence))
    print("HOLD: validated future measurements never automatically unlock motor EN/OE or manufacturing.")
    unittest.main(verbosity=2)
