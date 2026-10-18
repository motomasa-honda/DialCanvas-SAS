#!/usr/bin/env python3
"""G1-91 actual physical AON undervoltage fault for unpowered KiCad9 review."""
import subprocess,sys,json,uuid
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/"g1_90_fault_cutoff"
OLD="forest_guardian_g1_90_fault_cutoff_review"
NEW="forest_guardian_g1_91_aon_supervisor_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
sys.path.insert(0,str(P))
import build_review as prior
def uid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-91:"+x))
def pin(rows,shapes,ref,n,net,x,y,nc=False):
 x=prior.f(x);y=prior.f(y)
 rows.append(dict(group="B91",source_ref=ref,source_pin=n,source_net=net,
     review_net=net,kicad_ref=ref,wire_end_x=x,wire_end_y=y))
 if nc:
  shapes.append(f'  (no_connect (at {prior.f(float(x)+5.08)} {y}) (uuid "{uid(ref+str(n)+"nc")}"))')
 else:
  shapes.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1 1))) (uuid "{uid(ref+str(n)+"label")}"))')
  shapes.append(f'  (wire (pts (xy {x} {y}) (xy {prior.f(float(x)+5.08)} {y})) (stroke (width 0) (type default)) (uuid "{uid(ref+str(n)+"wire")}"))')
def six(ref,x,y):
 f=prior.f
 return (f'  (symbol (lib_id "FG_TIMER:TPS3808G01DBVR") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref+"instance")}")\n'
     f'    (property "Reference" "{ref}" (at {f(x+2.54)} {f(y-13.97)} 0) (effects (font (size 1.27 1.27))))\n'
     f'    (property "Value" "TPS3808G01DBVR" (at {f(x+2.54)} {f(y+13.97)} 0) (effects (font (size 1.05 1.05))))\n'
     f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) (effects (font (size 1 1))))\n'
     f'    (property "FG_Source_Ref" "B91:{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
     f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
def main():
 subprocess.run([sys.executable,str(P/"build_review.py")],check=True)
 s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
 rows=json.loads((P/"pin_map_522.json").read_text())
 assert len(rows)==522
 rewires={("U20",5),("U23",1),("U32",2),("U35",2)}
 for z in rows:
  if (z["kicad_ref"],z["source_pin"]) in rewires:
   assert z["review_net"]=="B88__TRIP_COMBINED"
   token=f'(label "{z["review_net"]}" (at {z["wire_end_x"]} {z["wire_end_y"]} 0)'
   assert s.count(token)==1,token
   s=s.replace(token,token.replace("B88__TRIP_COMBINED","B91__TRIP_ALL"))
   z["review_net"]="B91__TRIP_ALL"
 assert s.count('(paper "User" 1450 1500)')==1
 s=s.replace('(paper "User" 1450 1500)','(paper "User" 1450 1800)')
 shapes=[];y=1619.25
 # U36 TPS3808 DBV: RESET1 GND2 MR3 CT4 SENSE5 VDD6
 nets=["B91__AON_GOOD_N_RESET","GND","3V3_AON",
       "unconnected-(U36-CT-Pad4)","B91__AON_SENSE_DIV","3V3_AON"]
 for n,net in enumerate(nets,1):
  pin(rows,shapes,"U36",n,net,63.5-15.24,y+(n-3.5)*2.54,nc=(n==4))
 shapes.append(six("U36",63.5,y))
 # DBV inverter U37 1 NC, 2 A, 3 GND, 4 Y, 5 VCC
 nets=["unconnected-(U37-NC-Pad1)","B91__AON_GOOD_N_RESET",
       "GND","B91__AON_BAD","3V3_AON"]
 for n,net in enumerate(nets,1):
  pin(rows,shapes,"U37",n,net,175.26-15.24,y+(n-3)*2.54,nc=(n==1))
 shapes.append(prior.inst("U37","FG_FAULT:SN74LVC1G04DBVR","SN74LVC1G04DBVR",175.26,y,5))
 # U38 OR B88 trip + AON bad -> TRIP_ALL.
 nets=["B88__TRIP_COMBINED","B91__AON_BAD","GND",
       "B91__TRIP_ALL","3V3_AON"]
 for n,net in enumerate(nets,1):
  pin(rows,shapes,"U38",n,net,287.02-15.24,y+(n-3)*2.54)
 shapes.append(prior.inst("U38","FG_FAULT:SN74LVC1G32DBVR","SN74LVC1G32DBVR",287.02,y,5))
 parts=[
  ("R63","60K4_1PCT_AON_TOP",["3V3_AON","B91__AON_SENSE_DIV"]),
  ("R64","10K_1PCT_AON_BOT",["B91__AON_SENSE_DIV","GND"]),
  ("R65","100K_AON_RESET_PULLUP",["B91__AON_GOOD_N_RESET","3V3_AON"]),
  ("C35","100NF_U36_BYPASS",["3V3_AON","GND"]),
  ("C36","1NF_AON_SENSE_FILTER",["B91__AON_SENSE_DIV","GND"]),
  ("C37","100NF_U37_BYPASS",["3V3_AON","GND"]),
  ("C38","100NF_U38_BYPASS",["3V3_AON","GND"])]
 for i,(ref,value,nets) in enumerate(parts):
  x=398.78+111.76*i
  for n,net in enumerate(nets,1):
   pin(rows,shapes,ref,n,net,x-15.24,y+(n-1.5)*2.54)
  shapes.append(prior.inst(ref,"FG_REVIEW:PAD2",value,x,y,2))
 assert len(rows)==552 and len({r["kicad_ref"] for r in rows})==159
 s=s.rstrip()[:-1]+"\n"+"\n".join(shapes)+"\n)\n"
 (D/(NEW+".kicad_sch")).write_text(s)
 (D/"pin_map_552.json").write_text(json.dumps(rows,indent=2)+"\n")
 print("G1-91 generated: 552 physical pins, 159 real KiCad symbols, 4 exact original rewires")
 print("HOLD: U7 EN physically R4 pulled GND, no 3V3 below-POR safety qualification or powered HIL")
if __name__=="__main__":main()
