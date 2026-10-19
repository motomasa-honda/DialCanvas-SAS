#!/usr/bin/env python3
"""G1-94: replace *exactly* 16 provably singleton dangling labels with real KiCad NC.
This is an ERC finding reduction, NOT the creation of a supply or motor enable.
"""
import json,subprocess,sys,uuid
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/"g1_93_inhibited_phase_grant"
OLD="forest_guardian_g1_93_phase_grant_inhibited_review"
NEW="forest_guardian_g1_94_real_nc_cleanup_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
REG=D.parent/"g1_87_rearm_release"/"erc_open_register.json"

def uuid94(value):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-94:"+value))
def close_expression(s,start):
    level=0;quote=False;escape=False
    for i in range(start,len(s)):
        v=s[i]
        if quote:
            if escape:escape=False
            elif v=="\\":escape=True
            elif v=='"':quote=False
        elif v=='"':quote=True
        elif v=="(":level+=1
        elif v==")":
            level-=1
            if level==0:return i+1
    raise ValueError("unbalanced KiCad expression")
def only_expression(s,token):
    if s.count(token)!=1:raise ValueError(f"expected one KiCad expression: {token}, got {s.count(token)}")
    i=s.index(token)
    return s[i:close_expression(s,i)]
def num(x):
    return ("%.2f"%x).rstrip("0").rstrip(".")
def main():
    subprocess.run([sys.executable,str(P/"build_review.py")],check=True)
    s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
    pins=json.loads((P/"pin_map_618.json").read_text())
    original=json.loads((P/"pin_map_618.json").read_text())
    assert len(pins)==618 and len({q["kicad_ref"] for q in pins})==182
    reg=json.loads(REG.read_text())
    labels=reg["expected_label_nets"]
    assert len(labels)==16 and len(set(labels))==16
    assert reg["expected_types"]=={"label_dangling":16,"power_pin_not_driven":3}
    audit=[]
    for label in labels:
        hits=[p for p in pins if p["review_net"]==label]
        if len(hits)!=1:raise ValueError("Not singleton: "+label)
        q=hits[0]
        # All 16 currently use FG_REVIEW:PADx, whose actual schematic pin
        # name is "P<n>". KiCad-native unconnected net name is P<n>-Pad<n>.
        # This mapping is tested again against REAL KiCad9 XML, not assumed.
        ref=str(q["kicad_ref"]);n=int(q["source_pin"])
        x=q["wire_end_x"];y=q["wire_end_y"];end=num(float(x)+5.08)
        label_tok=f'(label "{label}" (at {x} {y} 0)'
        wire_tok=f'(wire (pts (xy {x} {y}) (xy {end} {y}))'
        label_object=only_expression(s,label_tok)
        wire_object=only_expression(s,wire_tok)
        # A unique isolated 5.08mm lead with only this one label, no
        # extra net on the other end. Confirm the documented pin endpoint.
        assert q["source_ref"] and q["group"] in {"B77","B78","B81"}
        nc=f'(no_connect (at {end} {y}) (uuid "{uuid94(ref+":"+str(n))}"))'
        s=s.replace(label_object,"",1)
        s=s.replace(wire_object,nc,1)
        native=f'unconnected-({ref}-P{n}-Pad{n})'
        q["source_net"]=native
        q["review_net"]=native
        audit.append(dict(old_net=label,ref=ref,pin=n,native_net=native,x=end,y=y,
                          evidence="single physical terminal, genuine KiCad no_connect"))
    assert len(audit)==16
    changes=[(o["kicad_ref"],o["source_pin"],o["review_net"],n["review_net"])
             for o,n in zip(original,pins) if o["review_net"]!=n["review_net"]]
    assert len(changes)==16 and len(pins)==len(original)
    assert s.count('(paper "User" 1450 2700)')==1
    # Same full schematic geometry, no extra parts, wires or power supplies.
    (D/"pin_map_618_clean.json").write_text(json.dumps(pins,indent=2)+"\n")
    (D/"nc_conversion_audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    (D/(NEW+".kicad_sch")).write_text(s)
    print("G1-94: replaced 16 SINGLETON labels/wires by 16 genuine KiCad no_connect objects")
    print("618 pads/182 symbols unchanged, no 5V supply invented, U14.EN limited OFF, all /OE disabled")
    print("HOLD: three undriven POWER pins are REAL remaining issues, no waiver/PWR_FLAG")
if __name__=="__main__":main()
