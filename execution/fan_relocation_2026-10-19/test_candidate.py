#!/usr/bin/env python3
"""Unit tests for fan-site rectangle clearance and source-derived geometry helpers."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"secondary_keeper_2026-10-16"))
from audit_candidate import boundary_distance, contains_point, rectangle_gap

class CandidateGeometryTests(unittest.TestCase):
    def setUp(self):
        self.rect=[[[0,0],[100,0],[100,100],[0,100],[0,0]]]
    def test_point_inside_and_boundary_margin(self):
        self.assertTrue(contains_point((50,50),[self.rect]))
        self.assertAlmostEqual(boundary_distance((50,50),self.rect),50)
        self.assertFalse(contains_point((101,50),[self.rect]))
    def test_rectangle_gap_uses_euclidean_corner_distance(self):
        self.assertEqual(rectangle_gap((0,10,0,10),(12,20,0,10)),2)
        self.assertAlmostEqual(rectangle_gap((0,10,0,10),(12,20,12,20)),2**0.5*2)
    def test_material_boundary_distance_detects_near_edge(self):
        self.assertAlmostEqual(boundary_distance((95,50),self.rect),5)

if __name__=="__main__":unittest.main()
