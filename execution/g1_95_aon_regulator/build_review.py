#!/usr/bin/env python3
"""G1-95: KiCad-native, manufacturer-pin 3V3_AON buck candidate on real 5V_RAW.

Unpowered review only; an unselected offboard 5V source is NOT certified.
All genuine supply ERC warnings remain UNSUPPRESSED until qualified upstream.
"""
from pathlib import Path
import subprocess,sys,json,re,uuid
D=Path(__file__).resolve().parent
P=D.parent/"g1_94_native_erc_cleanup"
OLD="forest_guardian_g1_94_real_nc_cleanup_review"
NEW="forest_guardian_g1_95_aon_regulator_review"
ROOT="6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"
def f(x):return ("%.2f"%x).rstrip("0").rstrip(".")
def sid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,"ForestGuardian:G1-95:"+x))
def expr(s,k):
 i=s.index(k);n=0;q=False;esc=False
 for p in range(i,len(s)):
  ch=s[p]
  if q:
   if esc:esc=False
   elif ch=="\\":esc=True
   elif ch=='"':q=False
  elif ch=='"':q=True
  elif ch=='(':n+=1
  elif ch==')':
   n-=1
   if n==0:return s[i:p+1]
 raise ValueError("Missing closing parenthesis")
def pad(rows,draw,ref,n,net,x,y,nc=False):
 x=f(x);y=f(y);end=f(float(x)+5.08)
 rows.append(dict(group="B95",source_ref=ref,source_pin=n,source_net=net,
  review_net=net,kicad_ref=ref,wire_end_x=x,wire_end_y=y))
 if nc:draw.append(f'  (no_connect (at {end} {y}) (uuid "{sid(ref+str(n)+"nc")}"))')
 else:
  draw.append(f'  (wire (pts (xy {x} {y}) (xy {end} {y})) (stroke (width 0) (type default)) (uuid "{sid(ref+str(n)+"wire")}"))')
  draw.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1 1))) (uuid "{sid(ref+str(n)+"label")}"))')
def instance(ref,lib,value,x,y,n):
 dz={2:8.89,8:16.51}[n]
 return (f'  (symbol (lib_id "{lib}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{sid(ref+"instance")}")\n'
   f'    (property "Reference" "{ref}" (at {f(x+2.54)} {f(y-dz)} 0) (effects (font (size 1.27 1.27))))\n'
   f'    (property "Value" "{value}" (at {f(x+2.54)} {f(y+dz)} 0) (effects (font (size 1.05 1.05))))\n'
   f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) (effects (font (size 1 1))))\n'
   f'    (property "FG_Source_Ref" "B95:{ref}" (at {f(x)} {f(y)} 0) (effects (font (size 1 1)) (hide yes)))\n'
   f'    (instances (project "{NEW}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
def main():
 subprocess.run([sys.executable,str(P/"build_review.py")],check=True)
 s=(P/(OLD+".kicad_sch")).read_text().replace(OLD,NEW)
 rows=json.loads((P/"pin_map_618_clean.json").read_text())
 assert len(rows)==618
 # Actual manufacturer TPS62933DRLR SOT583 DRL 8-pin:
 # 1 RT, 2 EN, 3 VIN, 4 GND, 5 SW, 6 BST, 7 SS, 8 FB.
 base=expr(s,'(symbol "FG_REVIEW:PAD8"')
 u=base.replace("FG_REVIEW:PAD8","FG_POWER:TPS62933DRLR").replace("PAD8_","TPS62933DRLR_")
 types=[
  ("RT","input"),("EN","input"),("VIN","power_in"),("GND","power_in"),
  ("SW","power_out"),("BST","passive"),("SS","input"),("FB","input")]
 for i,(name,typ) in enumerate(types,1):
  a=f'(name "P{i}"'
  assert u.count(a)==1,(name,a)
  u=u.replace(a,f'(name "{name}"')
  pattern=r'\(pin passive line ([^\n]*?\(name "'+name+r'")'
  u,k=re.subn(pattern,lambda m:'(pin '+typ+' line '+m.group(1),u)
  assert k==1,(name,k)
 lib=u.replace("FG_POWER:TPS62933DRLR","TPS62933DRLR",1)
 (D/"FG_POWER.kicad_sym").write_text('(kicad_symbol_lib\n (version 20231120)\n (generator "kicad_symbol_editor")\n'+lib+'\n)\n')
 libobj=expr(s,"(lib_symbols")
 loc=s.index(libobj)+len(libobj)-1
 s=s[:loc]+"\n"+u+"\n "+s[loc:]
 assert s.count('(paper "User" 1450 2700)')==1
 s=s.replace('(paper "User" 1450 2700)','(paper "User" 1450 3000)')
 out=[];y=2743.2
 nets=[
 "unconnected-(U45-RT-Pad1)","B77__5V_RAW","B77__5V_RAW",
 "GND","B95__BUCK_SW","B95__BUCK_BST",
 "B95__BUCK_SS","B95__BUCK_FB"]
 for i,net in enumerate(nets,1):
  pad(rows,out,"U45",i,net,63.5-15.24,y+(i-4.5)*2.54,nc=(i==1))
 out.append(instance("U45","FG_POWER:TPS62933DRLR","TPS62933DRLR_CANDIDATE",63.5,y,8))
 # J20 is only a source/return connection POINT. A wall adapter is NOT
 # fitted, specified or certified by the review. No PWR_FLAG anywhere.
 for n,net in enumerate(["B77__5V_RAW","GND"],1):
  pad(rows,out,"J20",n,net,175.26-15.24,y+(n-1.5)*2.54)
 out.append(instance("J20","FG_REVIEW:PAD2","UNSELECTED_5V_INPUT_CONNECTOR",175.26,y,2))
 # TI TPS62933 reference: FB 0.8V, default RT NC=500kHz, BST cap 100n,
 # 33nF SS. L and capacitors remain candidate values, NOT production BOM.
 parts=[
 ("L1","4U7H_BUCK_INDUCTOR_CANDIDATE",["B95__BUCK_SW","3V3_AON"]),
 ("R76","31K2_1PCT_FB_TOP",["3V3_AON","B95__BUCK_FB"]),
 ("R77","10K_1PCT_FB_BOT",["B95__BUCK_FB","GND"]),
 ("C46","10UF_10V_X7R_INPUT_A",["B77__5V_RAW","GND"]),
 ("C47","10UF_10V_X7R_INPUT_B",["B77__5V_RAW","GND"]),
 ("C48","22UF_6V3_X7R_OUTPUT_A",["3V3_AON","GND"]),
 ("C49","22UF_6V3_X7R_OUTPUT_B",["3V3_AON","GND"]),
 ("C50","100NF_10V_BST_TO_SW",["B95__BUCK_BST","B95__BUCK_SW"]),
 ("C51","33NF_SS_TO_GND",["B95__BUCK_SS","GND"]),
 ("C52","100NF_VIN_LOCAL_BYPASS",["B77__5V_RAW","GND"])]
 for i,(ref,value,nets) in enumerate(parts):
  x=287.02+111.76*i
  for n,net in enumerate(nets,1):
   pad(rows,out,ref,n,net,x-15.24,y+(n-1.5)*2.54)
  out.append(instance(ref,"FG_REVIEW:PAD2",value,x,y,2))
 assert len(rows)==648 and len({z["kicad_ref"] for z in rows})==194
 s=s.rstrip()[:-1]+"\n"+"\n".join(out)+"\n)\n"
 (D/(NEW+".kicad_sch")).write_text(s)
 (D/"pin_map_648.json").write_text(json.dumps(rows,indent=2)+"\n")
 print("PASS: 648 genuine pads / 194 symbols; actual TPS62933DRLR pin numbers wired into 5V_RAW to 3V3_AON buck candidate")
 print("HOLD: no certified adapter, no verified Iout/inductor/thermal, unresolved supply source/ERC, motors EN/OE hard-off")
if __name__=="__main__":main()
