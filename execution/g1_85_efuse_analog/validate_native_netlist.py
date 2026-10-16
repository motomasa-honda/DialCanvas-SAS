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
print("PASS genuine KiCad9 exported XML 374 physical pads /103 components /104 nets EXACT")
print("REAL KiCad ERC {} findings by category {}".format(len(viols),dict(tally)))
print("NO MANUFACTURING APPROVAL: all results candidate-only, board/M1 live tests missing.")
