#!/usr/bin/env python3
"""Compare exact RAW A/B partition from SHA-frozen original to NO-FLASH nvs_keys candidate."""
import tarfile,hashlib,csv,io,json
from pathlib import Path
d=Path(__file__).resolve().parent; exe=d.parent
original=exe.parent/"phase67-source/firmware.tar.gz"
assert hashlib.sha256(original.read_bytes()).hexdigest()=="a245ac0da5ad690509a651b2872cc9eb163f0718875a8f238527246f5fdccba3"
with tarfile.open(original,"r:gz") as t:
 src=t.extractfile("firmware/partition-review-raw-ab.csv")
 assert src is not None
 raw=src.read().decode()
def parse(data):
 rows={}
 for r in csv.reader(io.StringIO(data)):
  if not r or r[0].startswith("#"):continue
  assert len(r) in (5,6)
  n,ty,sub,off,sz=[s.strip() for s in r[:5]]
  assert n not in rows
  rows[n]=(ty,sub,int(off,0),int(sz,0),r[5].strip() if len(r)==6 else "")
 return rows
prev=parse(raw);now=parse((d/"partition-nvs-encrypted-raw-ab-review.csv").read_text())
assert len(prev)==9 and len(now)==11
assert set(now)==set(prev)|{"nvs_keys","fg_cfg"}
for name in prev:
 if name=="reserved":continue
 assert now[name]==prev[name],("Critical source partition changed",name)
assert now["nvs_keys"]==("data","nvs_keys",0x1E10000,0x1000,"encrypted")
assert now["fg_cfg"]==("data","nvs",0x1E11000,0x8000,"")
assert prev["reserved"]==("data","0x40",0x1E10000,0x1F0000,"")
assert now["reserved"]==("data","0x40",0x1E19000,0x1E7000,"")
items=sorted(now.items(),key=lambda p:p[1][2])
assert items[0][1][2]==0x9000
for (n,a),(m,b) in zip(items,items[1:]):
 assert a[2]%0x1000==a[3]%0x1000==0 and a[2]+a[3]==b[2],(n,m)
assert items[-1][1][2]+items[-1][1][3]==0x2000000
assert now["app_a"][3]==now["app_b"][3]==0x380000
with (exe/"tasks.csv").open(encoding="utf-8-sig",newline="") as f:tasks=list(csv.DictReader(f))
p=json.loads((exe/"progress.json").read_text())
assert next(x for x in tasks if x["ID"]=="G5-05")["Status"]=="WORKING"
assert p["task_total"]==len(tasks)==48
assert p["scoped_evidence_done"]==sum(t["Status"]=="DONE_SCOPE" for t in tasks)
assert p["manufacturer_release_closed"]==0
print("PASS G5-05 exact SHA-frozen RAW A/B source: 8 partitions byte-identical, 4KiB encrypted nvs_keys + independent 32KiB fg_cfg in reserved")
print("PASS contiguous, 4KiB aligned 32MiB partition table; no app reduction, no flash, no efuse")
