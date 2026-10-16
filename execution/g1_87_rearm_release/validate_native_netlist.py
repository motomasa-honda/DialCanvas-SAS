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
import re
ledger=json.loads((d/"erc_open_register.json").read_text())
issues=[v for sh in issue["sheets"] for v in sh["violations"]]
assert len(issues)==ledger["expected_count"]==19
assert dict(types)==ledger["expected_types"],("new or absent native ERC errors",types)
labs=[];powp=[]
for v in issues:
 if v["type"]=="label_dangling":
  m=re.findall(r"Label '([^']+)'",v["items"][0]["description"])
  assert len(m)==1,v
  labs.append(m[0])
 elif v["type"]=="power_pin_not_driven":
  m=re.fullmatch(r"Symbol (U\d+) Pin (\d+) \[([^,]+), Power input, Line\]",v["items"][0]["description"])
  assert m,v
  powp.append(f"{m.group(1)}.{m.group(2)}:{m.group(3)}")
 else:
  raise AssertionError(("Unexpected KiCad electrical error",v))
assert sorted(labs)==ledger["expected_label_nets"],("unreviewed NC labels",labs)
assert sorted(powp)==ledger["expected_power_inputs"],("unexpected power pin",powp)
assert ledger["motor_cutoff"]=="NONE"
print("PASS strict KiCad ERC ledger: 16 dangling labels + 3 undriven power pins; none suppressed")

print("PASS: actual KiCad9 XML export 446 pads, 124 symbols, 119 nets same as source delta")
print("HOLD REAL ELECTRICAL ERC FINDINGS:",dict(sorted(types.items())))
