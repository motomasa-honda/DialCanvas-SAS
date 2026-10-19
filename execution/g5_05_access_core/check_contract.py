#!/usr/bin/env python3
from pathlib import Path
import json,csv
root=Path(__file__).resolve().parent
header=(root/"fg_web_access.h").read_text()
code=(root/"fg_web_access.c").read_text()
script=(root/"apply_product.py").read_text()
assert all(z in header for z in ("FG_WEB_PAIR_WINDOW_MS 60000u","FG_WEB_PAIR_MAX_TRIES 5u","FG_WEB_TOKEN_BYTES 32u"))
assert all(z in code for z in ("fg_web_authenticate","fg_web_permit","FG_WEB_ADMIN","constant_equal","FG_WEB_PERSIST_FAILED"))
assert all(z in script for z in ("fg_web_open_local_pairing","fg_web_access_init","fg_web_access.c","ESP_ERROR_CHECK(nvs_flash_init())"))
tasks=list(csv.DictReader((root.parent/"tasks.csv").open(encoding="utf-8-sig",newline="")))
p=json.loads((root.parent/"progress.json").read_text())
assert next(x for x in tasks if x["ID"]=="G5-05")["Status"]=="WORKING"
assert next(x for x in tasks if x["ID"]=="G5-06")["Status"]=="WORKING"
from collections import Counter
counts=Counter(x["Status"] for x in tasks)
assert (p["scoped_evidence_done"],p["working"],p["open"],p["hardware_wait"])==(
 counts["DONE_SCOPE"],counts["WORKING"],counts["OPEN"],counts["HARDWARE_WAIT"])
assert p["scoped_evidence_done"]>=20 and p["manufacturer_release_closed"]==0
assert p["manufacturer_release_closed"]==0
print("PASS G5-05 role core scoped WORKING; no fake HTTPS completed claim or motor hardware validation")
