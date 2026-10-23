#!/usr/bin/env python3
"""現行CSVから一台用設計図・組立説明図をPDF/SVGで出力する。

実行例: python3 -B docs/08-manufacturing/generate_drawing_set.py --font /path/to/NotoSansJP.ttf
依存: reportlab, pypdf, fonttools。現物未確認の固定穴を推定しない。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont as FontToolsFont
from fontTools.varLib.instancer import instantiateVariableFont
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "drawing-set-v0.1"
MECH = ROOT / "docs/03-mechanical"
ELEC = ROOT / "docs/04-electronics"
W, H = 1680, 1188
K = 72 / 25.4 / 4  # SVG: 4 units/mm, PDF: A3 landscape.
DATE = "2026-10-23"
BASE = "033f460"
C = dict(ink="#23383d", mute="#607479", teal="#327e87", pale="#eaf3f3",
         gold="#c39743", brown="#945d31", wood="#73513d", grey="#a5b3b6",
         line="#cfdbdc", red="#b65340", blue="#326fa0", white="#ffffff")


class Sheet:
    """A single primitive stream produces both vector PDF and editable SVG."""
    def __init__(self, pdf, code, title, subtitle):
        self.pdf, self.code = pdf, code
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 {W} {H}">',
                    f'<title>{html.escape(code + " " + title)}</title>',
                    '<desc>一台用の設計参照・組立説明図。寸法単位mm。実機未受入。歯形と分解間隔は模式。</desc>']
        pdf.saveState()
        pdf.scale(K, K)
        self.rect(0, 0, W, H, C["white"], None)
        self.rect(0, 0, 21, H, C["teal"], None)
        self.text(58, 68, "FOREST GUARDIAN  /  DIALCANVAS DESK EDITION", 17, C["mute"])
        self.text(58, 118, f"{code}   {title}", 34, bold=True)
        self.text(58, 153, subtitle, 17, C["mute"])
        self.line(58, 180, W-58, 180, C["line"])
        self.line(58, 1112, W-58, 1112, C["line"])
        self.text(58, 1145, f"単位 mm  |  形状・組付けの設計参照  |  基準 {BASE} + 図面整合修正", 15, C["mute"])
        self.text(W-60, 1145, f"{DATE}  /  v0.1  /  {code}", 15, C["mute"], anchor="end")
        self.text(58, 1171, "完成品の実機受入は未実施。印刷物を実寸の切削テンプレートとして使わない。", 13, C["mute"])

    def style(self, fill, stroke, width=1, dash=None):
        if fill: self.pdf.setFillColor(fill)
        if stroke: self.pdf.setStrokeColor(stroke)
        self.pdf.setLineWidth(width)
        self.pdf.setDash(dash or [])

    def rect(self, x, y, w, h, fill=None, stroke=C["ink"], width=1, dash=None):
        self.style(fill, stroke, width, dash)
        self.pdf.rect(x, H-y-h, w, h, fill=int(bool(fill)), stroke=int(bool(stroke)))
        ds = f' stroke-dasharray="{",".join(map(str,dash))}"' if dash else ""
        self.svg.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"{ds}/>')

    def line(self, x1, y1, x2, y2, color=C["ink"], width=1.3, dash=None):
        self.style(None, color, width, dash)
        self.pdf.line(x1, H-y1, x2, H-y2)
        ds = f' stroke-dasharray="{",".join(map(str,dash))}"' if dash else ""
        self.svg.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"{ds}/>')

    def poly(self, pts, fill=None, stroke=C["ink"], width=1.3):
        self.style(fill, stroke, width)
        path = self.pdf.beginPath()
        path.moveTo(pts[0][0], H-pts[0][1])
        for x, y in pts[1:]: path.lineTo(x, H-y)
        path.close()
        self.pdf.drawPath(path, fill=int(bool(fill)), stroke=int(bool(stroke)))
        data = " ".join(f"{x:.3f},{y:.3f}" for x,y in pts)
        self.svg.append(f'<polygon points="{data}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')

    def circle(self, x, y, r, fill=None, stroke=C["ink"], width=1.3):
        self.style(fill, stroke, width)
        self.pdf.circle(x, H-y, r, fill=int(bool(fill)), stroke=int(bool(stroke)))
        self.svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')

    def text(self, x, y, value, size=18, color=C["ink"], bold=False, anchor="start"):
        font = "FG-Bold" if bold else "FG"
        self.style(color, None)
        self.pdf.setFont(font, size)
        value = str(value)
        if anchor == "middle": self.pdf.drawCentredString(x, H-y, value)
        elif anchor == "end": self.pdf.drawRightString(x, H-y, value)
        else: self.pdf.drawString(x, H-y, value)
        self.svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Noto Sans JP,Noto Sans CJK JP,sans-serif" font-size="{size}" font-weight="{600 if bold else 400}" text-anchor="{anchor}" fill="{color}">{html.escape(value)}</text>')

    def para(self, x, y, value, width, size=18, leading=28, color=C["ink"]):
        line = ""
        for char in value:
            if char == "\n" or pdfmetrics.stringWidth(line+char, "FG", size) > width:
                self.text(x, y, line, size, color)
                y += leading
                line = "" if char == "\n" else char
            else: line += char
        if line:
            self.text(x, y, line, size, color)
            y += leading
        return y

    def arrow(self, x1, y1, x2, y2, color=C["teal"], width=2):
        self.line(x1, y1, x2, y2, color, width)
        a = math.atan2(y2-y1, x2-x1)
        self.poly([(x2,y2),(x2-11*math.cos(a-.4),y2-11*math.sin(a-.4)),
                   (x2-11*math.cos(a+.4),y2-11*math.sin(a+.4))],color,None)

    def dim(self, x1, y1, x2, y2, label, dy=-12):
        self.arrow(x1,y1,x2,y2,C["mute"],1)
        self.arrow(x2,y2,x1,y1,C["mute"],1)
        self.text((x1+x2)/2,(y1+y2)/2+dy,label,16,C["ink"],anchor="middle")

    def box(self, x, y, w, h, title, lines=(), color=C["teal"]):
        self.rect(x,y,w,h,C["pale"],C["line"])
        self.rect(x,y,6,h,color,None)
        self.text(x+22,y+35,title,22,color,bold=True)
        yy = y+70
        for value in lines: yy = self.para(x+22,yy,value,w-44,17,26)

    def number(self, x, y, value):
        self.circle(x,y,20,C["teal"],None)
        self.text(x,y+7,str(value),21,C["white"],bold=True,anchor="middle")

    def finish(self):
        self.svg.append("</svg>\n")
        path = OUT / f"{self.code}.svg"
        path.write_text("\n".join(self.svg),encoding="utf-8")
        self.pdf.restoreState()
        self.pdf.showPage()


def table(s, x, y, widths, rows, row_h=38, size=17):
    for i,row in enumerate(rows):
        xx = x
        for w,value in zip(widths,row):
            s.rect(xx,y+i*row_h,w,row_h,C["pale"] if i==0 else C["white"],C["line"],.8)
            s.text(xx+12,y+i*row_h+row_h*.68,value,size,C["teal"] if i==0 else C["ink"],bold=(i==0))
            xx += w
    return y+len(rows)*row_h


def gear(s,x,y,r,color):
    pts=[]
    for i in range(80):
        a=2*math.pi*i/80
        rr=r*(1 if i%4 in (1,2) else .84)
        pts.append((x+rr*math.cos(a),y+rr*math.sin(a)))
    s.poly(pts,color,C["brown"],.8)
    s.circle(x,y,r*6/11,None,C["brown"],.8)
    s.circle(x,y,r*3/11,C["white"],C["brown"],.8)


def dims_rect(s,x,y,w,h,wl,hl):
    s.line(x,y-7,x,y-43,C["mute"],.8)
    s.line(x+w,y-7,x+w,y-43,C["mute"],.8)
    s.dim(x,y-30,x+w,y-30,wl)
    s.line(x-7,y,x-54,y,C["mute"],.8)
    s.line(x-7,y+h,x-54,y+h,C["mute"],.8)
    s.dim(x-40,y,x-40,y+h,hl,dy=0)


def overview(c,rows):
    s=Sheet(c,"D00","全体設計・基準寸法","単一モーター / 28歯車・27軸は今回の一台の配置例 / 最新ケース見積図 v0.4")
    ox,oy,k=135,285,3
    s.rect(ox,oy,270*k,205*k,"#f0e8df",C["wood"],3)
    # P1 aperture: the nominal lower wave points from the case parts CSV.
    wave=[(258,189),(232,180),(182,191),(135,193),(88,191),(38,180),(12,189)]
    points=[(12,12),(258,12)]
    # Smooth visual interpolation of the quote-drawing guide points; the quote sheet remains authoritative.
    for i in range(len(wave)-1):
        p0,p1,p2,p3=wave[max(0,i-1)],wave[i],wave[i+1],wave[min(len(wave)-1,i+2)]
        for step in range(16):
            t=step/16
            points.append(tuple(.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t*t+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t*t*t) for j in (0,1)))
    points.append(wave[-1])
    s.poly([(ox+x*k,oy+y*k) for x,y in points],C["white"],C["wood"],2)
    for layer,col in [("B",C["brown"]),("A",C["gold"])]:
        for row in rows:
            if row["layer"]==layer:
                gear(s,ox+float(row["case_x_mm"])*k,oy+float(row["case_y_mm"])*k,11*k,col)
    cx,cy=ox+135*k,oy+102.5*k
    s.circle(cx,cy,57.5*k,C["pale"],C["teal"],2)
    s.circle(cx,cy,43.8*k,"#f7f5ed",C["teal"],1.5)
    for a in range(12):
        r1,r2=37*k,40*k
        angle=a*math.pi/6
        s.line(cx+r1*math.sin(angle),cy-r1*math.cos(angle),cx+r2*math.sin(angle),cy-r2*math.cos(angle),C["teal"],2)
    s.line(cx,cy,cx-45,cy-64,C["teal"],5)
    s.line(cx,cy,cx+63,cy-65,C["teal"],3)
    s.circle(cx,cy,5,C["gold"],None)
    dims_rect(s,ox,oy,810,615,"270","205")
    s.text(ox,oy-80,"正面図 / 歯形は模式、位置は軸CSVから転記",21,bold=True)
    s.text(ox,945,"P1: 9厚 / G2前面ガード: 3厚 / PC支持板A・B: 各8厚",18)
    s.text(ox,978,"前面枠下辺の加工輪郭・許容差は、続くケース見積図A01/A02を参照。",17,C["mute"])
    s.text(ox,1017,"表示器: LCD有効径 Ø87.60 / モジュール外径 Ø115。",18)
    x,y,k=1110,300,1.8
    s.text(x,y-90,"側面図 / Z基準",23,bold=True)
    s.rect(x,y,172*k,205*k,"#f0e8df",C["wood"],2)
    z0=x+12*k
    for z1,z2,col in [(-3,0,C["pale"]),(29,37,C["teal"]),(70,78,C["teal"]),(148,160,C["wood"])]:
        s.rect(z0+z1*k,y,(z2-z1)*k,205*k,col,C["ink"],1)
    for z,label in [(0,"0"),(29,"A"),(70,"B"),(148,"148")]:
        s.line(z0+z*k,y-10,z0+z*k,y+205*k+12,C["mute"],.8,[5,4])
        s.text(z0+z*k,y+205*k+36,label,15,anchor="middle")
    s.dim(x,y-40,x+172*k,y-40,"奥行 172")
    s.arrow(z0,y+440,z0+148*k,y+440)
    s.text(x,y+477,"前ガード内面 z=0 → 背板内面 z=148",16)
    s.box(1050,865,560,195,"図面の読み方",[
        "寸法表記を優先。CAD小数桁を一律の加工公差にしない。",
        "未確認の穴・ねじ長さは『現物合わせ』として記載。",
        "木工接合・前ガード保持は工房の見積回答で具体化。"],C["teal"])
    s.finish()


def plate(c,rows,layer):
    code="D03" if layer=="A" else "D04"
    s=Sheet(c,code,f"支持板 {layer} / 穴位置表","板左上原点 / +X右・+Y下 / 全体外形 252 × 187 × 8 / ブッシュ穴 14か所")
    data=[r for r in rows if r["layer"]==layer]
    ox,oy,k=140,300,3
    s.rect(ox,oy,252*k,187*k,C["pale"],C["teal"],2)
    if layer=="A":
        s.circle(ox+126*k,oy+93.5*k,59.5*k,C["white"],C["teal"],1.3)
        for x,y in [(46,13.5),(206,13.5),(46,173.5),(206,173.5)]:
            s.circle(ox+x*k,oy+y*k,1.7*k,C["gold"],C["brown"],1)
        s.text(ox+126*k,oy+93.5*k,"中央開口 Ø119",23,C["teal"],anchor="middle")
    else:
        s.rect(ox+66*k,oy+33.5*k,120*k,120*k,C["white"],C["teal"],1.3)
        s.text(ox+126*k,oy+93.5*k,"中央開口 120 × 120",23,C["teal"],anchor="middle")
    for row in data:
        x=ox+float(row["plate_x_mm"])*k; y=oy+float(row["plate_y_mm"])*k
        s.circle(x,y,4*k,"#b8dadd",C["teal"],1)
        s.line(x-5,y,x+5,y,C["ink"],.7);s.line(x,y-5,x,y+5,C["ink"],.7)
        s.text(x+16,y+5,row["gear_id"],15)
    dims_rect(s,ox,oy,252*k,187*k,"252","187")
    s.number(ox,oy,0)
    s.arrow(ox,oy+187*k+46,ox+95,oy+187*k+46)
    s.text(ox+110,oy+187*k+52,"+X",17)
    table(s,1000,245,[100,220,220],[("ID","X","Y")]+[(r["gear_id"],r["plate_x_mm"],r["plate_y_mm"]) for r in data],38,18)
    y=915
    notes=["OILES 80B-0608: ID6 / OD8 / 長さ8。指定穴はカタログ推奨 Ø8 H7。",
           "ブッシュは板へ圧入。組立時に割れ・白化・軸の引っ掛かりを確認する。",
           "ケース外側左上から板原点は (+9,+9)。軸位置はCSVと同一。"]
    if layer=="A": notes.append("金色4穴は表示キャリア用 Ø3.4: (46,13.5),(206,13.5),(46,173.5),(206,173.5)。")
    else: notes.append("B00はA00と同軸。共通軸を両板へ通し、箱を閉じる前に軸通りを確認する。")
    for note in notes:
        y=s.para(140,y,note,1420,18,31)
    s.finish()


def axial(c):
    s=Sheet(c,"D05","軸方向断面・歯車の向き","前→後を左→右に表示 / 実Z位置に比例した模式断面 / 歯先・止めねじ形状は省略")
    x0,k=180,8.2
    for z in [0,23,29,37,46,52,55,61,70,78,84,91,106,108,141,148,160]:
        xx=x0+z*k
        s.line(xx,245,xx,995,C["line"],.7,[3,5])
        if z in [0,29,37,55,70,84,108,141,148,160]: s.text(xx,225,str(z),14,anchor="middle")
    s.arrow(x0,258,x0+160*k,258)
    s.text(1510,249,"+Z",17)
    s.text(70,355,"A単軸",23,bold=True)
    s.text(70,385,"13組",17,C["mute"])
    s.text(70,585,"B単軸",23,bold=True)
    s.text(70,615,"13組",17,C["mute"])
    s.text(65,815,"共通軸",23,bold=True)
    s.text(65,846,"1本・2歯車",16,C["mute"])
    def band(z1,z2,y,h,color): s.rect(x0+z1*k,y,(z2-z1)*k,h,color,C["ink"],1)
    def label(z1,z2,y,name,above=True):
        mid=x0+(z1+z2)/2*k
        yy=y-30 if above else y+103
        s.text(mid,yy,name,16,anchor="middle")
        s.line(mid,yy+6 if above else yy-18,mid,y if above else y+70,C["mute"],.8)
    for y,shaft,parts in [
        (340,(23,53),[(23,28,"カラー",C["grey"]),(28,29,"W",C["gold"]),(29,37,"A板",C["pale"]),(37,38,"W",C["gold"]),(38,46,"ボス",C["gold"]),(46,52,"歯面A",C["gold"])]),
        (570,(55,85),[(55,61,"歯面B",C["brown"]),(61,69,"ボス",C["brown"]),(69,70,"W",C["gold"]),(70,78,"B板",C["pale"]),(78,79,"W",C["gold"]),(79,84,"カラー",C["grey"])])]:
        for i,(a,b,name,col) in enumerate(parts):
            band(a,b,y,70,col)
            if name!="W": label(a,b,y,name,i%2==0)
        band(*shaft,y+29,12,C["ink"])
        s.dim(x0+shaft[0]*k,y+145,x0+shaft[1]*k,y+145,f"Ø6 h7 × 30   /   z={shaft[0]}…{shaft[1]}")
    y=805
    for a,b,col in [(29,37,C["pale"]),(37,38,C["gold"]),(38,46,C["gold"]),(46,52,C["gold"]),
                    (55,61,C["brown"]),(61,69,C["brown"]),(69,70,C["gold"]),(70,78,C["pale"]),
                    (84,106,C["grey"]),(108,141,C["teal"])]: band(a,b,y,70,col)
    band(26,91,y+29,12,C["ink"])
    band(99,108,y+32,6,C["ink"])
    s.text(x0+119*k,y+42,"#4411",20,C["white"])
    s.dim(x0+26*k,y+148,x0+91*k,y+148,"共通軸 Ø6 h7 × 65 / z=26…91")
    s.text(x0+95*k,y-28,"継手 84…106",18,anchor="middle")
    s.text(x0+124*k,y-28,"モーター 108…141",18,anchor="middle")
    s.dim(x0+141*k,y+110,x0+148*k,y+110,"7",dy=27)
    s.text(180,1025,"W = POM 0612-10、各1mm。A00/B00にはカラーを置かず、ギア側Wを2枚使用。",18)
    s.text(180,1060,"モーター取付面 z=108。支持金具の形状・固定穴・ねじは現行ソースに未定義（製作用詳細図の対象外）。",18,C["red"])
    s.finish()


def carrier(c):
    s=Sheet(c,"D06","表示器キャリア・固定スタック","基板外周M4穴 75 × 78.5 / 4本腕の中央は開放 / 支持板Aのアンカーへ接続")
    cx,cy,k=445,610,3.3
    s.rect(cx-95*k,cy-95*k,190*k,190*k,None,C["line"],1,[8,6])
    s.circle(cx,cy,59.5*k,None,C["teal"],1.2)
    s.circle(cx,cy,57.5*k,None,C["grey"],1)
    for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        x1,y1=cx+sx*37.5*k,cy+sy*39.25*k
        x2,y2=cx+sx*80*k,cy+sy*80*k
        s.line(x1,y1,x2,y2,C["gold"],18*k)
        s.circle(x1,y1,9*k,C["gold"],None);s.circle(x2,y2,9*k,C["gold"],None)
        s.circle(x1,y1,2.25*k,C["white"],C["brown"])
        s.circle(x2,y2,1.7*k,C["white"],C["brown"])
    s.line(cx,cy-110*k,cx,cy+110*k,C["mute"],.8,[6,5])
    s.line(cx-110*k,cy,cx+110*k,cy,C["mute"],.8,[6,5])
    s.text(cx,cy-122*k,"中心原点 / +X右 / +Y上",20,anchor="middle")
    s.dim(cx-37.5*k,cy-39.25*k-44,cx+37.5*k,cy-39.25*k-44,"75")
    s.dim(cx+37.5*k+75,cy-39.25*k,cx+37.5*k+75,cy+39.25*k,"78.5",dy=0)
    s.dim(cx-80*k,cy+80*k+75,cx+80*k,cy+80*k+75,"アンカー 160")
    s.box(920,235,680,260,"キャリアの名目寸法",[
        "透明PC 3厚。190 × 190素材から4本腕を切出し（4本で1組）。",
        "腕幅18。M4側: 中心X=±37.50 / Y=±39.25、穴 Ø4.5。",
        "M3側: 中心X/Y=±80、穴 Ø3.4。外形最大±89。",
        "外周の基板固定座へ接続し、中央の部品・端子域は開ける。"])
    s.box(920,530,680,195,"基板側: M4 × 8 / 4本",[
        "ねじ頭 → PC 3 → POM絶縁スペーサ2 → 基板M4取付座。",
        "公称掛かり = 8 - 3 - 2 = 3。底付きと掛かりは組立時に確認。",
        "M4ねじへ別座金を追加すると掛かりが減るため追加しない。"])
    s.box(920,755,680,205,"支持板側: M3 × 25 / 4組",[
        "PCキャリア3 → スペーサ合計7 → 支持板A 8。",
        "7mmは6mm POMスペーサ + 1mm座金。外側はM3平座金と緩み止めナット。",
        "PCを割らない手締め。根拠のない締付トルクは指定しない。"])
    s.text(140,1070,"前後: 基板 z=1.5…17 / 2mmスペーサ / PCキャリア19…22 / 7mm支持 / A板29…37。",18)
    s.finish()


def rear(c):
    s=Sheet(c,"D07","背面電装・サービス板","P4を内側から見る / ケース中心(0,0)、+X右・+Y上 / 破線は部品外形ではなく配置予約")
    ox,oy,k=140,310,3
    def p(x,y): return ox+(x+135)*k,oy+(102.5-y)*k
    s.rect(ox,oy,810,615,"#f5eee6",C["wood"],2)
    for x,y in [(30,6),(135,6),(240,6),(30,199),(135,199),(240,199),(6,102.5),(264,102.5)]:
        s.circle(ox+x*k,oy+y*k,1.75*k,C["white"],C["wood"],1)
    tx,ty=p(-115,35)
    s.rect(tx,ty,230*k,120*k,C["pale"],C["teal"],2)
    for x,y in [(-105,25),(105,25),(-105,-75),(105,-75)]:
        xx,yy=p(x,y);s.circle(xx,yy,1.75*k,C["white"],C["teal"])
    for x0,w,title in [(-115,125,"電源・作業予約 125 × 120"),(15,100,"端子予約 100 × 120")]:
        xx,yy=p(x0,35);s.rect(xx,yy,w*k,120*k,None,C["mute"],1,[6,5])
        s.text(xx+12,yy+27,title,14)
    # Point locations are specified; silhouettes/pad holes are deliberately not invented.
    for x,y,name in [(-86,58,"HUSB238"),(-48,58,"#2851"),(35,68,"TMC2209"),(85,50,"DS3231")]:
        xx,yy=p(x,y);s.circle(xx,yy,6,C["teal"],None)
        s.text(xx,yy-20,name,17,anchor="middle")
        s.text(xx,yy+25,f"({x:+g},{y:+g})",14,anchor="middle")
    xx,yy=p(-86,78);s.rect(xx-12*k,yy-9.5*k,24*k,19*k,C["white"],C["teal"],1)
    s.text(xx,yy-38,"USB-C",16,anchor="middle")
    for x,name in [(22,"+15V"),(65,"GND")]:
        xx,yy=p(x,20);s.rect(xx,yy,35*k,52.8*k,None,C["gold"],1.5,[6,4])
        s.text(xx+17.5*k,yy+65,"221-415",14,anchor="middle")
        s.text(xx+17.5*k,yy+90,"221-505",14,anchor="middle")
        s.text(xx+17.5*k,yy+119,name,17,C["teal"],bold=True,anchor="middle")
    xx,yy=p(-100,-5);s.text(xx,yy,"DFR0758 / DFR1015",19,C["teal"])
    s.text(xx,yy+36,"結束保持 / スロットは現物合わせ",16)
    xx,yy=p(22,-58);s.text(xx,yy,"ヒューズリード3枝",17)
    s.text(xx,yy+32,"サービス板へ別々に結束",14)
    s.text(140,980,"サービス板: 230 × 120 × 3 / 中心 (0,-25) / 板内の固定穴中心: X=±105、Y=±50。",17)
    s.text(140,1010,"板の4穴のみ Ø3.5。P4木部へは位置を写し、実材・ねじに合う下穴を加工する。",17)
    s.box(1010,245,590,235,"標準金物の選択",[
        "HUSB238 / RTC / TMC: M2.5を使用。点数は2 / 2 / 4。",
        "#2851: M2 × 12ねじ2本、M2ナット、3mmナイロンスペーサ。",
        "WAGO取付台: 各2点、計4本のM3ねじ・座金・ナット。"])
    s.box(1010,510,590,260,"現物から決めるもの",[
        "小型PC絶縁パッド4枚の外形、基板穴位置、P4への固定位置。",
        "M2.5 / WAGO M3のねじ長さ、DFR0758の結束スロット。",
        "P4の下穴径・深さは指定しない。板・パッドを置いて転記する。",
        "各パッドは木ねじ3.1 × 12を2本、サービス板は4本で固定。"],C["brown"])
    s.box(1010,800,590,245,"カバーを閉じる前に",[
        "+15V / GNDの221-415を混同しない。両方にラベルを付ける。",
        "カバー側と本体側の線を別の結束点で保持し、開閉余長を残す。",
        "モーター後方7mmは線の曲げ成立を保証する値ではない。"])
    s.finish()


def power(c):
    s=Sheet(c,"D08","電源の接続図","線は接続関係を示す / 配線長は実際の通路へ合わせる / PD 15V・2A設定 / 旧7軸回路は使用しない")
    def device(x,y,w,name,sub="",color=C["teal"]):
        s.rect(x,y,w,85,C["pale"],color,1.5)
        s.text(x+w/2,y+34,name,20,color,bold=True,anchor="middle")
        if sub:s.text(x+w/2,y+65,sub,15,anchor="middle")
    nodes=[(65,205,"Anker A2147","PD 30W"),(315,205,"Neutrik USB-C","NAUSBC-5G-FL10"),
           (565,205,"HUSB238 #5807","15V / 2A"),(815,180,"3Aヒューズ","MINI 297"),(1040,285,"WAGO +15V","221-415")]
    for x,w,name,sub in nodes:device(x,235,w,name,sub)
    for (x,w,*_), (x2,*_) in zip(nodes,nodes[1:]):s.arrow(x+w,277,x2-8,277,C["red"])
    s.line(1325,277,1450,277,C["red"],2.5)
    s.line(1450,277,1450,355,C["red"],2.5)
    s.line(1450,355,130,355,C["red"],2.5)
    s.line(130,355,130,852,C["red"],2.5)
    rows=[(430,"DFR0758","標準5V / USB-A","A-C 0.3m","MPA-ACECSS03BK","3.4C 表示器","USB TO UART"),
          (610,"DFR1015","9Vへ設定","2A → SPST","モーター専用枝","TMC2209 VM","#4411へ4芯・2相"),
          (790,"Pololu #2851","5V補助","2A → SPST","LED専用枝","FIT0836 LED","約330mm使用")]
    for y,a,aa,b,bb,d,dd in rows:
        s.arrow(130,y+42,240,y+42,C["red"],2.3)
        device(250,y,290,a,aa)
        device(650,y,335,b,bb,C["brown"])
        device(1120,y,365,d,dd)
        s.arrow(540,y+42,640,y+42,C["red"],2)
        s.arrow(985,y+42,1110,y+42,C["red"],2)
        s.text(390,y+119,"入力GND → G0",16,C["blue"],anchor="middle")
    # TVS is a parallel shunt at VM, not an inline element.
    s.line(1090,652,1090,695,C["red"],1.7)
    s.rect(1040,695,170,40,C["white"],C["brown"],1)
    s.text(1125,723,"SMBJ12A",16,anchor="middle")
    s.text(1240,725,"K=VM / A=G0（並列）",16,C["brown"])
    s.line(1090,735,1090,757,C["blue"],1.7)
    s.text(1090,780,"G0",15,C["blue"],anchor="middle")
    s.box(65,962,745,125,"G0 = WAGO共通GND",[
        "HUSB238、3つの降圧入力、TMCの戻りを分岐点まで個別に配線。"],C["blue"])
    s.box(845,962,765,125,"出力側の戻り",[
        "表示: USBケーブル / LED: #2851 GND / 信号: 3.4C GNDと共通化。"],C["blue"])
    s.finish()


def signals(c):
    s=Sheet(c,"D09","制御線・モーター線の接続","GPIO番号は信号名。40ピン端子の物理ピン番号ではない / VIOとRTCは3.3V / UARTは未使用")
    rows=[("3.4C側","接続先","用途"),
          ("GPIO4","TMC2209 STEP","STEP → GNDへ10kΩ"),
          ("GPIO5","TMC2209 DIR","回転方向"),
          ("GPIO32","TMC2209 ENN","ENN → VIOへ10kΩ / HIGHで禁止"),
          ("3.3V / GND","TMC2209 VIO / GND","ロジック電源 / モーター戻りは別配線"),
          ("GPIO28 / GPIO29","DS3231 SDA / SCL","I²C 0x68"),
          ("3.3V / GND","DS3231 VCC / GND","CR1220はDS3231のホルダーへ"),
          ("GPIO2 / GPIO3","EC11 A / B","COM → GND / 内部pull-up"),
          ("GPIO21","EC11 SW","SW COM → GND / 内部pull-up")]
    table(s,70,225,[300,490,740],rows,53,20)
    s.text(70,765,"#4411の4本は巻線抵抗で2相へ分け、色に依存せず両端を表示する。",23,bold=True)
    for i,(name,end) in enumerate([("A1","1A"),("A2","1B"),("B1","2A"),("B2","2B")]):
        y=825+i*50
        s.text(95,y+6,f"#4411 {name}",18)
        s.line(270,y,520,y,C["ink"],2)
        s.rect(470,y-12,120,24,"#e4e7e6",C["ink"],1)
        s.line(590,y,880,y,C["ink"],2)
        s.text(920,y+6,f"AWG22 → TMC {end}",18)
        if i==0:s.text(530,y-31,"個別はんだ + 接着剤付き熱収縮",16,anchor="middle")
    s.box(1200,755,410,310,"線の固定",[
        "4本を個別に絶縁。TRPW6.4-2.0-10を各約25mm使用。",
        "端子・はんだ部と離れた点へ結束。接続部へ引張りを掛けない。",
        "PC接続時は内部USB給電線を外す。モーターVMをOFFにする。"])
    s.text(70,1070,"初期駆動: MS1/MS2開放で1/8、SPRD開放でStealthChop、0.30A RMS/相を評価開始点とする。",18)
    s.finish()


def exploded(c,rows):
    s=Sheet(c,"A00","分解組立図・全体構成","前側を左下、後側を右上へ展開 / 分解間隔は説明用 / ケースの側板・上下板の組付けはA02を参照")
    def p(x,y,z):return 90+1.3*x+1.44*z,520+.4*x+1.1*y-.5*z
    def plate3d(z,x,y,w,h,opening=False,wood=False):
        pts=[p(x,y,z),p(x+w,y,z),p(x+w,y+h,z),p(x,y+h,z)]
        if opening and wood:
            # Draw the four rails, preserving the open window instead of painting over the contents.
            for xx,yy,ww,hh in [(x,y,w,13),(x,y+h-13,w,13),(x,y+13,13,h-26),(x+w-13,y+13,13,h-26)]:
                s.poly([p(xx,yy,z),p(xx+ww,yy,z),p(xx+ww,yy+hh,z),p(xx,yy+hh,z)],"#e5d2bf",C["wood"],1.3)
        else:s.poly(pts,"#f3eade" if wood else None,C["wood"] if wood else C["teal"],1.7)
    def circle3d(x,y,z,r,fill=None,color=C["teal"]):
        s.poly([p(x+r*math.cos(a*math.pi/24),y+r*math.sin(a*math.pi/24),z) for a in range(48)],fill,color,1.3)
    def gear3d(x,y,z,col):
        points=[]
        for i in range(80):
            a=2*math.pi*i/80;r=11 if i%4 in (1,2) else 9.2
            points.append(p(x+r*math.cos(a),y+r*math.sin(a),z))
        s.poly(points,col,C["brown"],.8)
        circle3d(x,y,z,3,C["white"],C["brown"])
    # Back-to-front paint order preserves the exploded plane boundaries.
    plate3d(690,0,0,270,205,wood=True)
    s.poly([p(20,67.5,690),p(250,67.5,690),p(250,187.5,690),p(20,187.5,690)],C["pale"],C["teal"],1)
    xx,yy=p(40,110,690);s.text(xx,yy,"背面電装 / D07",18)
    s.poly([p(125,24.5,550),p(145,24.5,550),p(145,44.5,550),p(125,44.5,550)],C["teal"],C["ink"],1.4)
    s.poly([p(145,24.5,550),p(145,24.5,583),p(145,44.5,583),p(145,44.5,550)],C["grey"],C["ink"],1.2)
    a,b=p(135,34.5,515);xx,yy=p(135,34.5,550);s.line(a,b,xx,yy,C["ink"],7)
    plate3d(460,9,9,252,187)
    s.poly([p(75,42.5,460),p(195,42.5,460),p(195,162.5,460),p(75,162.5,460)],None,C["teal"],1)
    for layer,z,col in [("B",370,C["brown"]),("A",290,C["gold"])]:
        for row in rows:
            if row["layer"]==layer:
                gear3d(float(row["case_x_mm"]),float(row["case_y_mm"]),z,col)
    plate3d(220,9,9,252,187)
    circle3d(135,102.5,220,59.5)
    for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        xx,yy=p(135+sx*37.5,102.5+sy*39.25,135)
        a,b=p(135+sx*80,102.5+sy*80,135)
        s.line(xx,yy,a,b,C["gold"],10)
    circle3d(135,102.5,100,57.5,C["pale"])
    circle3d(135,102.5,100,43.8,"#f7f5ed")
    xx,yy=p(135,102.5,100);s.text(xx-25,yy+6,"3.4C",21,anchor="middle")
    plate3d(40,0,0,270,205)
    plate3d(0,0,0,270,205,opening=True,wood=True)
    seq=[(0,1),(40,2),(100,3),(220,4),(290,5),(370,6),(460,7),(550,8),(690,9)]
    for z,n in seq:
        xx,yy=p(0,0,z);s.number(xx-12,yy-28,n)
    s.arrow(190,900,1430,385,C["mute"],1.5)
    s.text(1480,380,"後",25,C["mute"])
    s.text(140,930,"前",25,C["mute"])
    legend=[("1  P1前面枠","2  G2ガード 3厚","3  3.4C + PCキャリア"),
            ("4  支持板A 8厚","5  A歯車14個","6  B歯車14個"),
            ("7  支持板B 8厚","8  共通軸・継手・モーター","9  P4背板 + 背面電装")]
    table(s,80,965,[495,495,540],legend,39,18)
    s.finish()


def axis_assembly(c):
    s=Sheet(c,"A01","軸ユニットの組立","先にA/B支持板へブッシュを入れ、単軸を組む / 共通軸は支持板2枚の位置を合わせてから通す")
    def strip(y,parts):
        x=110
        for i,(name,sub,col,w) in enumerate(parts):
            s.rect(x,y,w,92,col,C["ink"],1)
            s.text(x+w/2,y+130,name,18,anchor="middle")
            s.text(x+w/2,y+160,sub,16,C["mute"],anchor="middle")
            if i<len(parts)-1:s.arrow(x+w+8,y+45,x+w+45,y+45,C["mute"],1.2)
            x+=w+58
    s.number(90,245,1);s.text(130,253,"A単軸: 前→後 / 同じ構成を13組",25,bold=True)
    strip(300,[("カラー","KSC0605",C["grey"],150),("POM W","1mm",C["gold"],80),
               ("支持板A","ブッシュ込8mm",C["pale"],190),("POM W","1mm",C["gold"],80),
               ("歯車ボス","前側8mm",C["gold"],160),("歯面A","後側6mm",C["gold"],145)])
    s.number(90,535,2);s.text(130,543,"B単軸: 前→後 / Aと歯車の向きが反対 / 13組",25,bold=True)
    strip(590,[("歯面B","前側6mm",C["brown"],145),("歯車ボス","後側8mm",C["brown"],160),
               ("POM W","1mm",C["gold"],80),("支持板B","ブッシュ込8mm",C["pale"],190),
               ("POM W","1mm",C["gold"],80),("カラー","KSC0605",C["grey"],150)])
    s.box(75,855,740,205,"3  A00 / B00共通軸",[
        "6 × 65軸に歯車2個、ギア側POM W2枚を入れる。カラーなし。",
        "A00とB00の穴を同軸に保ち、両板のブッシュへ通す。",
        "継手の6mm側へ7mm入れ、軸方向位置をD05へ合わせる。"])
    s.box(850,855,755,205,"組付け後の手回し",[
        "歯車・カラーを樹脂板へ押し付けず、擦れない状態に調整。",
        "付属M4 × 4止めねじを使い、歯車と軸へ合いマークを付ける。",
        "両列を手回しし、滑り・噛み込み・板割れの有無を確認。"])
    s.finish()


def case_assembly(c):
    s=Sheet(c,"A02","表示器とケースの組立順","支持板252 × 187は内寸開口246 × 181より大きい / 箱を閉じる前に支持板を溝へ入れる")
    s.number(85,240,4);s.text(128,248,"表示器を支持板Aへ固定",25,bold=True)
    s.box(75,285,670,245,"基板→キャリア→支持板",[
        "M4 × 8と2mm絶縁スペーサ各4で表示基板を4本腕へ取り付ける。",
        "M3 × 25、7mm支持スペーサ、座金・ナットでA板の4点へ。",
        "USB・microSDを操作できる方向に置き、ケーブルを仮に通す。",
        "前面ガードを重ねる前にねじ底付き・表示面の座りを確認。"])
    # Top-looking assembly sketch: wall open on the right, two slot-held boards.
    x,y=880,300
    s.rect(x,y,480,250,None,C["wood"],7)
    s.rect(x+500,y,35,250,"#e7d5c3",C["wood"],2)
    s.arrow(x+480,y+120,x+410,y+120,C["brown"],3)
    for dx,label in [(115,"A"),(285,"B")]:
        s.rect(x+dx,y-20,18,290,C["pale"],C["teal"],2)
        s.text(x+dx+9,y+310,label,23,C["teal"],bold=True,anchor="middle")
    s.text(x+230,y-40,"ケース壁を開いた状態で板を挿入",20,anchor="middle")
    s.text(x+300,y+355,"模式図: 分解方向・板厚は説明用",16,C["mute"],anchor="middle")
    s.number(85,635,5);s.text(128,643,"溝へ入れてケース壁を閉じる",25,bold=True)
    s.box(75,680,725,205,"支持板の保持",[
        "A溝 z=28.5…37.5 / B溝 z=69.5…78.5、幅9 × 深さ4。",
        "板端の捕捉は各辺3mm。PETシム0.25/0.5mmでガタを調整。",
        "板を入れてからP2/P3を接合。接合方法は工房見積で決める。"])
    s.number(890,635,6);s.text(933,643,"モーター・前後カバーを合わせる",25,bold=True)
    s.box(880,680,725,205,"取付面と開閉",[
        "共通軸とモーター軸を継手で接続し、取付面z=108へ合わせる。",
        "固定金具形状・締結詳細は現行ソースに未定義。別途具体化する。",
        "P1/G2とP4は最後に固定し、保守時に取り外せるようにする。"],C["brown"])
    s.text(80,957,"P4のケース留め8本は3.1 × 25木ねじを見積に含める。P1/側板接合とガード保持は見積回答で決定。",19)
    s.text(80,1005,"支持板を交換する場合はケース壁の接合を開く。背板だけを外して支持板を引き抜く構造にはしない。",19)
    s.finish()


def rear_assembly(c):
    s=Sheet(c,"A03","背面電装とハーネスの組立","P4を内側へ向けて作業 / D07の基準座標へ仮置き / 小物の穴とねじ長さは実スタックで選ぶ")
    s.number(85,235,7);s.text(130,243,"PCサービス板と小型絶縁パッドを準備",25,bold=True)
    s.box(75,280,730,250,"P4へ取り付ける",[
        "230 × 120 × 3サービス板: Ø3.5を4穴。板内中心X=±105,Y=±50。",
        "HUSB238 / #2851 / RTC / TMC用パッド4枚は、実基板から穴を写す。",
        "パッドとサービス板を置いてP4へ転記。木部下穴は材・ねじに合わせる。",
        "3.1 × 12木ねじはサービス板4本 + パッド各2本、計12本。"])
    # A cross-section intentionally has no unsupported board-hole coordinates.
    s.text(1000,240,"小型基板の固定断面（模式）",23,bold=True)
    s.rect(1040,300,415,60,"#dfcbb7",C["wood"],1.5);s.text(1248,339,"P4 木板 12",20,anchor="middle")
    s.rect(1040,365,415,22,C["pale"],C["teal"],1.2);s.text(1248,420,"PC絶縁パッド 3",20,anchor="middle")
    s.rect(1080,465,335,22,C["teal"],C["ink"],1)
    s.line(1110,440,1110,515,C["ink"],5);s.line(1385,440,1385,515,C["ink"],5)
    s.text(1248,550,"PCB: M2.5 / #2851のみM2",20,anchor="middle")
    s.number(85,620,8);s.text(130,628,"部品・端子・ヒューズを固定して配線",25,bold=True)
    s.box(75,670,730,280,"サービス板上",[
        "221-505各2点をM3ねじ・座金・ナットで固定。穴は取付台から写す。",
        "DFR0758 / DFR1015は結束バンド各2本で保持。",
        "HUSB238は15V/2A、DFR1015は9Vに設定して表示を確認。",
        "3本のヒューズリードを板へ結束し、端子と継ぎ目へ荷重を掛けない。",
        "極性ラベルを付け、接続はD08/D09へ合わせる。"])
    s.box(870,670,735,280,"モーター4芯と開閉余長",[
        "無通電で巻線2組を識別。A1/A2/B1/B2を両端表示する。",
        "AWG22へ1本ずつはんだ継ぎ、接着剤付き熱収縮を個別に掛ける。",
        "信号線とモーター相線は別経路にまとめる。",
        "本体側とカバー側で別々に固定し、カバーを開けられる余長を残す。",
        "線長・曲げ・固定点は完成品の実ルートへ合わせる。"])
    s.text(80,1030,"ネジ径を選定済みでも、M2.5/取付台M3の長さやPCB穴座標はカタログ値として決め打ちしない。",19)
    s.finish()


def checks(c):
    s=Sheet(c,"A04","完成品の確認・閉じ方","完成機そのものを確認する / 先行試験片・専用治具は購入や組立の必須条件にしない")
    steps=[("9-1 無通電の確認",["+15V / 9V / 5V / GNDの極性と短絡を確認。ヒューズとSPSTの直列経路を照合。",
                             "モーター巻線2組、個別絶縁、端子保持を確認。歯車は手回しして接触・引っ掛かりを見る。"]),
           ("9-2 表示・RTC・操作",["内部A-C給電線で表示器を起動し、microSD、エンコーダー、RTC保持を確認。",
                             "CR1220はDS3231のホルダーへ。3.4CのRTC端子へ一次電池を接続しない。"]),
           ("9-3 低速の歯車駆動",["初期0.30A RMS/相から低速正逆・停止を確認。歯車と軸の合いマークを見る。",
                             "滑り、噛み込み、異音、線への接触があれば、その箇所を調整する。"]),
           ("9-4 全負荷とカバー開閉",["表示・無線・SD・LED・モーターの同時動作で電圧降下と閉箱温度を記録。",
                             "P4を開閉し、線の挟み込み・張力・可動部接触がないことを確認して閉じる。"])]
    y=230
    for title,lines in steps:
        s.box(75,y,1530,156,title,lines)
        y+=190
    s.text(80,1040,"残る机上詳細: モーター支持金具の形状・固定穴・締結。工房回答事項: ケース材/接合/ガード保持。",19,C["brown"])
    s.text(80,1076,"実機受入は表示コネクター経路、配線開閉、電源全負荷/温度/保護、歯車の噛み合い/滑り/音。",18)
    s.finish()


def register_fonts(path):
    """ReportLab embeds subset TrueType fonts; pin a variable font before use."""
    temp=Path(tempfile.gettempdir())/"fg-font-cache"/hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    temp.mkdir(parents=True,exist_ok=True)
    for name,weight in [("FG",400),("FG-Bold",600)]:
        dest=temp/f"{name}.ttf"
        if not dest.exists():
            font=FontToolsFont(path)
            if "fvar" in font:font=instantiateVariableFont(font,{"wght":weight},inplace=True)
            font.save(dest);font.close()
        pdfmetrics.registerFont(TTFont(name,str(dest)))


def validate_rows(rows):
    if len(rows)!=28 or len({r["shaft_group"] for r in rows})!=27:
        raise ValueError("Current one-unit schedule must have 28 gears on 27 shafts")
    for layer in ("A","B"):
        seq=[r for r in rows if r["layer"]==layer]
        if len(seq)!=14:raise ValueError("Expected fourteen positions per layer")
        for r in seq:
            if r["KHK_part"]!="BSS1-20C":raise ValueError("Unexpected gear model")
            if abs(float(r["case_x_mm"])-float(r["plate_x_mm"])-9)>.001:raise ValueError("X datum mismatch")
            if abs(float(r["case_y_mm"])-float(r["plate_y_mm"])-9)>.001:raise ValueError("Y datum mismatch")
        for a,b in zip(seq,seq[1:]):
            distance=math.hypot(float(a["plate_x_mm"])-float(b["plate_x_mm"]),float(a["plate_y_mm"])-float(b["plate_y_mm"]))
            if abs(distance-20)>.002:raise ValueError("Nominal gear mesh center distance mismatch")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font",type=Path,required=True,help="Noto Sans JP TrueType font (static or variable)")
    args=parser.parse_args()
    register_fonts(args.font)
    OUT.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader((MECH/"gear_axis_schedule_bss20_candidate.csv").open(encoding="utf-8-sig")))
    validate_rows(rows)
    tmp=Path(tempfile.mkdtemp(prefix="fg-drawing-pdf-"))
    raw=tmp/"design.pdf"
    c=canvas.Canvas(str(raw),pagesize=(W*K,H*K),pageCompression=1)
    c.setTitle("Forest Guardian 一台用設計図 v0.1")
    overview(c,rows)
    for layer in ("A","B"):plate(c,rows,layer)
    for fn in (axial,carrier,rear,power,signals):fn(c)
    c.save()
    # Preserve the already-reviewed v0.4 wood shop sheets without rescaling.
    new=PdfReader(str(raw));wood=PdfReader(str(MECH/"walnut_case_quote_drawing_set_v0.4.pdf"))
    writer=PdfWriter();writer.add_page(new.pages[0])
    for page in wood.pages:writer.add_page(page)
    for page in new.pages[1:]:writer.add_page(page)
    writer.add_metadata({"/Title":"Forest Guardian 一台用設計図 v0.1","/Subject":"設計参照・ケース見積 v0.4・実機未受入"})
    with (OUT/"forest_guardian_design_v0.1.pdf").open("wb") as f:writer.write(f)
    c=canvas.Canvas(str(OUT/"forest_guardian_assembly_v0.1.pdf"),pagesize=(W*K,H*K),pageCompression=1)
    c.setTitle("Forest Guardian 分解組立図・組立手順 v0.1")
    exploded(c,rows)
    for fn in (axis_assembly,case_assembly,rear_assembly,checks):fn(c)
    c.save()
    inputs=[MECH/"gear_axis_schedule_bss20_candidate.csv",MECH/"walnut_case_quote_parts_v0.4.csv",
            MECH/"walnut_case_quote_drawing_set_v0.4.pdf",MECH/"display-board-interface.md",
            ELEC/"rear-harness-and-mount-candidate-v0.1.md",ELEC/"motor-harness-interface.md"]
    manifest={"date":DATE,"version":"v0.1","geometry_baseline_commit":BASE,
              "status":"DESIGN_REFERENCE_NOT_PHYSICALLY_ACCEPTED","design_pdf_pages":len(writer.pages),
              "assembly_pdf_pages":5,"input_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              "open_detail":"Motor support bracket geometry, mounting holes and fasteners are not defined in the baseline.",
              "fit_on_arrival":["small PCB hole positions / M2.5 screw lengths","WAGO carrier hole positions / M3 lengths","P4 wood pilot holes","display connector route","harness and cover opening"],
              "files":[p.name for p in sorted(OUT.glob("*.svg"))]}
    (OUT/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Design: {len(writer.pages)} pages; Assembly: 5 pages; SVG: {len(list(OUT.glob('*.svg')))} sheets")


if __name__=="__main__":main()
