#!/usr/bin/env python3
"""Find board-edge retainer windows clear of footprints and copper in Seeed EAGLE source."""
from __future__ import annotations
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

HERE=Path(__file__).resolve().parent
BOARD=HERE/'source'/'Stepper_Motor_Driver.brd'
OUT=HERE/'board_edge_capture_screen.json'
ACTIVE={'D1','D2','D3','D4','R1','R2','R3','R4','U1','C1','C2','J4','J5','SW2'}
CLEARANCE=0.30
# Lip windows are inside the PCB outline. Coordinates use EAGLE board datum (lower left).
WINDOWS={
    'north_long': {'rect_mm':[3.0,18.7,17.0,19.3], 'retainer_type':'removable edge lip study'},
    'south_short': {'rect_mm':[24.0,0.0,28.0,0.6], 'retainer_type':'removable edge lip study'},
}

def f(el,k): return float(el.get(k,'0'))
def rotate(x,y,deg):
    a=math.radians(deg);return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a))
def parse_rot(value):
    value=value or 'R0'
    if not value.startswith('R'): raise ValueError(f'unsupported element transform {value}')
    return int(value[1:].split()[0])%360
def box_points(x,y,dx,dy,deg):
    return [rotate(x+sx*dx/2,y+sy*dy/2,deg) for sx in (-1,1) for sy in (-1,1)]
def bounds(points,origin):
    return [min(origin[0]+x for x,y in points),min(origin[1]+y for x,y in points),
            max(origin[0]+x for x,y in points),max(origin[1]+y for x,y in points)]
def rects_overlap(a,b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
def find_hits(features, windows=WINDOWS, clearance=CLEARANCE):
    hits=[]
    for name,window in windows.items():
        rect=window['rect_mm']; expanded=[rect[0]-clearance,rect[1]-clearance,rect[2]+clearance,rect[3]+clearance]
        for ft in features:
            if rects_overlap(expanded,ft['bbox']): hits.append({'window':name,'ref':ft['ref'],'kind':ft['kind'],'feature_bbox_mm':ft['bbox']})
    return hits
def main():
    root=ET.parse(BOARD).getroot().find('./drawing/board'); assert root is not None
    elems={e.get('name'):e for e in root.findall('./elements/element')}
    packages={p.get('name'):p for lib in root.findall('./libraries/library') for p in lib.findall('./packages/package')}
    features=[]
    for ref in sorted(ACTIVE):
        e=elems[ref]; pkg=packages[e.get('package')]; angle=parse_rot(e.get('rot')); origin=(f(e,'x'),f(e,'y'))
        # Package tPlace line/circle art is only a body-outline proxy. Copper pads are exact source geometry.
        for w in pkg.findall('wire'):
            if w.get('layer')=='21':
                pts=[rotate(f(w,'x1'),f(w,'y1'),angle),rotate(f(w,'x2'),f(w,'y2'),angle)]
                bb=bounds(pts,origin); half=f(w,'width')/2
                features.append({'ref':ref,'kind':'package_tplace_proxy','bbox':[bb[0]-half,bb[1]-half,bb[2]+half,bb[3]+half]})
        for c in pkg.findall('circle'):
            if c.get('layer')=='21':
                cx,cy=rotate(f(c,'x'),f(c,'y'),angle);r=f(c,'radius')+f(c,'width')/2
                features.append({'ref':ref,'kind':'package_tplace_circle_proxy','bbox':[origin[0]+cx-r,origin[1]+cy-r,origin[0]+cx+r,origin[1]+cy+r]})
        for pad in pkg.findall('pad'):
            px,py=rotate(f(pad,'x'),f(pad,'y'),angle);d=f(pad,'diameter')
            features.append({'ref':ref,'kind':'through_hole_pad_copper_bound','bbox':[origin[0]+px-d/2,origin[1]+py-d/2,origin[0]+px+d/2,origin[1]+py+d/2]})
        for smd in pkg.findall('smd'):
            if smd.get('layer') not in ('1','16'): continue
            local_rot=parse_rot(smd.get('rot','R0'))
            # Rotate SMD's own pad outline before element rotation.
            x,y=rotate(f(smd,'x'),f(smd,'y'),angle)
            pad_angle=angle+local_rot
            dx,dy=f(smd,'dx'),f(smd,'dy')
            if pad_angle%180: dx,dy=dy,dx
            cx,cy=origin[0]+x,origin[1]+y
            features.append({'ref':ref,'kind':'smd_copper_bound','bbox':[cx-dx/2,cy-dy/2,cx+dx/2,cy+dy/2]})
    hits=find_hits(features)
    assert not hits, json.dumps(hits,indent=2)
    # All proposed lip windows are contained within the official nominal outline.
    for w in WINDOWS.values():
        x0,y0,x1,y1=w['rect_mm'];assert 0<=x0<x1<=35 and 0<=y0<y1<=19.3
    report={
      'status':'SOURCE_GEOMETRY_EDGE_WINDOW_SCREEN_ONLY',
      'board_source':'source/Stepper_Motor_Driver.brd',
      'board_sha256':hashlib.sha256(BOARD.read_bytes()).hexdigest(),
      'nominal_board_outline_mm':[35.0,19.3],
      'source_elements_checked':sorted(ACTIVE),
      'clearance_from_source_tplace_and_copper_bounds_mm':CLEARANCE,
      'candidate_windows':WINDOWS,
      'source_geometry_hits':hits,
      'board_retention':'NOT_DESIGNED; windows identify possible lip-contact regions only',
      'limitations':['EAGLE tPlace lines are only component-body proxies, not vendor 3D/courtyard data',
        'no component-height, solder-joint, board-thickness or process-tolerance evidence',
        'retainer material, spring behavior, insertion path, screw/tool access, shock and vibration unverified',
        'motor and driver PCB Z stack and D7 55mm extraction sweep not checked'],
      'manufacturing_release':False
    }
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('PASS: two PCB-edge lip windows clear archived source tPlace and copper bounds by 0.30 mm')
    print('HOLD: windows are not a retaining mechanism; component height, slot, service and D7 integration remain open')
if __name__=='__main__': main()
