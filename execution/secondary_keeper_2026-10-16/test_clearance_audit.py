#!/usr/bin/env python3
"""Unit tests for axis-relative boss source-intersection geometry."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("audit_full_d7_clearance.py")
SPEC = importlib.util.spec_from_file_location("clearance_audit", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(audit)


def rectangular_xy(x0, x1, y0, y1, z0=134, z1=138):
    ring = [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]
    return {"id": "FIXTURE", "axis": "XY", "low": z0, "high": z1,
            "geometry": {"type": "Polygon", "coordinates": [ring]}}


class ClearanceAuditTests(unittest.TestCase):
    def test_empty_source_is_boss_volume_clear(self):
        result = audit.boss_intersections({"solids": []})
        self.assertEqual(set(result), {str(i) for i in range(1, 8)})
        self.assertTrue(all(not hits for hits in result.values()))

    def test_source_intersection_is_attributed_to_correct_axis(self):
        source = {"solids": [rectangular_xy(107, 108, 37, 38)]}
        result = audit.boss_intersections(source)
        self.assertEqual(len(result["1"]), 1)
        self.assertEqual(result["1"][0]["source_index"], 0)
        self.assertEqual(result["1"][0]["solid_id"], "FIXTURE")
        self.assertTrue(all(not result[str(i)] for i in range(2, 8)))
        self.assertAlmostEqual(result["1"][0]["overlap_volume_mm3"], 4.0)

    def test_duplicate_source_ids_remain_separately_identifiable(self):
        solid = rectangular_xy(107, 108, 37, 38)
        source = {"solids": [solid, {**solid}]}
        result = audit.boss_intersections(source)
        self.assertEqual([hit["source_index"] for hit in result["1"]], [0, 1])
        self.assertEqual([hit["solid_id"] for hit in result["1"]], ["FIXTURE", "FIXTURE"])
        self.assertEqual([hit["overlap_volume_mm3"] for hit in result["1"]], [4.0, 4.0])

    def test_stud_centerline_detects_solid_xy_material_and_respects_voids(self):
        # Axis 1 stud center is (108.15, 38.9). One XY layer contains it;
        # an otherwise identical layer has an inner-ring void there.
        outer = [[100, 30], [120, 30], [120, 50], [100, 50], [100, 30]]
        hole = [[107, 37], [110, 37], [110, 41], [107, 41], [107, 37]]
        source = {"solids": [
            {"id": "WOOD", "axis": "XY", "low": 137, "high": 139,
             "geometry": {"type": "Polygon", "coordinates": [outer]}},
            {"id": "OPENING", "axis": "XY", "low": 139, "high": 145,
             "geometry": {"type": "Polygon", "coordinates": [outer, hole]}},
        ]}
        hits = audit.stud_centerline_intersections(source)
        self.assertEqual(hits["1"], [{"source_index": 0, "solid_id": "WOOD", "z_overlap_mm": 2.0}])
        self.assertTrue(all(not items for axis, items in hits.items() if axis != "1"))

    def test_candidate_offsets_change_audited_envelope(self):
        source = {"solids": [rectangular_xy(107, 108, 37, 38)]}
        shifted = audit.boss_intersections(source, x_offset=(25, 28), y_offset=(0, 4),
                                           z_range=(134, 138))
        self.assertTrue(all(not hits for hits in shifted.values()))

    def test_degenerate_bounds_rejected(self):
        with self.assertRaises(ValueError):
            audit.boss_intersections({"solids": []}, x_offset=(24, 24))


if __name__ == "__main__":
    unittest.main()
