#!/usr/bin/env python3
"""Full-source geometry screen for the external 30mm rear exhaust-fan candidate."""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"secondary_keeper_2026-10-16"))
import audit_full_d7_clearance as geom

EXPECTED_SHA256 = "20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f"
EXPECTED_SOLIDS = 1774
CENTER = (220.0, 40.0)
FAN_BODY = (30.0, 30.0, 10.0)
FAN_BODY_Z = (146.5, 156.5)
PLATE_SIZE = 45.0
PLATE_Z = (145.0, 146.5)
VENT_DIAMETER = 29.7
WOOD_Z = (137.0, 145.0)
WOOD_LAYERS = 9
SUPPORT_OFFSET = 19.0
AXES = [(1,85,40),(2,55,140),(3,135,140),(4,225,130),(5,140,85),(6,50,85),(7,140,40)]
SERVICE_SIZE = (50.0,41.0)
OLD_FAN_IDS = {"FAN_MAX_BODY", "FAN_GUARD_TARGET", "FAN_GASKET"}

def point_segment_distance(p: tuple[float,float], a: list[float], b: list[float]) -> float:
    dx,dy=b[0]-a[0],b[1]-a[1]
    d=dx*dx+dy*dy
    t=0.0 if d==0 else max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def boundary_distance(p: tuple[float,float], rings: list[list[list[float]]]) -> float:
    return min(point_segment_distance(p,a,b) for ring in rings
               for a,b in zip(ring,ring[1:]+ring[:1]))

def contains_point(p: tuple[float,float], polygons: list[list[list[list[float]]]]) -> bool:
    return any(geom.point_in_polygon(p,rings) for rings in polygons)

def point_margin(p: tuple[float,float], polygons: list[list[list[list[float]]]]) -> float:
    return min(boundary_distance(p,rings) for rings in polygons)

def prism_hits(source: dict, rect: tuple[float,float,float,float],
               z: tuple[float,float], skip: set[str]) -> list[dict]:
    result=[]
    for index,solid in enumerate(source["solids"]):
        if solid["id"] in skip: continue
        frame=solid["axis"]
        if frame=="XY": overlap=max(0.0,min(z[1],solid["high"])-max(z[0],solid["low"])); r=rect
        elif frame=="XZ": overlap=max(0.0,min(rect[3],solid["high"])-max(rect[2],solid["low"])); r=(rect[0],rect[1],z[0],z[1])
        elif frame=="YZ": overlap=max(0.0,min(rect[1],solid["high"])-max(rect[0],solid["low"])); r=(rect[2],rect[3],z[0],z[1])
        else: raise ValueError(f"unsupported source extrusion frame {frame}")
        if overlap<=0: continue
        area=sum(geom.polygon_rect_area(poly,r) for poly in geom.geometry_polygons(solid["geometry"]))
        volume=area*overlap
        if volume>1e-6:
            result.append({"source_index":index,"solid_id":solid["id"],"overlap_volume_mm3":round(volume,6)})
    return result

def rectangle_gap(a: tuple[float,float,float,float],b: tuple[float,float,float,float]) -> float:
    dx=max(0.0,a[0]-b[1],b[0]-a[1]);dy=max(0.0,a[2]-b[3],b[2]-a[3])
    return math.hypot(dx,dy)

def audit(source: dict, raw_sha256: str) -> dict:
    if raw_sha256!=EXPECTED_SHA256: raise ValueError("canonical D7 SHA256 mismatch")
    if len(source.get("solids",[]))!=EXPECTED_SOLIDS: raise ValueError("expected 1,774 source solids")
    wood=sorted((s for s in source["solids"] if s["id"]=="BACK_WOOD" and s["axis"]=="XY"),key=lambda s:s["low"])
    if len(wood)!=WOOD_LAYERS or abs(wood[0]["low"]-137)>1e-8 or abs(wood[-1]["high"]-145)>1e-8:
        raise ValueError("expected all nine contiguous BACK_WOOD XY source slices from Z137 to Z145")
    if any(abs(a["high"]-b["low"])>1e-8 for a,b in zip(wood,wood[1:])):
        raise ValueError("BACK_WOOD source slices are not contiguous")
    layers=[geom.geometry_polygons(s["geometry"]) for s in wood]
    cx,cy=CENTER; radius=VENT_DIAMETER/2
    center=(cx,cy)
    opening_layers=[]
    for solid,polys in zip(wood,layers):
        is_inside=contains_point(center,polys)
        margin=point_margin(center,polys)
        opening_layers.append({"z_mm":[solid["low"],solid["high"]],"center_inside_wood":is_inside,
                               "center_to_nearest_material_boundary_mm":round(margin,6),
                               "full_circle_inside_wood":bool(is_inside and margin+1e-9>=radius)})
    supports=[]
    outer=layers[-1]
    for dx,dy in [(-SUPPORT_OFFSET,-SUPPORT_OFFSET),(SUPPORT_OFFSET,-SUPPORT_OFFSET),
                  (SUPPORT_OFFSET,SUPPORT_OFFSET),(-SUPPORT_OFFSET,SUPPORT_OFFSET)]:
        point=(cx+dx,cy+dy)
        per_layer=[contains_point(point,p) for p in layers]
        supports.append({"xy_mm":[point[0],point[1]],"inside_every_wood_layer":all(per_layer),
                         "outer_layer_boundary_distance_mm":round(point_margin(point,outer),6)})
    fan_rect=(cx-FAN_BODY[0]/2,cx+FAN_BODY[0]/2,cy-FAN_BODY[1]/2,cy+FAN_BODY[1]/2)
    plate_rect=(cx-PLATE_SIZE/2,cx+PLATE_SIZE/2,cy-PLATE_SIZE/2,cy+PLATE_SIZE/2)
    vent_square=(cx-radius,cx+radius,cy-radius,cy+radius)
    old_fan={s["id"] for s in source["solids"] if s["id"].startswith("FAN_")}
    fan_hits=prism_hits(source,fan_rect,FAN_BODY_Z,old_fan)
    plate_hits=prism_hits(source,plate_rect,PLATE_Z,old_fan|{"BACK_WOOD"})
    duct_hits=prism_hits(source,vent_square,WOOD_Z,old_fan|{"BACK_WOOD"})
    grille_hits=[h for h in duct_hits if h["solid_id"]=="REAR_GRILLE"]
    duct_fixed_hits=[h for h in duct_hits if h["solid_id"]!="REAR_GRILLE"]
    service=[]
    for number,x,y in AXES:
        reserve=(x-SERVICE_SIZE[0]/2,x+SERVICE_SIZE[0]/2,y-SERVICE_SIZE[1]/2,y+SERVICE_SIZE[1]/2)
        service.append({"axis":number,"plate_to_50x41_service_reserve_gap_mm":round(rectangle_gap(plate_rect,reserve),6)})
    outlet_area=math.pi*(29.3/2)**2
    vent_area=math.pi*radius**2
    all_ok=(all(x["full_circle_inside_wood"] for x in opening_layers)
            and all(x["inside_every_wood_layer"] for x in supports)
            and not fan_hits and not plate_hits and not duct_fixed_hits
            and min(x["plate_to_50x41_service_reserve_gap_mm"] for x in service)>0)
    return {
        "audit":"FG-M1 external fan and through-backwood vent candidate",
        "source_sha256":raw_sha256,"source_solid_count":len(source["solids"]),
        "candidate":{"center_xy_mm":list(CENTER),"sunon_screening_model":"MF30100V3-1000U-A99",
          "fan_body_mm":list(FAN_BODY),"fan_body_z_mm":list(FAN_BODY_Z),
          "rear_adapter_plate_mm":[PLATE_SIZE,PLATE_SIZE,PLATE_Z[1]-PLATE_Z[0]],"plate_z_mm":list(PLATE_Z),
          "backwood_vent_diameter_mm":VENT_DIAMETER,"backwood_z_mm":list(WOOD_Z),
          "vent_area_mm2":round(vent_area,4),"manufacturer_outlet_diameter_mm":29.3,
          "vent_area_over_outlet_area_ratio":round(vent_area/outlet_area,4),
          "adapter_support_centers_relative_mm":[[-19,-19],[19,-19],[19,19],[-19,19]],
          "support_hole_diameter":"NOT_ASSIGNED; fastener and wood substrate unqualified"},
        "site_revision_history":[
          {"xy_mm":[95,90],"result":"REJECTED","reason":"outermost source layer boundary is only 1.0mm from this center; insufficient for Ø29.7mm bore and associated support layout"},
          {"xy_mm":[220,40],"result":"SELECTED_FOR_REVIEW","reason":"full nine-layer aperture fit, all support centers in wood, full-D7 fixed-source clearance and service-reserve clearance"}],
        "backwood_layer_screens":opening_layers,"all_nine_full_vent_circles_in_material":all(x["full_circle_inside_wood"] for x in opening_layers),
        "adapter_support_centers":supports,"all_support_centers_inside_all_wood_layers":all(x["inside_every_wood_layer"] for x in supports),
        "source_3d_prism_intersections":{"external_fan_body":fan_hits,"adapter_plate_excluding_wood_contact":plate_hits,
           "vent_square_path_excluding_backwood":duct_hits,"vent_square_hits_removable_rear_grille":grille_hits,
           "vent_square_hits_fixed_nonwood":duct_fixed_hits},
        "service_reserve_clearance":service,
        "disposition":"CANDIDATE_SOURCE_GEOMETRY_PASS_NOT_THERMALLY_OR_MECHANICALLY_QUALIFIED" if all_ok else "FAIL_CANDIDATE_GEOMETRY",
        "limitations":["all FAN_* solids represent the original fan and hardware to be relocated; new guard and mounting hardware are not source modeled",
          "29.7mm backwood port is a new unapproved cut; panel strength, grain and edge breakout are not qualified",
          "adapter is a 45mm square positional envelope only; metal, thickness, holes, screws, gasket and retention are unresolved",
          "module keepouts use conditional 50x41mm reserved footprints, not measured assembled modules",
          "no inlet-flow area, pressure drop, closed-case temperature, noise, startup/stall current or service-use test",
          "catalog free-air values are not installed flow; no purchase, cutting or power authorization"],
        "release":{"G3_06":"OPEN","G2_07":"OPEN","G3_04":"WORKING","manufacturing_gates_closed":0,
                   "motor_efuse_en":"LOW","purchase":False,"cut":False,"power":False,"flash":False}}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("assembly_json",type=Path);parser.add_argument("--output",type=Path)
    args=parser.parse_args();raw=args.assembly_json.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    result=audit(json.loads(raw),digest);text=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text,encoding="utf-8")
    print(text,end="")
    if result["disposition"]=="FAIL_CANDIDATE_GEOMETRY":raise SystemExit(2)
if __name__=="__main__":main()
