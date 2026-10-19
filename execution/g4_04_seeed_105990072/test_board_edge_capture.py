#!/usr/bin/env python3
"""Regression checks that PCB edge-window screening rejects source-feature overlap."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("edge_capture", HERE / "check_board_edge_capture.py")
edge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edge)

features = [{"ref": "TEST", "kind": "copper", "bbox": [9.0, 19.25, 9.2, 19.45]}]
assert edge.find_hits(features), "feature inside 0.30 mm expanded lip window was not rejected"
clear = [{"ref": "TEST", "kind": "copper", "bbox": [9.0, 19.61, 9.2, 19.81]}]
assert not edge.find_hits(clear), "feature outside 0.30 mm expanded lip window was rejected"
print("PASS: edge-window screen rejects overlap and honors 0.30 mm clearance boundary")
