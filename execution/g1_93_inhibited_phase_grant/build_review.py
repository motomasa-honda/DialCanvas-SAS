#!/usr/bin/env python3
"""G1-93 physical PG+independent rail stable+RUN phase grant, review only.
Phase gate FET deliberately inhibited by two 68k series resistors; OE HIGH.
"""
import json,subprocess,sys,uuid
from pathlib import Path
D=Path(__file__).resolve().parent
P=D.parent/"g1_92_inhibited_start_grant"
OLD="forest_guardian_g1_92_start_grant_inhibited_review"
NEW="forest_guardian_g1_93_phase_grant_inhibited_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
def f(x):return ("%.2f"%x).rstrip("0").rstrip(".")
def uid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-93:"+x))
def pin(rows,parts,ref,n,net,x,y,nc=False):
 x=f(x);y=f(y);end=f(float(x)+5.08)
 rows.append(dict(group="B93",source_ref=ref,source_pin=n,source_net=net,
     review_net=net,kicad_ref=ref,wire_end_x=x,wire_end_y=y))
 if nc:
  parts.append(f'  (no_connect (at {end} {y}) (uuid "{uid(ref+str(n)+"nc")}"))')
 else:
  parts.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1 1))) (uuid "{uid(ref+str(n)+"label")}"))')
  parts.append(f'  (wire (pts (xy {x} {y}) (xy {end} {y})) (stroke (width 0) (type default)) (uuid "{uid(ref+str(n)+"wire")}"))')
def inst(ref,library,value,x,y,n):
 dz={2:8.89,3:10.16,5:12.7,6:13.97}[n]
 return (f'  (symbol (lib_id "{library}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(ref+"inst")}")\n'
     f'    (property "Reference" "{ref}" (at {f(x+2.54)} {f(y-dz)} 0) (effects (font (size 1.27 1.27))))\n'
     f'    (property "Value" "{value}" (at {f(x+2.54)} {f(y+dz)} 0) (effects (font (size 1.05 1.05))))\n'
     f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) (effects (font (size 1 1))))\n'
     f'    (property "FG_Source_Ref" "B93:{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
     f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
def main():
 subprocess.run([sys.executable,str(P/"build_review.py")],check=True)
 s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
 rows=json.loads((P/"pin_map_579.json").read_text())
 assert len(rows)==579
 assert s.count('(paper "User" 1450 2100)')==1
 s=s.replace('(paper "User" 1450 2100)','(paper "User" 1450 2700)')
 y=2203.45;extra=[]
 # U42 manufacturer real TPS3808G01 DBV physical pins RESET1 GND2
 # MR3 CT4 SENSE5 VDD6. Threshold 2.851V on AND-logic output.
 # CT NC: ~20ms TYPICAL reset release, worst-case not yet qualified.
 x=63.5
 nets=["B93__PG_RAIL_STABLE_N_RESET","GND","3V3_AON",
       "unconnected-(U42-CT-Pad4)","B93__PG_RAIL_DIV","3V3_AON"]
 for n,net in enumerate(nets,1):
  pin(rows,extra,"U42",n,net,x-15.24,y+(n-3.5)*2.54,nc=(n==4))
 extra.append(inst("U42","FG_TIMER:TPS3808G01DBVR","TPS3808G01DBVR",x,y,6))
 # U43 requires actual U12 run-state / heartbeat latch and the
 # G1-92 independent qualified start grant (not PG).
 x=175.26
 nets=["B77__HB_TWO_EDGE_Q_ISOLATED","B92__RAIL_GRANT_LOGIC",
       "GND","B93__RUN_AND_START","3V3_AON"]
 for n,net in enumerate(nets,1):
  pin(rows,extra,"U43",n,net,x-15.24,y+(n-3)*2.54)
 extra.append(inst("U43","FG_FAULT:SN74LVC1G08DBVR","SN74LVC1G08DBVR",x,y,5))
 x=287.02
 nets=["B93__PG_RAIL_STABLE_N_RESET","B93__RUN_AND_START",
       "GND","B93__PHASE_GRANT_LOGIC","3V3_AON"]
 for n,net in enumerate(nets,1):
  pin(rows,extra,"U44",n,net,x-15.24,y+(n-3)*2.54)
 extra.append(inst("U44","FG_FAULT:SN74LVC1G08DBVR","SN74LVC1G08DBVR",x,y,5))
 # Q2 drains the REAL U34 OR.B holdoff node, not a status-only stub,
 # but GATE voltage is deliberately inhibited by R72+R73+R74.
 # Without Q2, R61 10k holds U34 B=HIGH -> all 8 OE=HIGH.
 x=398.78
 nets=["B93__PHASE_FET_GATE","GND","B90__OE_DISABLE_NOT_RELEASED"]
 for n,net in enumerate(nets,1):
  pin(rows,extra,"Q2",n,net,x-15.24,y+(n-2)*2.54)
 extra.append(inst("Q2","FG_CUTOFF:DMN2056U_PG_SOT23_REVIEW","DMN2056U_DIODES",x,y,3))
 passive=[
   ("R69","60K4_1PCT_PG_RAIL_DELAY_TOP",["B88__PG_AND_RAIL_OK","B93__PG_RAIL_DIV"]),
   ("R70","10K_1PCT_PG_RAIL_DELAY_BOT",["B93__PG_RAIL_DIV","GND"]),
   ("R71","100K_PG_RAIL_DELAY_RESET_PULLUP",["B93__PG_RAIL_STABLE_N_RESET","3V3_AON"]),
   ("R72","68K_1PCT_PHASE_FET_INHIBITOR_A",["B93__PHASE_GRANT_LOGIC","B93__PHASE_LIMIT_STAGE"]),
   ("R73","68K_1PCT_PHASE_FET_INHIBITOR_B",["B93__PHASE_LIMIT_STAGE","B93__PHASE_FET_GATE"]),
   ("R74","1K_1PCT_PHASE_GATE_GND",["B93__PHASE_FET_GATE","GND"]),
   ("C42","100NF_U42_BYPASS",["3V3_AON","GND"]),
   ("C43","100NF_U43_BYPASS",["3V3_AON","GND"]),
   ("C44","100NF_U44_BYPASS",["3V3_AON","GND"]),
   ("C45","1NF_PG_RAIL_SENSE_FILTER",["B93__PG_RAIL_DIV","GND"])]
 for i,(ref,value,nets) in enumerate(passive):
  x=510.54+i*111.76 if i<8 else 175.26+(i-8)*111.76
  yy=y if i<8 else 2330.45
  for n,net in enumerate(nets,1):
   pin(rows,extra,ref,n,net,x-15.24,yy+(n-1.5)*2.54)
  extra.append(inst(ref,"FG_REVIEW:PAD2",value,x,yy,2))
 assert len(rows)==618 and len({z["kicad_ref"] for z in rows})==182
 s=s.rstrip()[:-1]+"\n"+"\n".join(extra)+"\n)\n"
 (D/"pin_map_618.json").write_text(json.dumps(rows,indent=2)+"\n")
 (D/(NEW+".kicad_sch")).write_text(s)
 print("G1-93 actual: 618 physical KiCad pins/182 components, qualified PG+rail 20ms nominal phase grant and real Q2->U34.B OE inhibit")
 print("HOLD: Q2 gate forced LOW by 68k+68k and 1k GND; all eight OE held HIGH, eFuse EN held disabled")
if __name__=="__main__":main()
