#!/usr/bin/env python3
"""Produce editable KiCad9 G1-88 PG+rail fault mixer by an exact G1-87 delta.
REVIEW ONLY. No real power path or manufacturing approval."""
import json,uuid
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/"g1_87_rearm_release"
OLD="forest_guardian_g1_87_release_qualified_review"
NEW="forest_guardian_g1_88_pg_rail_fault_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
def uid(tag):return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-88:"+tag))
def num(v):return f"{v:.2f}".rstrip("0").rstrip(".")
def sub1(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)
def close(s,start):
    depth=0;inside=False;escape=False
    for i in range(start,len(s)):
        c=s[i]
        if inside:
            if escape:escape=False
            elif c=="\\":escape=True
            elif c=='"':inside=False
        elif c=='"':inside=True
        elif c=="(":depth+=1
        elif c==")":
            depth-=1
            if depth==0:return i+1
    raise ValueError("unbalanced KiCad schematic")
def extract(s,token):
    i=s.index(token);return s[i:close(s,i)]
def pin(rows,items,ref,n,net,x,y,nc=False):
    xx=num(x);yy=num(y)
    rows.append(dict(group="B88",source_ref=ref,source_pin=n,source_net=net,
        review_net=net,kicad_ref=ref,wire_end_x=xx,wire_end_y=yy))
    if nc:
        items.append(f'  (no_connect (at {num(x+5.08)} {yy}) (uuid "{uid(ref+str(n)+"nc")}"))')
    else:
        items.append(f'  (label "{net}" (at {xx} {yy} 0) (effects (font (size 1 1))) (uuid "{uid(ref+str(n)+"label")}"))')
        items.append(f'  (wire (pts (xy {xx} {yy}) (xy {num(x+5.08)} {yy})) (stroke (width 0) (type default)) (uuid "{uid(ref+str(n)+"wire")}"))')
def symbol(ref,lib,val,x,y,count):
    dz=12.7 if count==5 else 8.89
    a=f'  (symbol (lib_id "{lib}") (at {num(x)} {num(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref+"instance")}")\n'
    a+=f'    (property "Reference" "{ref}" (at {num(x+2.54)} {num(y-dz)} 0) (effects (font (size 1.27 1.27))))\n'
    a+=f'    (property "Value" "{val}" (at {num(x+2.54)} {num(y+dz)} 0) (effects (font (size 1.05 1.05))))\n'
    a+=f'    (property "Footprint" "" (at {num(x)} {num(y)} 0) (effects (font (size 1 1))))\n'
    a+=f'    (property "FG_Source_Ref" "B88:{ref}" (at {num(x)} {num(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
    a+=f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )'
    return a
def main():
    text=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
    rows=json.loads((P/"pin_map_446.json").read_text())
    assert len(rows)==446
    delta={("U20",5):"B88__TRIP_COMBINED",("U23",1):"B88__TRIP_COMBINED",
           ("U22",2):"B88__QUAL_EXT_N",("U26",1):"B88__QUAL_EXT_N"}
    for r in rows:
        k=(r["kicad_ref"],r["source_pin"])
        if k in delta:
            coord=f'(at {r["wire_end_x"]} {r["wire_end_y"]} 0)'
            old_label=f'(label "{r["review_net"]}" {coord}'
            r["review_net"]=delta[k]
            text=sub1(text,old_label,f'(label "{r["review_net"]}" {coord}')
    # Manufacturer DBV OR A1 B2 GND3 Y4 VCC5, same pin geometry as AND.
    or_def=extract(text,'(symbol "FG_FAULT:SN74LVC1G08DBVR"').replace("SN74LVC1G08DBVR","SN74LVC1G32DBVR")
    pos=close(text,text.index("(lib_symbols"))
    text=text[:pos-1]+"\n"+or_def+"\n  "+text[pos-1:]
    lib=(P/"FG_FAULT.kicad_sym").read_text()
    plain_or=extract(lib,'(symbol "SN74LVC1G08DBVR"').replace("SN74LVC1G08DBVR","SN74LVC1G32DBVR")
    pos=lib.rfind(")")
    (D/"FG_FAULT.kicad_sym").write_text(lib[:pos]+"\n"+plain_or+"\n"+lib[pos:])
    items=[]
    gates=[
      ("U28","FG_FAULT:SN74LVC1G08DBVR","SN74LVC1G08DBVR",["B77__EFUSE_PG_OD","B81__RAIL_OK_N_SUPERVISOR","GND","B88__PG_AND_RAIL_OK","3V3_AON"]),
      ("U29","FG_FAULT:SN74LVC1G04DBVR","SN74LVC1G04DBVR",["unconnected-(U29-NC-Pad1)","B88__PG_AND_RAIL_OK","GND","B88__PG_OR_RAIL_BAD","3V3_AON"]),
      ("U30","FG_FAULT:SN74LVC1G08DBVR","SN74LVC1G08DBVR",["B88__PG_OR_RAIL_BAD","B88__MONITOR_ACTIVE","GND","B88__POST_START_FAULT","3V3_AON"]),
      ("U31","FG_FAULT:SN74LVC1G32DBVR","SN74LVC1G32DBVR",["B86__TRIP_ASSERT","B88__POST_START_FAULT","GND","B88__TRIP_COMBINED","3V3_AON"]),
      ("U32","FG_FAULT:SN74LVC1G04DBVR","SN74LVC1G04DBVR",["unconnected-(U32-NC-Pad1)","B88__TRIP_COMBINED","GND","B88__QUAL_EXT_N","3V3_AON"])]
    for i,(ref,libname,value,nets) in enumerate(gates):
        x=63.5+111.76*i;y=1092.2
        for n,net in enumerate(nets,1):
            pin(rows,items,ref,n,net,x-15.24,y+(n-3)*2.54,net.startswith("unconnected-"))
        items.append(symbol(ref,libname,value,x,y,5))
    passive=[("J19","MONITOR_ACTIVE_REVIEW_INPUT",["B88__MONITOR_ACTIVE","GND"]),
             ("R56","10K_PULLDOWN_DISABLED",["B88__MONITOR_ACTIVE","GND"])]
    passive += [(f"C{i}",f"100NF_BYPASS_U{i+3}",["3V3_AON","GND"]) for i in range(25,30)]
    for i,(ref,val,nets) in enumerate(passive):
        x=622.3+111.76*i;y=1155.7
        for n,net in enumerate(nets,1):
            pin(rows,items,ref,n,net,x-15.24,y+(n-1.5)*2.54)
        items.append(symbol(ref,"FG_REVIEW:PAD2",val,x,y,2))
    assert len(rows)==485 and len({x["kicad_ref"] for x in rows})==136
    (D/"pin_map_485.json").write_text(json.dumps(rows,indent=2)+"\n")
    (D/(NEW+".kicad_sch")).write_text(text.rstrip()[:-1]+"\n"+"\n".join(items)+"\n)\n")
    print("Generated 485 physical KiCad pads/136 symbols; 4 original rewires; no power enabled")
if __name__=="__main__":main()
