#!/usr/bin/env python3
import sys,json,collections,xml.etree.ElementTree as ET
from pathlib import Path
d=Path(sys.argv[1]);here=Path(__file__).resolve().parent
p=json.loads((here/"pin_map_404.json").read_text())
r=ET.parse(d/"native.net.xml").getroot()
actual={}
for net in r.findall("./nets/net"):
 for node in net.findall("node"):
  k=(node.attrib["ref"],int(node.attrib["pin"]))
  assert k not in actual;kname=net.attrib["name"].lstrip("/");actual[k]=kname
expect={(p["kicad_ref"],p["source_pin"]):p["review_net"] for p in p}
assert actual==expect,[(k,v,actual.get(k)) for k,v in expect.items() if actual.get(k)!=v][:15]
assert len(actual)==404 and len(r.findall("./components/comp"))==112 and len(r.findall("./nets/net"))==110
erc=json.loads((d/"erc.json").read_text());types=collections.Counter(v["type"] for s in erc["sheets"] for v in s["violations"])
assert not types["endpoint_off_grid"] and not types["lib_symbol_issues"],types
import re
lock=json.loads((here/"erc_open_register.json").read_text())
issues=[v for sheet in erc["sheets"] for v in sheet["violations"]]
assert len(issues)==lock["expected_count"]==19
assert dict(types)==lock["expected_types"],("unexpected ERC type / count",types)
dangling=[]
power=[]
for issue in issues:
 if issue["type"]=="label_dangling":
  m=re.findall(r"Label '([^']+)'",issue["items"][0]["description"])
  assert len(m)==1,issue
  dangling.append(m[0])
 elif issue["type"]=="power_pin_not_driven":
  m=re.fullmatch(r"Symbol (U\d+) Pin (\d+) \[([^,]+), Power input, Line\]",issue["items"][0]["description"])
  assert m,issue
  power.append(f"{m.group(1)}.{m.group(2)}:{m.group(3)}")
 else:
  raise AssertionError(("unreviewed native KiCad electrical problem",issue))
assert sorted(dangling)==lock["expected_label_nets"]
assert sorted(power)==lock["expected_power_inputs"]
assert lock["safety"]["manufacturing_closed"]==0
print("PASS: exact 19 native ERC issues counted and classified; NO hidden suppression")

print("PASS genuine KiCad9 XML 404 physical pads, 112 symbols and 110 nets EXACT")
print("HOLD actual native ERC findings",dict(sorted(types.items())))
