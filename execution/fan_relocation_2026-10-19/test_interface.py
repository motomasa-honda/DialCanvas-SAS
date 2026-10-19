import unittest
import check_interface

class FanInterfaceContractTests(unittest.TestCase):
    def test_current_interface_contract(self):
        check_interface.check()

    def test_fan_mount_pattern_is_not_fabrication_released(self):
        candidate = check_interface.DATA["candidate_integration"]
        self.assertEqual(candidate["wood_adapter_support_count"], 4)
        self.assertIsNone(candidate["fan_mount_hole_centers"])

    def test_nominal_matching_diameters_are_not_clearance(self):
        candidate = check_interface.DATA["candidate_integration"]
        self.assertEqual(candidate["nominal_port_to_fan_inlet_diameter_difference_mm"], 0)
        self.assertIsNone(candidate["wood_port_tolerance_mm"])

if __name__ == "__main__":
    unittest.main()
