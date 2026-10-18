#!/usr/bin/env python3
"""G1-95 power candidate calculation independent of physical measurement."""
import copy
import json
import math
import unittest
from pathlib import Path
from motor_feasibility import evaluate_report,size_candidate,CURRENT,SOURCE


class MotorFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current=json.loads(CURRENT.read_text())
        cls.source=json.loads(SOURCE.read_text())

    def test_real_review_baseline_refuses_hardware_release(self):
        result=evaluate_report(self.current,self.source)
        self.assertFalse(result["hardware_release"])
        self.assertEqual(result["manufacturer_release_gates_closed"],0)
        self.assertEqual(result["motor_identity_review"]["status"],
                         "HOLD_MOTOR_MODEL_AND_MANUFACTURER_UNIDENTIFIED")
        self.assertEqual(result["motor_identity_review"]["motor_part_sku"],None)
        self.assertFalse(result["motor_identity_review"]["candidate_is_selected"])
        self.assertEqual(result["driver_board_review"]["seller_skus"],
                         ["MTR-09-004","MTR-09-024"])
        self.assertFalse(result["seller_motor_listing_review"]["selected"])
        self.assertEqual(result["seller_motor_listing_review"]["listed_voltage_values_v"],[5,12])
        self.assertEqual(result["seller_motor_listing_review"]["listed_dc_resistance_ohm_values"],[50,200])
        candidate=result["audited_manufacturer_motor_candidate"]
        self.assertEqual(candidate["exact_order_code"],"PKP223U09A2")
        self.assertEqual(candidate["listed_leads"],6)
        self.assertAlmostEqual(candidate["listed_winding_current_a_per_phase"],.95)
        self.assertEqual(candidate["seven_axes_two_phases_theoretical_current_a"],13.3)
        self.assertEqual(candidate["status"],"REJECTED_FOR_CURRENT_M1_DRIVER_AND_POWER_ENVELOPE")
        self.assertFalse(candidate["selected"])
        self.assertEqual(candidate["gearhead"],"NONE")
        supplier=result["conditional_supplier_motor_candidate"]
        self.assertEqual(supplier["supplier_product_id"],"858")
        self.assertEqual(supplier["listed_connection"],"5-pin unipolar")
        self.assertEqual(supplier["listed_reduction_ratio"],16.128)
        self.assertEqual(supplier["listed_steps_per_output_revolution"],516)
        self.assertEqual(supplier["listed_envelope_mm"],
                         {"diameter":28,"body_height":20,"shaft_length":9,"shaft_diameter":5})
        self.assertAlmostEqual(supplier["seven_axis_one_phase_ohmic_current_estimate_a"],.833333)
        self.assertAlmostEqual(supplier["seven_axis_two_phase_ohmic_current_estimate_a"],1.666667)
        self.assertFalse(supplier["selected_for_production"])
        self.assertFalse(supplier["hardware_release"])
        self.assertIn("OEM_MANUFACTURER_NOT_IDENTIFIED",supplier["source_class"])
        self.assertEqual(len(result["hypothetical_combinations"]),16)
        self.assertEqual(len(result["current_model"]["physical_evidence_missing_fields"]),11)
        self.assertFalse(result["current_model"]["rated_efuse_min_available"])

    def test_two_phase_nominal_threshold_already_insufficient_for_100ma(self):
        typical=3334/2210
        eighty=size_candidate(80,2,typical)
        hundred=size_candidate(100,2,typical)
        self.assertEqual(eighty["verdict"],"HOLD_MANUFACTURER_MIN_UNVERIFIED")
        self.assertEqual(hundred["verdict"],"FAIL_NOMINAL_20PCT_MARGIN")
        self.assertAlmostEqual(eighty["manufacturer_efuse_min_required_a_exclusive"],1.4)
        self.assertLess(eighty["max_phase_ma_from_typical_only_not_approved"],87)
        self.assertGreater(eighty["max_phase_ma_from_typical_only_not_approved"],86)

    def test_higher_phase_assumption_rejected_when_current_exceeds_typical(self):
        typical=3334/2210
        cases=[size_candidate(160,n,typical) for n in (1,2,3,4)]
        self.assertEqual(cases[1]["verdict"],"FAIL_EVEN_TYPICAL_EFUSE")
        self.assertEqual(cases[2]["verdict"],"FAIL_EVEN_TYPICAL_EFUSE")
        self.assertEqual(cases[3]["verdict"],"FAIL_EVEN_TYPICAL_EFUSE")

    def test_optional_guaranteed_min_is_only_a_conditional_review(self):
        typ=3334/2210
        self.assertEqual(size_candidate(60,2,typ,1.5)["verdict"],
                         "CONDITIONAL_REQUIRES_PROVENANCE_AND_PHYSICAL_HIL")
        self.assertFalse(size_candidate(60,2,typ,1.5)["hardware_release"])
        self.assertEqual(size_candidate(80,2,typ,1.3)["verdict"],
                         "FAIL_GUARANTEED_MIN_LIMIT_MARGIN")

    def test_invalid_and_nonfinite_inputs_rejected(self):
        for current in (0,-1,float("nan"),float("inf"),True):
            with self.assertRaises(ValueError):size_candidate(current,2,1.5)
        for phases in (0,5,1.0,True):
            with self.assertRaises(ValueError):size_candidate(60,phases,1.5)

    def test_vendor_reference_change_fails_closed(self):
        src=copy.deepcopy(self.source)
        src["stepper_driver_boards"]["selected_candidate_sku"]="UNKNOWN"
        with self.assertRaises(ValueError):evaluate_report(self.current,src)

    def test_conflicting_motor_variant_is_never_selected(self):
        src=copy.deepcopy(self.source)
        src["stepper_driver_boards"]["separate_seller_motor_listing"]["selected"]=True
        with self.assertRaises(ValueError):evaluate_report(self.current,src)

    def test_release_cannot_be_set_by_matrix_generation(self):
        data=copy.deepcopy(self.current)
        data["hardware_release"]=True
        with self.assertRaises(AssertionError):evaluate_report(data,self.source)
        self.assertFalse(self.current["hardware_release"])


if __name__=="__main__":
    unittest.main(verbosity=2)
