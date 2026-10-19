#!/usr/bin/env python3
"""Independently compare genuine KiCad9 CLI XML against 374 original+added pads."""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
if len(sys.argv)!=2:raise SystemExit("Pass native output directory")
dir=Path(__file__).resolve().parent
p=json.loads((dir/"pin_map_374.json").read_text())
d=Path(sys.argv[1])
root=ET.parse(d/"review.net.xml").getroot()
out={}
for net in root.findall("./nets/net"):
    n=net.attrib["name"].lstrip("/")
    for node in net.findall("node"):
        k=(node.attrib["ref"],int(node.attrib["pin"]))
        assert k not in out,("duplicate KiCad endpoint",k)
        out[k]=n
expect={}
for x in p:
    k=(x["kicad_ref"],int(x["source_pin"]))
    assert k not in expect
    expect[k]=x["review_net"]
assert out==expect,("NATIVE MISMATCH",[(k,v,out.get(k)) for k,v in expect.items() if out.get(k)!=v][:20])
assert len(out)==374
assert len(root.findall("./components/comp"))==103
assert len(root.findall("./nets/net"))==104
erc=json.loads((d/"erc.json").read_text())
viols=[i for s in erc["sheets"] for i in s["violations"]]
tally=collections.Counter(v["type"] for v in viols)
assert tally["endpoint_off_grid"]==0,tally
assert tally["lib_symbol_issues"]==0,tally
import re
lock=json.loads((dir/"erc_open_register.json").read_text())
assert len(viols)==lock["expected_count"]==18
assert dict(tally)==lock["expected_error_types"],("new KiCad ERC finding class or count",tally)
labels=[]
power=[]
for i in viols:
    if i["type"]=="label_dangling":
        label_matches=re.findall(r"Label '([^']+)'",i["items"][0]["description"])
        assert len(label_matches)==1
        labels.append(label_matches[0])
    elif i["type"]=="power_pin_not_driven":
        match=re.fullmatch(r"Symbol (U\d+) Pin (\d+) \[([^,]+), Power input, Line\]",i["items"][0]["description"])
        assert match,i
        power.append(f"{match.group(1)}.{match.group(2)}:{match.group(3)}")
    else:
        raise AssertionError(("unreviewed ERC error",i))
assert sorted(labels)==lock["expected_label_nets"]
assert sorted(power)==lock["expected_power_inputs"]
assert lock["safety"]["manufacturing_closed"]==0 and not lock["safety"]["power_enabled"]
print("PASS: exact native ERC HOLD ledger, no unreviewed exceptions; 16 NC labels + 2 missing power drivers")

print("PASS genuine KiCad9 exported XML 374 physical pads /103 components /104 nets EXACT")
print("REAL KiCad ERC {} findings by category {}".format(len(viols),dict(tally)))
print("NO MANUFACTURING APPROVAL: all results candidate-only, board/M1 live tests missing.")
