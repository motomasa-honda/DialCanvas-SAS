#!/usr/bin/env python3
"""G1-89 unpowered native KiCad9 hardware startup timer candidate."""
import json,re,sys,uuid
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/"g1_88_pg_rail_fault"
sys.path.insert(0,str(P))
import build_review as prior
OLD="forest_guardian_g1_88_pg_rail_fault_review"
NEW="forest_guardian_g1_89_hardware_start_deadline_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
def one(s,old,new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new)
def obj(s,key):
    i=s.index(key)
    return s[i:prior.close(s,i)]
def uuid89(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-89:"+key))
def sym(ref,lib,value,x,y,pincount):
    f=prior.num; offset=13.97 if pincount==6 else 8.89
    return (f'  (symbol (lib_id "{lib}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uuid89(ref+"instance")}")\n'
      f'    (property "Reference" "{ref}" (at {f(x+2.54)} {f(y-offset)} 0) (effects (font (size 1.27 1.27))))\n'
      f'    (property "Value" "{value}" (at {f(x+2.54)} {f(y+offset)} 0) (effects (font (size 1.05 1.05))))\n'
      f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) (effects (font (size 1 1))))\n'
      f'    (property "FG_Source_Ref" "B89:{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
      f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
def main():
    prior.main()
    s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
    rows=json.loads((P/"pin_map_485.json").read_text())
    assert len(rows)==485
    # Remove unsafe manual short-to-GND J19 that could defeat PG/rail fault.
    target='(symbol (lib_id "FG_REVIEW:PAD2") (at 622.3 1155.7 0)'
    s=one(s,obj(s,target),"")
    for q in [x for x in rows if x["kicad_ref"]=="J19"]:
        x,y=q["wire_end_x"],q["wire_end_y"]
        lab=f'(label "{q["review_net"]}" (at {x} {y} 0)'
        w=f'(wire (pts (xy {x} {y})'
        s=one(s,obj(s,lab),"")
        s=one(s,obj(s,w),"")
    rows=[x for x in rows if x["kicad_ref"]!="J19"]
    assert len(rows)==483
    # Open-drain MONITOR_ACTIVE needs a TI-required pull-UP, not a pull-down.
    q=next(x for x in rows if x["kicad_ref"]=="R56" and x["source_pin"]==2)
    s=one(s,f'(label "GND" (at {q["wire_end_x"]} {q["wire_end_y"]} 0)',
            f'(label "3V3_AON" (at {q["wire_end_x"]} {q["wire_end_y"]} 0)')
    q["review_net"]=q["source_net"]="3V3_AON"
    # Copy precise 6-pin geometries of the already-native KiCad 9 PAD6.
    native=obj(s,'(symbol "FG_REVIEW:PAD6"')
    u33=native.replace("FG_REVIEW:PAD6","FG_TIMER:TPS3808G01DBVR").replace("PAD6_","TPS3808G01DBVR_")
    pin_types=[("RESET_N","open_collector"),("GND","power_in"),
               ("MR_N","input"),("CT","input"),("SENSE","input"),("VDD","power_in")]
    for i,(name,typ) in enumerate(pin_types,1):
        u33=one(u33,f'(name "P{i}"',f'(name "{name}"')
        pattern=r'\(pin passive line ([^\n]*?\(name "'+name+r'")'
        u33,count=re.subn(pattern,lambda m:'(pin '+typ+' line '+m.group(1),u33)
        assert count==1,(name,count)
    library=u33.replace("FG_TIMER:TPS3808G01DBVR","TPS3808G01DBVR",1)
    (D/"FG_TIMER.kicad_sym").write_text('(kicad_symbol_lib\n (version 20231120)\n (generator "kicad_symbol_editor")\n'+library+'\n)\n')
    at=prior.close(s,s.index("(lib_symbols"))
    s=s[:at-1]+"\n"+u33+"\n "+s[at-1:]
    s=one(s,'(paper "User" 1450 1200)','(paper "User" 1450 1500)')
    extra=[]
    x=63.5;y=1268.73
    # DBV pins 1=RESET_N 2=GND 3=MR_N 4=CT 5=SENSE 6=VDD.
    # Critical G1-89 repair: TPS3808 MR digital VIH>=0.7*3V3=2.31V,
    # while TPS259474 eFuse EN may assert at 1.183V.
    # MR is tied to its own well-defined AON VDD, while high-accuracy
    # adjustable SENSE sees the SAME physical eFuse EN via a divider.
    # This starts the timer before the minimum eFuse turn-on threshold;
    # neither MCU software nor PG can postpone the hardware deadline.
    wires=["B88__MONITOR_ACTIVE","GND","3V3_AON",
           "B89__STARTUP_CT","B89__EN_SENSE_DIV","3V3_AON"]
    for n,net in enumerate(wires,1):
        prior.pin(rows,extra,"U33",n,net,x-15.24,y+(n-3.5)*2.54)
    extra.append(sym("U33","FG_TIMER:TPS3808G01DBVR","TPS3808G01DBVR",x,y,6))
    # SENSE falling threshold nominal 0.405V; for EN divider 12k/10k,
    # equivalent EN threshold is 0.891V typical (worst tolerance <0.920V),
    # safely below eFuse EN rising min 1.183V. R4 permanent PD retained.
    # 68nF gives ~389ms nominal delay, NOT a guaranteed max <=500ms.
    parts=[("R57","12K_1PCT_EN_SENSE_TOP",["B77__U7_EN_CLAMPED_DISABLED","B89__EN_SENSE_DIV"]),
           ("R58","10K_1PCT_EN_SENSE_BOT",["B89__EN_SENSE_DIV","GND"]),
           ("C30","68NF_LOW_LEAKAGE_CT",["B89__STARTUP_CT","GND"]),
           ("C31","100NF_VDD_DECOUPLING",["3V3_AON","GND"]),
           ("C32","1NF_SENSE_FILTER",["B89__EN_SENSE_DIV","GND"])]
    for i,(ref,value,nets) in enumerate(parts):
        x=175.26+i*111.76
        for n,net in enumerate(nets,1):
            prior.pin(rows,extra,ref,n,net,x-15.24,y+(n-1.5)*2.54)
        extra.append(sym(ref,"FG_REVIEW:PAD2",value,x,y,2))
    for item in rows[483:]:item["group"]="B89"
    assert len(rows)==499 and len({x["kicad_ref"] for x in rows})==141
    (D/"pin_map_499.json").write_text(json.dumps(rows,indent=2)+"\n")
    (D/(NEW+".kicad_sch")).write_text(s.rstrip()[:-1]+"\n"+"\n".join(extra)+"\n)\n")
    print("PASS: KiCad G1-89 499 true pads/141 symbols; J19 removed; R56 pull-up, actual TPS3808 DBV.")
    print("HOLD: U7 EN still R4 to GND, 28 OE disabled. 3V3 cold POR, analog delay and safety HIL not accepted.")
if __name__=="__main__":main()
