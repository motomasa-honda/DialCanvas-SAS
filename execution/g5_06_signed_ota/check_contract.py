#!/usr/bin/env python3
"""G5-06 only real acceptance constraints; review stage NOT marked DONE."""
import csv,json
from collections import Counter
from pathlib import Path
p=Path(__file__).resolve().parent
core=(p/"fg_ota_gate.c").read_text()
port=(p/"fg_ota_port.c").read_text()
patch=(p/"apply_product.py").read_text()
assert 'if(!motors_off_proven||!independent_hil_approved||!io->ready' in core
assert core.index("io->finish_verified") < core.index("io->select_next_boot")
assert 'io->abort(io->context)' in core
assert 'FG_OTA_SLOT_CAPACITY' in core
assert 'trailing=source->read(source->context,buf,1)' in core
assert 'if(trailing!=0)' in core and 'io->abort(io->context)' in core
assert 'true transport EOF' in (p/"fg_ota_gate.h").read_text()
assert 'esp_ota_get_next_update_partition(NULL)' in port
assert 'esp_ota_get_running_partition()' in port
assert 'esp_ota_get_state_partition(running,&state)' in port
assert 'esp_ota_begin(target,bytes,&s->handle)' in port
assert 'esp_ota_end(s->handle)' in port
assert 'esp_ota_set_boot_partition(s->target)' in port
assert 'esp_ota_mark_app_invalid_rollback_and_reboot()' in port
assert 'bool fg_ota_boot_guard_unqualified(void)' in port
assert 'if(status!=ESP_OK)' in port and 'return false;' in port
assert 'if(state!=ESP_OTA_IMG_VALID&&state!=ESP_OTA_IMG_UNDEFINED)' in port
assert 'Rollback did not reboot' in port
assert 'if(!fg_ota_boot_guard_unqualified()){gpio_set_level(ARM,0);return;}' in patch
assert 'esp_ota_mark_app_valid_cancel_rollback' not in port
assert 'CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT' in port
assert 'CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE' in port
assert 'fg_ota_stage(source,&ops,bytes,false,false)' in port
assert '"fg_ota_port.c"' in patch and 'REQUIRES app_update' in patch
with (p.parent/"tasks.csv").open(encoding="utf-8-sig",newline="") as f:tasks=list(csv.DictReader(f))
state=next(x["Status"] for x in tasks if x["ID"]=="G5-06")
assert state=="WORKING"
progress=json.loads((p.parent/"progress.json").read_text())
counts=Counter(task["Status"] for task in tasks)
assert len(tasks)==progress["task_total"]==48
assert progress["scoped_evidence_done"]==counts["DONE_SCOPE"]
assert progress["working"]==counts["WORKING"]
assert progress["open"]==counts["OPEN"]
assert progress["hardware_wait"]==counts["HARDWARE_WAIT"]
assert progress["manufacturer_release_closed"]==0
print("PASS G5-06 real IDF OTA port staged: inactive A/B only, IDF signature and rollback mandatory, HIL false")
print("HOLD no network update consumer, production signer, approved HIL, signed bootloader, or power-cycle test")
