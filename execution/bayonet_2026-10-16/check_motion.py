#!/usr/bin/env python3
"""Independent dependency-free AABB/CSG key motion regression.
Original D7 1774-solid geometry is NOT re-evaluated in this CI.
Does NOT prove hardware retention, wood, stress, fabrication, safety.
"""
import itertools,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/"design_contract.json").read_text())
def intersect(a,b):
    p=(max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3]))
    return p if p[2]-p[0]>1e-9 and p[3]-p[1]>1e-9 else None
def subtract(r,cut):
    overlap=intersect(r,cut)
    if not overlap:return [r]
    a,b,c,h=r;i,j,k,l=overlap
    v=[(a,b,i,h),(k,b,c,h),(i,b,k,j),(i,l,k,h)]
    return [x for x in v if x[2]-x[0]>1e-9 and x[3]-x[1]>1e-9]
def geometry(axis,side):
    x=axis["x"];y=axis["y"];key_y=y+(-7 if side=="L" else 7)
    if side=="L":
        guide=(x-24.2,y-14,x-23.0,y+14)
        boss=(x-24.75,key_y-1,x-23.0,key_y+3.85)
        keyx=(x-23.60,x-22.55);slotx=(x-23.72,x-22.85)
    else:
        guide=(x+23.0,y-14,x+24.2,y+14)
        boss=(x+23.0,key_y-1,x+24.75,key_y+3.85)
        keyx=(x+22.55,x+23.60);slotx=(x+22.85,x+23.72)
    return key_y,guide,boss,keyx,slotx
def contact(axis,side,slide=0,dz=0,enable_window=True,enable_entry=True,keep_lip=True):
    ky,guide,boss,kx,sx=geometry(axis,side)
    key=(kx[0],ky-.5+slide,kx[1],ky+.5+slide)
    low,high=135.0+dz,135.5+dz
    ranges=sorted(set(z for z in [low,high,123,134.3,134.85,135.7,136.5,136.65,136.75] if low-1e-8<=z<=high+1e-8))
    if low<ranges[0]:ranges.insert(0,low)
    if high>ranges[-1]:ranges.append(high)
    window=(sx[0],ky-.8,sx[1],ky+3.8)
    entry=(sx[0],ky-.7,sx[1],ky+.7)
    for za,zb in zip(ranges,ranges[1:]):
        if zb-za<1e-8:continue
        z=(za+zb)/2
        if not keep_lip and z>=135.7:continue
        solids=[]
        if 123<z<136.5:solids.append(guide)
        if 134.3<z<136.65:solids.append(boss)
        for fixed in solids:
            overlap=intersect(key,fixed)
            if overlap is None:continue
            v=[overlap]
            if enable_window and 134.85<=z<135.7:v=[p for r in v for p in subtract(r,window)]
            if enable_entry and 135.7<=z<136.75:v=[p for r in v for p in subtract(r,entry)]
            if v:return True
    return False
assert d["key_count"]==14 and len(d["axes"])==7
assert d["source_d7_sha256"]=="20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
assert d["nominal_key_x_overlap_mm"]==.60 and d["slide_y_mm"]==2.5
assert d["nominal_remaining_boss_x_mm"]==1.15
samples=0;contacts=0
for axis in d["axes"]:
    for side in ("L","R"):
        assert not any(contact(axis,side,0,z/20) for z in range(71)),(axis,side,"entry")
        samples+=71
        assert not any(contact(axis,side,z/20,0) for z in range(51)),(axis,side,"side slide")
        samples+=51
        assert contact(axis,side,2.5,.25),(axis,side,"no positive stop")
        contacts+=1
        assert not any(contact(axis,side,z/20,0) for z in range(51)),(axis,side,"unslide")
        samples+=51
        assert not any(contact(axis,side,0,z/20) for z in range(71)),(axis,side,"unlock extraction")
        samples+=71
        # Deliberately defeat entry / window / lip and ensure test detects broken design.
        assert contact(axis,side,0,1.5,enable_entry=False),(axis,side,"missing entry opening mutation")
        assert contact(axis,side,2.5,0,enable_window=False),(axis,side,"missing lower keyway mutation")
        assert not contact(axis,side,2.5,.25,keep_lip=False),(axis,side,"missing capture lip mutation")
assert samples==3416 and contacts==14
r=d["release"]
assert r["manufacturing_gates_closed"]==0 and r["software_evidence_passed"]==11
assert r["scoped_work_done"]==16 and r["scoped_work_total"]==48
assert d["production_secondary_antislide_keeper"]=="NOT_DESIGNED"
assert d["material_allowable_stress"]=="UNSPECIFIED"
assert d["source_geometry_check"].startswith("LOCAL_D7_FULL_1774")
for p in ("fabrication","power","purchase","flash","main_merge"):assert r[p] is False
out=ROOT/"evidence";out.mkdir(exist_ok=True)
report={"status":"PASS_NOMINAL_KEY_INSERT_SLIDE_CAPTURE_UNSLIDE", "axes":7,"positive_keys":14,
    "kinematic_collision_free_samples":samples,"latched_plus_Z_blocked":contacts,
    "detected_deliberate_design_faults":42,"physical_strength":"NOT_TESTED",
    "antislide_keeper":"NOT_DESIGNED","original_D7_collision":"NOT_RECOMPUTED_IN_GITHUB",
    "manufacturing_gates_closed":0,"software_evidence_passed":11,"outcome_done":16}
(out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
