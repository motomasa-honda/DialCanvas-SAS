#!/usr/bin/env python3
"""G1-92 - Physical positive rail-start grant, hardware inhibited at EN.
Review KiCad9 only: resistors prevent U14 eFuse enable even if logic asserts.
"""
from pathlib import Path
import subprocess,sys,json,uuid
D=Path(__file__).resolve().parent
P=D.parent/"g1_91_aon_supervisor"
OLD="forest_guardian_g1_91_aon_supervisor_review"
NEW="forest_guardian_g1_92_start_grant_inhibited_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
sys.path.insert(0,str(P))
import build_review as parent
def guid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-92:"+x))
def f(x):return ("%.2f"%x).rstrip("0").rstrip(".")
def add_pin(rows,shapes,ref,num,net,x,y,nc=False):
    x=f(x);y=f(y)
    rows.append(dict(group="B92",source_ref=ref,source_pin=num,
        source_net=net,review_net=net,kicad_ref=ref,wire_end_x=x,wire_end_y=y))
    end=f(float(x)+5.08)
    if nc:
        shapes.append(f'  (no_connect (at {end} {y}) (uuid "{guid(ref+str(num)+"NC")}"))')
    else:
        shapes.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1 1))) (uuid "{guid(ref+str(num)+"label")}"))')
        shapes.append(f'  (wire (pts (xy {x} {y}) (xy {end} {y})) (stroke (width 0) (type default)) (uuid "{guid(ref+str(num)+"wire")}"))')
def instance(ref,lib,value,x,y,n):
    dz={5:12.7,2:8.89}[n]
    return (f'  (symbol (lib_id "{lib}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{guid(ref+"instance")}")\n'
        f'    (property "Reference" "{ref}" (at {f(x+2.54)} {f(y-dz)} 0) (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "{value}" (at {f(x+2.54)} {f(y+dz)} 0) (effects (font (size 1.05 1.05))))\n'
        f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) (effects (font (size 1 1))))\n'
        f'    (property "FG_Source_Ref" "B92:{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
        f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
def main():
    subprocess.run([sys.executable,str(P/"build_review.py")],check=True)
    rows=json.loads((P/"pin_map_552.json").read_text())
    assert len(rows)==552
    s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
    assert s.count('(paper "User" 1450 1800)')==1
    s=s.replace('(paper "User" 1450 1800)','(paper "User" 1450 2100)')
    shapes=[];y=1936.75
    # START grant MUST NOT depend on motor PG: PG LOW while eFuse OFF.
    # U39 AND: existing independently-qualified ARM_LATCH and QUAL_CLR_N.
    x=63.5
    nets=["B77__ARM_LATCH_Q_ISOLATED","B77__QUAL_CLR_N","GND",
          "B92__ARM_AND_HEALTH","3V3_AON"]
    for n,net in enumerate(nets,1):
        add_pin(rows,shapes,"U39",n,net,x-15.24,y+(n-3)*2.54)
    shapes.append(instance("U39","FG_FAULT:SN74LVC1G08DBVR","SN74LVC1G08DBVR",x,y,5))
    # U40 invert actual fault request (latched FAULT_Q OR raw TRIP).
    x=175.26
    nets=["unconnected-(U40-NC-Pad1)","B90__CUT_REQUEST_OR",
          "GND","B92__NO_FAULT","3V3_AON"]
    for n,net in enumerate(nets,1):
        add_pin(rows,shapes,"U40",n,net,x-15.24,y+(n-3)*2.54,nc=(n==1))
    shapes.append(instance("U40","FG_FAULT:SN74LVC1G04DBVR","SN74LVC1G04DBVR",x,y,5))
    # U41: positive start request. AON fault is included in TRIP_ALL via
    # U38; eFuse PG and independent 5V rail are deliberately NOT inputs.
    x=287.02
    nets=["B92__ARM_AND_HEALTH","B92__NO_FAULT","GND",
          "B92__RAIL_GRANT_LOGIC","3V3_AON"]
    for n,net in enumerate(nets,1):
        add_pin(rows,shapes,"U41",n,net,x-15.24,y+(n-3)*2.54)
    shapes.append(instance("U41","FG_FAULT:SN74LVC1G08DBVR","SN74LVC1G08DBVR",x,y,5))
    # Physically joined to ACTUAL U14 EN (not a hypothetical label),
    # but R66 and R68 are each 68k 1% positive-current inhibitors.
    # Even if ONE inhibitor shorts and BOTH external R4/R67 pull-downs
    # open, R57+R58 (22k) prevents EN reaching min UVLO at 3V6.
    # Both inhibitors must remain populated until licensed hardware HIL.
    passive=[
      ("R66","68K_1PCT_START_INHIBITOR_A",["B92__RAIL_GRANT_LOGIC","B92__GRANT_LIMIT_STAGE"]),
      ("R68","68K_1PCT_START_INHIBITOR_B",["B92__GRANT_LIMIT_STAGE","B77__U7_EN_CLAMPED_DISABLED"]),
      ("R67","10K_1PCT_SECOND_EN_PULLDOWN",["B77__U7_EN_CLAMPED_DISABLED","GND"]),
      ("C39","100NF_U39_BYPASS",["3V3_AON","GND"]),
      ("C40","100NF_U40_BYPASS",["3V3_AON","GND"]),
      ("C41","100NF_U41_BYPASS",["3V3_AON","GND"])]
    for i,(ref,value,nets) in enumerate(passive):
        x=398.78+i*111.76
        for n,net in enumerate(nets,1):
            add_pin(rows,shapes,ref,n,net,x-15.24,y+(n-1.5)*2.54)
        shapes.append(instance(ref,"FG_REVIEW:PAD2",value,x,y,2))
    assert len(rows)==579 and len({r["kicad_ref"] for r in rows})==168
    assert len({(r["kicad_ref"],r["source_pin"]) for r in rows})==579
    s=s.rstrip()[:-1]+"\n"+"\n".join(shapes)+"\n)\n"
    (D/(NEW+".kicad_sch")).write_text(s)
    (D/"pin_map_579.json").write_text(json.dumps(rows,indent=2)+"\n")
    print("G1-92 true KiCad: 579 physical pins/168 parts, 552 parent unchanged, start permit wired to U14 EN via two 68k hardware inhibiting resistors")
    print("HOLD eFuse EN always below min UVLO with passive limit; 28-phase OE disabled, no hardware operation approved")
if __name__=="__main__":main()
