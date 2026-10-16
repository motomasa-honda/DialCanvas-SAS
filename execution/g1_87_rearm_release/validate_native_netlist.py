#!/usr/bin/env python3
"""All pin numbers & nets validated against actual KiCad9 export, not simulated."""
from pathlib import Path
import collections,json,sys,xml.etree.ElementTree as ET
d=Path(__file__).resolve().parent;o=Path(sys.argv[1])
c=json.loads((d/"contract.json").read_text())
mapping=json.loads((d/"pin_map_446.json").read_text())
r=ET.parse(o/"native.net.xml").getroot()
actual={}
for net in r.findall("./nets/net"):
 for node in net.findall("node"):
  key=node.attrib["ref"],int(node.attrib["pin"])
  assert key not in actual,key
  actual[key]=net.attrib["name"].lstrip("/")
expect={(p["kicad_ref"],p["source_pin"]):p["review_net"] for p in mapping}
assert actual==expect,("KiCad real net mismatch",[(k,v,actual.get(k)) for k,v in expect.items() if actual.get(k)!=v][:20])
assert len(actual)==446 and len(r.findall("./components/comp"))==124
assert len(r.findall("./nets/net"))==119
issue=json.loads((o/"erc.json").read_text())
types=collections.Counter(v["type"] for sh in issue["sheets"] for v in sh["violations"])
assert not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
print("PASS: actual KiCad9 XML export 446 pads, 124 symbols, 119 nets same as source delta")
print("HOLD REAL ELECTRICAL ERC FINDINGS:",dict(sorted(types.items())))
