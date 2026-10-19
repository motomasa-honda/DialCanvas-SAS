#!/usr/bin/env python3
"""After G5-05 access + HTTPS patch, wire real ESP32-P4/C6 Hosted Wi-Fi service.
Loading is disabled unless CONFIG_NVS_ENCRYPTION. NO settings, flash, eFuse writes,
credentials or TLS private keys embedded in committed source.
"""
from pathlib import Path
import sys
assert len(sys.argv)==2
here=Path(__file__).resolve().parent
main=Path(sys.argv[1])/"main"
src=main/"app_main.c";manifest=main/"idf_component.yml";cm=main/"CMakeLists.txt"
a=src.read_text();dep=manifest.read_text();b=cm.read_text()
def replace_one(old,new):
 global a
 assert a.count(old)==1,("missing expected product anchor",old)
 a=a.replace(old,new)
replace_one('#include "fg_https_api.h"','#include "fg_https_api.h"\n#include "fg_net_service.h"')
replace_one("static fg_https_api https_service;",
"""static fg_https_api https_service;
static fg_net_credentials network_credentials;
/* Network task never touches motor ARM, GPIO, MCP or phase state. */
static void network_task(void *arg){
 (void)arg;
 fg_net_service_loop(&network_credentials,&https_service);
}""")
# Initiate only after screen+UI exists, so the physical pair PIN remains visible locally.
replace_one(' lv_timer_create(draw_clock,33,0);atomic_store(&display_ready,true);bsp_display_unlock();',
""" lv_timer_create(draw_clock,33,0);atomic_store(&display_ready,true);bsp_display_unlock();
 /* May start ONLY with encrypted NVS provisioned Wi-Fi + PEM cert/private key.
  * On default builds this task exits without touching Wi-Fi or making a listener.
  */
 if(xTaskCreate(network_task,"fg_wifi_https",8192,NULL,3,NULL)!=pdPASS)
  ESP_LOGE(TAG,"Network task not created; HTTPS remains off");""")
assert 'waveshare/esp32_p4_wifi6_touch_lcd_xc:' in dep
assert "espressif/esp_hosted:" not in dep
dep+='  espressif/esp_hosted: "1.4.*"\n  espressif/esp_wifi_remote: "0.14.*"\n'
assert 'REQUIRES esp_https_server' in b
b=b.replace('"fg_https_api.c"','"fg_https_api.c" "fg_hosted_wifi.c" "fg_net_service.c"')
b=b.replace("REQUIRES esp_https_server","REQUIRES esp_wifi esp_event esp_netif esp_https_server")
for fname in ("fg_hosted_wifi.c","fg_hosted_wifi.h","fg_net_service.c","fg_net_service.h"):
 target=main/fname
 assert not target.exists(),fname
 target.write_text((here/fname).read_text())
src.write_text(a);manifest.write_text(dep);cm.write_text(b)
assert a.count('fg_net_service_loop(&network_credentials,&https_service)')==1
assert a.count('fg_intent_apply(&ctl,&intent,ctx)')==1
assert 'esp_wifi_connect(' not in a and 'httpd_start(' not in a
print("PASS actual BSP product: C6 hosted Wi-Fi source, IP up/down -> HTTPS gate, encrypted NVS only")
print("HOLD default release build has no provisioned secrets; no hardware IP/TLS/E2E has happened")
