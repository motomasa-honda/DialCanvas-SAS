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
import re
register=json.loads((here/"erc_open_register.json").read_text())
assert register["count"]==20
expected_erc=set(register["tracked_label_nets"])
actual_erc=set()
for issue in issues:
    assert issue["type"]=="label_dangling",("unexpected ERC class",issue["type"])
    assert issue["severity"]=="error"
    matches=re.findall(r"Label '([^']+)'",issue["items"][0]["description"])
    assert len(matches)==1,issue
    assert matches[0] not in actual_erc,("duplicate ERC issue",matches[0])
    actual_erc.add(matches[0])
assert len(issues)==20,("ERC issue count changed; update blocker status deliberately",len(issues))
assert actual_erc==expected_erc,("ERC unresolved issue changed",actual_erc^expected_erc)
assert set(register["statuses"]["real_efuse_analog_design_blockers"])=={
    "B77__REQUIRES_OVLO_PARTS","B77__REQUIRES_DVDT_DESIGN",
    "B77__REQUIRES_ILIM_R","B77__REQUIRES_ITIMER_C"
}
assert register["release"]["efuse_en"]=="GND_ONLY"
assert register["release"]["manufacturing_gates_closed"]==0

print("PASS: Genuine KiCad9 XML nets EXACTLY match 98 components/104 nets/364 pins")
print("REAL ERC: {} findings by type: {}".format(len(issues),dict(sorted(tally.items()))))
if issues:print("HOLD: ERC violations remain; physical electrical safety is NOT approved")
