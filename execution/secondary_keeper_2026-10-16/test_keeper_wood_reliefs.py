#!/usr/bin/env python3
"""Unit tests for the source-bound keeper wood-relief geometry screen."""
import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("keeper_reliefs", HERE / "audit_keeper_wood_reliefs.py")
screen = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(screen)


def board_with_hole(hole=None):
    outer = [[0, 0], [300, 0], [300, 200], [0, 200], [0, 0]]
    rings = [outer]
    if hole:
        rings.append(hole)
    return {"solids": [{"id": "BACK_WOOD", "axis": "XY", "low": 137, "high": 145,
                       "geometry": {"type": "Polygon", "coordinates": rings}}]}


class KeeperWoodReliefTests(unittest.TestCase):
    def test_seven_seats_and_bores_fit_uninterrupted_source_board(self):
        result = screen.screen_reliefs(board_with_hole())
        self.assertTrue(result["all_seats_inside_original_wood"])
        self.assertTrue(result["all_bore_envelopes_are_full_wood_or_full_void"])
        self.assertEqual(len(result["axis_results"]), 7)
        self.assertTrue(all(not hits for hits in result["rear_driver_square_corridor_fixed_nonwood_intersections"].values()))

    def test_seat_clipping_existing_void_is_rejected(self):
        # A source opening crosses axis 5's seat box, so its intersection area
        # must be below the complete seat area and the seven-axis candidate fails.
        hole = [[160, 80], [166, 80], [166, 90], [160, 90], [160, 80]]
        result = screen.screen_reliefs(board_with_hole(hole))
        self.assertFalse(result["all_seats_inside_original_wood"])
        self.assertFalse(result["axis_results"]["5"]["seat_entirely_in_existing_wood"])

    def test_rectangle_boundary_distance_detects_clearance(self):
        ring = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
        self.assertAlmostEqual(screen.rect_boundary_distance((2, 4, 3, 5), [ring]), 2.0)


if __name__ == "__main__":
    unittest.main()
