#!/usr/bin/env python3
"""Build a real, editable SVG review overlay for seven serviceable axes."""
import json
from pathlib import Path
from xml.etree import ElementTree as ET
root = Path(__file__).resolve().parent
layout = json.loads((root/"cassettes/seven_axis_conditional_layout.json").read_text())
branches = json.loads((root/"g6_06_build_service_sequence/branch_register_42.json").read_text())
assert len(layout["slots"]) == 7 and len(branches) == 42
assert layout["axial_retraction_mm"] == 55
assert all(b["physical_pin"] == "UNVERIFIED" and b["cut_length"] == "TBD" for b in branches)
ns="http://www.w3.org/2000/svg"
ET.register_namespace("", ns)
def node(parent, tag, **attrs): return ET.SubElement(parent, "{"+ns+"}"+tag, {k.replace("_","-"):str(v) for k,v in attrs.items()})
svg=ET.Element("{"+ns+"}svg", {"width":"270mm","height":"190mm","viewBox":"0 0 270 190"})
node(svg,"rect",x=0,y=0,width=270,height=190,fill="white",stroke="black",stroke_width=".5")
centers=node(svg,"g",id="axis_centers")
service=node(svg,"g",id="service_envelopes_candidate")
labels=node(svg,"g",id="logical_connectors")
for s in layout["slots"]:
    axis="G"+str(s["axis"]); x=s["x"]; y=s["y"]
    six=[b for b in branches if b["axis"]==axis]
    assert sorted(b["pin"] for b in six)==list(range(1,7))
    node(service,"rect",x=x-25,y=y-20.5,width=50,height=41,fill="none",stroke="#777",stroke_dasharray="2 1",stroke_width=".5")
    node(centers,"circle",cx=x,cy=y,r=1.6,fill="#111")
    t=node(labels,"text",x=x+3,y=y-2,font_size=4); t.text=axis+" / J_M1_"+axis
    t=node(labels,"text",x=x+3,y=y+3,font_size=2.8); t.text="1-4 PH0-3; 5 5V; 6 GND"
note=node(svg,"text",x=4,y=185,font_size=3); note.text="REVIEW ONLY: +Z 55mm sweep unverified; no physical wire routes or manufacturing release"
out=root/"g6_05_seven_axis_review.svg"
ET.ElementTree(svg).write(out,encoding="utf-8",xml_declaration=True)
check=ET.parse(out).getroot()
assert len(check.findall(".//{"+ns+"}circle"))==7
assert len(check.findall(".//{"+ns+"}rect"))==8
print("PASS seven centers, seven 50x41mm nominal envelopes, 42 logical pins; HOLD physical routing")
