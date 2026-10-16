#!/usr/bin/env python3
"""Meaningful acceptance boundaries only: real network event logic, secret gating,
single control writer, no destructive configuration, and zero fake DONE scope."""
from pathlib import Path
import json,csv
root=Path(__file__).resolve().parent
wifi=(root/"fg_hosted_wifi.c").read_text()
secret=(root/"fg_net_service.c").read_text()
patch=(root/"apply_network_product.py").read_text()
assert 'WIFI_EVENT_STA_DISCONNECTED' in wifi and 'IP_EVENT_STA_GOT_IP' in wifi
assert 'IP_EVENT_STA_LOST_IP' in wifi and 'atomic_store(&s->ip_ready,false)' in wifi
assert 'esp_wifi_set_storage(WIFI_STORAGE_RAM)' in wifi
assert 'WIFI_AUTH_WPA2_PSK' in wifi
assert 'unsigned n=atomic_fetch_add(&s->disconnect_count,1u)+1u;' in wifi
assert '#if !defined(CONFIG_NVS_ENCRYPTION) || !CONFIG_NVS_ENCRYPTION' in secret
assert 'nvs_open("fg_secure_web",NVS_READONLY,&h)' in secret
assert 'nvs_get_blob(h,"tls_key"' in secret
assert 'fg_https_stop(api)' in secret
assert 'fg_https_start_if_ready(api,true,s->cert,s->cert_len' in secret
assert 'vTaskDelete(NULL);return;' in secret
assert 'espressif/esp_hosted: "1.4.*"' in patch
assert 'espressif/esp_wifi_remote: "0.14.*"' in patch
assert 'fg_intent_apply(&ctl,&intent,ctx)' in patch
assert 'xTaskCreate(network_task' in patch
assert not any(x in wifi+secret+patch for x in ('esp_efuse_write','esp_efuse_burn','esp_flash_erase','nvs_set_blob('))
with (root.parent/"tasks.csv").open(encoding="utf-8-sig",newline="") as f:t=list(csv.DictReader(f))
pr=json.loads((root.parent/"progress.json").read_text())
assert next(x["Status"] for x in t if x["ID"]=="G5-05")=="WORKING"
assert (pr["scoped_evidence_done"],pr["working"],pr["open"],pr["hardware_wait"])==(20,7,17,4)
assert pr["manufacturer_release_closed"]==0
print("PASS G5-05 real-network source fail-closed: encrypted NVS+IP+TLS prerequisites, offline on loss")
print("HOLD actual P4/C6 firmware interoperability, key provisioning, real TLS handshake & E2E")
