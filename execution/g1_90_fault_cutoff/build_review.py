#!/usr/bin/env python3
"""G1-90: real native KiCad physical fault-to-EN sink and fault-to-8OE disable.
The native circuit remains HARD DISABLED; review not a powered release."""
import json, subprocess, sys, uuid
from pathlib import Path

D = Path(__file__).resolve().parent
P = D.parent / "g1_89_hardware_start_deadline"
OLD = "forest_guardian_g1_89_hardware_start_deadline_review"
NEW = "forest_guardian_g1_90_fault_cutoff_review"
ROOT = "6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"

def u(k):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-90:"+k))
def f(n):
    return ("%.2f" % n).rstrip("0").rstrip(".")
def close(s,idx):
    count=0;quoted=False;escape=False
    for i in range(idx,len(s)):
        c=s[i]
        if quoted:
            if escape:escape=False
            elif c=="\\":escape=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=="(":count+=1
        elif c==")":
            count-=1
            if count==0:return i+1
    raise ValueError("Unbalanced S-expression")
def find(s,token):
    start=s.index(token)
    return s[start:close(s,start)]
def pin(pins,parts,ref,n,net,x,y):
    x=f(x);y=f(y)
    pins.append(dict(group="B90",source_ref=ref,source_pin=n,source_net=net,
        review_net=net,kicad_ref=ref,wire_end_x=x,wire_end_y=y))
    parts.append(f'  (wire (pts (xy {x} {y}) (xy {f(float(x)+5.08)} {y})) (stroke (width 0) (type default)) (uuid "{u(ref+str(n)+"wire")}"))')
    parts.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1 1))) (uuid "{u(ref+str(n)+"label")}"))')
def inst(ref,library,value,x,y,n):
    dz={2:8.89,3:10.16,5:12.7}[n]
    return (f'  (symbol (lib_id "{library}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{u(ref+"symbol")}")\n'
      f'    (property "Reference" "{ref}" (at {f(x+2.54)} {f(y-dz)} 0) (effects (font (size 1.27 1.27))))\n'
      f'    (property "Value" "{value}" (at {f(x+2.54)} {f(y+dz)} 0) (effects (font (size 1.05 1.05))))\n'
      f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) (effects (font (size 1 1))))\n'
      f'    (property "FG_Source_Ref" "B90:{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
      f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
def fet_library():
    # Verified INFINEON 2N7002 PG-SOT23: 1 GATE 2 SOURCE 3 DRAIN.
    # Review symbol uses manufacturer pin NUMBER but no PCB footprint.
    inside = '''(symbol "2N7002_PG_SOT23_REVIEW" (pin_numbers (hide yes)) (pin_names (offset 0) (hide yes)) (in_bom no) (on_board no)
      (property "Reference" "Q" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
      (property "Value" "2N7002_INFINEON_PG_SOT23" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1 1))))
      (symbol "2N7002_PG_SOT23_REVIEW_0_1"
       (rectangle (start -7.62 5.08) (end 7.62 -5.08)
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "2N7002_PG_SOT23_REVIEW_1_1"
       (pin input line (at -10.16 2.54 0) (length 2.54) (name "GATE" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))
       (pin passive line (at -10.16 0 0) (length 2.54) (name "SOURCE" (effects (font (size 1 1)))) (number "2" (effects (font (size 1 1)))))
       (pin passive line (at -10.16 -2.54 0) (length 2.54) (name "DRAIN" (effects (font (size 1 1)))) (number "3" (effects (font (size 1 1)))))
      )
    )'''
    (D/"FG_CUTOFF.kicad_sym").write_text('(kicad_symbol_lib\n (version 20231120)\n (generator "kicad_symbol_editor")\n'+inside+'\n)\n')
    return inside.replace('(symbol "2N7002_PG_SOT23_REVIEW"', '(symbol "FG_CUTOFF:2N7002_PG_SOT23_REVIEW"',1)

def main():
    # Execute parent in a separate Python process to preserve import isolation
    # between G1-88 and G1-89 both named build_review.py.
    subprocess.run([sys.executable,str(P/"build_review.py")],check=True)
    s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
    rows=json.loads((P/"pin_map_499.json").read_text())
    assert len(rows)==499
    # Already-proven AND/OR library. Add ONE physical FET to pull EN low on FAULT.
    fet=fet_library()
    at=close(s,s.index("(lib_symbols"))
    s=s[:at-1]+"\n"+fet+"\n "+s[at-1:]
    extra=[]
    # Dedicated fault-asserted 2N7002 drain sinks the *actual* U14 EN net.
    # U14 EN still has original R4 10k pull-DOWN; no actuation is possible.
    x=63.5;y=1422.4
    for n,net in enumerate(["B90__FAULT_FET_GATE","GND","B77__U7_EN_CLAMPED_DISABLED"],1):
        pin(rows,extra,"Q1",n,net,x-15.24,y+(n-2)*2.54)
    extra.append(inst("Q1","FG_CUTOFF:2N7002_PG_SOT23_REVIEW","2N7002_INFINEON",x,y,3))
    # The source OR logic after U35 intentionally treats TRIP as primary
    # protection even when the NOR fault latch output has not yet settled.
    # This STILL does not certify behavior when AON logic itself is unpowered.
    parts=[
      ("R59","330R_FAULT_GATE_SERIES",["B90__CUT_REQUEST_OR","B90__FAULT_FET_GATE"]),
      ("R60","100K_FET_GS_PULLDOWN",["B90__FAULT_FET_GATE","GND"]),
      ("R61","10K_OE_SAFE_DISABLE_PULLUP",["B90__OE_DISABLE_NOT_RELEASED","3V3_AON"]),
      ("C33","100NF_U34_DECOUPLING",["3V3_AON","GND"]),
    ]
    for i,(ref,value,nets) in enumerate(parts):
        px=175.26+111.76*i
        for n,net in enumerate(nets,1):
            pin(rows,extra,ref,n,net,px-15.24,y+(n-1.5)*2.54)
        extra.append(inst(ref,"FG_REVIEW:PAD2",value,px,y,2))
    # Existing G1-88 manufacturer-labelled SN74LVC1G32DBVR OR:
    # 1=FAULT or direct TRIP (from U35), 2=hard-disable pullup, 4=8 OE_N
    x=622.3
    oe_nets=["B90__CUT_REQUEST_OR","B90__OE_DISABLE_NOT_RELEASED","GND",
             "B78__PHASE_OE_N_FIXED_HIGH","3V3_AON"]
    for n,net in enumerate(oe_nets,1):
        pin(rows,extra,"U34",n,net,x-15.24,y+(n-3)*2.54)
    extra.append(inst("U34","FG_FAULT:SN74LVC1G32DBVR","SN74LVC1G32DBVR",x,y,5))
    # Important cold-start/fault-propagation hardening: relying only on
    # FAULT_Q is unsafe while the NOR latch is initializing or propagating.
    # U35 directly ORs the pre-latch TRIP_COMBINED with latched FAULT_Q.
    # Both eFuse sink and /OE must react to either HIGH source.
    x=734.06
    for n,net in enumerate(["B86__FAULT_Q","B88__TRIP_COMBINED","GND",
                            "B90__CUT_REQUEST_OR","3V3_AON"],1):
        pin(rows,extra,"U35",n,net,x-15.24,y+(n-3)*2.54)
    extra.append(inst("U35","FG_FAULT:SN74LVC1G32DBVR","SN74LVC1G32DBVR",x,y,5))
    x=845.82
    for n,net in enumerate(["3V3_AON","GND"],1):
        pin(rows,extra,"C34",n,net,x-15.24,y+(n-1.5)*2.54)
    extra.append(inst("C34","FG_REVIEW:PAD2","100NF_U35_DECOUPLING",x,y,2))
    assert len(rows)==522 and len({p["kicad_ref"] for p in rows})==149
    assert len({(p["kicad_ref"],p["source_pin"]) for p in rows})==522
    s=s.rstrip()[:-1]+"\n"+"\n".join(extra)+"\n)\n"
    (D/(NEW+".kicad_sch")).write_text(s)
    (D/"pin_map_522.json").write_text(json.dumps(rows,indent=2)+"\n")
    print("PASS: G1-90 522 pads/149 parts, original TRIP and FAULT_Q hard-OR to eFuse sink and all 8 OE_N.")
    print("HOLD: U14 EN remains R4-to-GND, U34 input2 pullup HIGH; 28 phase outputs disabled.")
if __name__=="__main__": main()
