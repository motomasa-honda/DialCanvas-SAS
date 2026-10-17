#!/usr/bin/env python3
"""Patch actual G5-05 P4/C6 Hosted+HTTPS product with a fail-closed OTA adapter.
 *No* signed private key, reboot command, update endpoint, flash, or efuse writes.
"""
from pathlib import Path
import sys
assert len(sys.argv)==2,"usage: apply_product.py firmware-path"
d=Path(__file__).resolve().parent
main=Path(sys.argv[1])/"main"
app=main/"app_main.c"; cm=main/"CMakeLists.txt"
text=app.read_text();build=cm.read_text()
def change_once(old,new):
 global text
 assert text.count(old)==1,("firmware source drift",old)
 text=text.replace(old,new)
change_once('#include "fg_net_service.h"',
            '#include "fg_net_service.h"\n#include "fg_ota_port.h"')
# Physical ARM GPIO is already configured and driven LOW earlier in app_main.
change_once('ESP_ERROR_CHECK(nvs_flash_init());',
            'ESP_ERROR_CHECK(nvs_flash_init());\n'
            ' /* Never mark unsigned/unreviewed new app VALID on first boot. */\n'
            ' fg_ota_boot_guard_unqualified();')
assert build.count('"fg_net_service.c"')==1
build=build.replace('"fg_net_service.c"','"fg_net_service.c" "fg_ota_gate.c" "fg_ota_port.c"')
assert "REQUIRES esp_wifi" in build
build=build.replace("REQUIRES esp_wifi","REQUIRES app_update esp_wifi")
for name in ("fg_ota_gate.c","fg_ota_gate.h","fg_ota_port.c","fg_ota_port.h"):
 target=main/name
 assert not target.exists(),name
 target.write_text((d/name).read_text())
app.write_text(text);cm.write_text(build)
assert text.count("fg_ota_boot_guard_unqualified();")==1
assert text.count("fg_intent_apply(&ctl,&intent,ctx)")==1
assert "FG_OTA_ALLOW_UNVERIFIED" not in text
print("PASS G5-06 actual product CMake + boot-first-review guard integrated, physical gate remains false")
print("HOLD not a signed update receiver, no active signing configuration, never flashed")
