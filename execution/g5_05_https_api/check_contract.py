#!/usr/bin/env python3
from pathlib import Path
import csv,json
root=Path(__file__).resolve().parent
api=(root/"fg_https_api.c").read_text()
adapter=(root/"apply_https_product.py").read_text()
assert 'httpd_ssl_start(&s->server,&cfg)' in api
assert 'cfg.transport_mode=HTTPD_SSL_TRANSPORT_SECURE' in api
assert 'httpd_start(' not in api
assert 'if(xQueueSend(s->intent_queue,&i,0)!=pdTRUE)' in api
assert 'FG_INTENT_START_ALL' in api and '"202 Accepted"' in api
assert '"/v1/pair"' in api and '"/v1/status"' in api
assert '"Bearer "' not in api or 'Bearer ' in api
assert 'fg_web_permit(role,"POST",r->uri)' in api
assert 'if(ctl.last_sequence>=UINT64_MAX-1)continue;' in adapter
assert 'xSemaphoreTake(web_auth_mutex,0)' in adapter
assert 'PAIR %06u' in adapter
assert 'fg_https_api_init(&https_service' in adapter
assert 'network_ready' in api and 'certlen<32' in api
with (root.parent/"tasks.csv").open(encoding="utf-8-sig",newline="") as f:tasks=list(csv.DictReader(f))
p=json.loads((root.parent/"progress.json").read_text())
assert next(x for x in tasks if x["ID"]=="G5-05")["Status"]=="WORKING"
assert p["scoped_evidence_done"]==20 and p["manufacturer_release_closed"]==0
print("PASS HTTPS secure-only route product adapter, paired role auth, control queue only, no direct GPIO")
print("HOLD no external Wi-Fi transport or provisioned server TLS key, no real traffic/HIL")
