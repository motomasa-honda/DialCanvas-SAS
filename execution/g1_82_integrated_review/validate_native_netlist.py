#!/usr/bin/env python3
"""Compare real KiCad9 native XML export against all original 364-pad source nets."""
import collections
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

here=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit("Expected one native evidence directory")
out=Path(sys.argv[1])
mapping=json.loads((here/"pin_map_364.json").read_text())
assert len(mapping)==364
root=ET.parse(out/"review.net.xml").getroot()
actual={}
for net in root.findall("./nets/net"):
    name=net.attrib["name"].lstrip("/")
    for node in net.findall("node"):
        key=(node.attrib["ref"],int(node.attrib["pin"]))
        assert key not in actual,("duplicate native pin",key)
        actual[key]=name
expected={}
for item in mapping:
    key=(item["kicad_ref"],int(item["source_pin"]))
    assert key not in expected,("duplicate source pin",key)
    expected[key]=item["review_net"]
assert actual==expected,("Native pin/net mismatch",sum(actual.get(k)!=v for k,v in expected.items()))
assert len(root.findall("./components/comp"))==98
assert len(root.findall("./nets/net"))==104
assert len(actual)==364
erc=json.loads((out/"erc.json").read_text())
issues=[v for s in erc["sheets"] for v in s["violations"]]
tally=collections.Counter(v["type"] for v in issues)
assert tally.get("endpoint_off_grid",0)==0,tally
assert tally.get("lib_symbol_issues",0)==0,tally
print("PASS: Genuine KiCad9 XML nets EXACTLY match 98 components/104 nets/364 pins")
print("REAL ERC: {} findings by type: {}".format(len(issues),dict(sorted(tally.items()))))
if issues:print("HOLD: ERC violations remain; physical electrical safety is NOT approved")
