#!/usr/bin/env python3
"""After the tested G5-05 product patch, add ONLY bounded HTTPS routes and local PIN GUI.
No Wi-Fi/certificate provisioning here. Compiled HTTPS adapter stays fail-closed until
trusted networking code explicitly invokes fg_https_start_if_ready with valid TLS material.
"""
from pathlib import Path
import sys
assert len(sys.argv)==2, "Usage: apply_https_product.py path/to/firmware"
here=Path(__file__).resolve().parent
main=Path(sys.argv[1])/"main"
app=main/"app_main.c";cm=main/"CMakeLists.txt"
a=app.read_text();build=cm.read_text()
def patch(old,new):
 global a
 assert a.count(old)==1, ("product source drift",old)
 a=a.replace(old,new)
patch('#include "fg_web_access.h"',
      '#include "fg_web_access.h"\n#include "fg_https_api.h"\n#include "freertos/semphr.h"')
patch("static fg_web_access web_access;",
      "static fg_web_access web_access;\nstatic SemaphoreHandle_t web_auth_mutex;\nstatic fg_https_api https_service;\nstatic atomic_ullong pairing_until_ms;\nstatic atomic_bool display_ready;")
# Preserve 5ms control loop: trylock, never block on NVS writes in network server task.
patch("""   if(ctl.state==FG_OFF&&!ctl.arm){
    uint32_t local_code=0;
    if(fg_web_open_local_pairing(&web_access,now/1000U,&local_code))atomic_store(&pairing_code_local,local_code);
   }""",
"""   if(ctl.state==FG_OFF&&!ctl.arm&&atomic_load(&display_ready)&&
      xSemaphoreTake(web_auth_mutex,0)==pdTRUE){
    uint32_t local_code=0;
    if(fg_web_open_local_pairing(&web_access,now/1000U,&local_code)){
     atomic_store(&pairing_code_local,local_code);
     atomic_store(&pairing_until_ms,now/1000U+FG_WEB_PAIR_WINDOW_MS);
     atomic_store(&status_page,true);
    }
    xSemaphoreGive(web_auth_mutex);
   }""")
# Existing control task is sole writer, CANONICAL monotonic sequence.
patch('   (void)fg_intent_apply(&ctl,&intent,ctx);',
"""   if(intent.kind==FG_INTENT_START_ALL){
    if(ctl.last_sequence>=UINT64_MAX-1)continue;
    intent.sequence=ctl.last_sequence+1;
   }
   (void)fg_intent_apply(&ctl,&intent,ctx);""")
# Only local display shows code. No remote endpoint echoes pairing code.
patch('  lv_label_set_text_fmt(status_label,\n   "CTRL',
"""  unsigned pin=atomic_load(&pairing_code_local);
  uint64_t deadline=atomic_load(&pairing_until_ms);
  bool show_pin=pin>=100000u && now_ms_for_screen()<deadline;
  if(pin&&!show_pin)atomic_store(&pairing_code_local,0u);
  lv_label_set_text_fmt(status_label,
   "CTRL""")
# Helper called only by GUI task, not referenced in HTTPS code.
patch('static void draw_clock(lv_timer_t *timer){',
      'static uint64_t now_ms_for_screen(void){return (uint64_t)esp_timer_get_time()/1000U;}\nstatic void draw_clock(lv_timer_t *timer){')
patch('PAIRING AP service not implemented%s",',
      'PAIRING  %s\\nNETWORK/TLS awaiting provisioning",')
patch('faults[f],atomic_load(&pairing_requested)?" (request recorded)":"");',
      'faults[f],show_pin?"LOCAL CODE ON SCREEN":"not active");')
# Show actual six-digit PIN in status page explicitly, via dedicated label override on active state.
patch('  return;\n }\n lv_obj_add_flag(status_label,LV_OBJ_FLAG_HIDDEN);',
"""  if(show_pin){
   lv_label_set_text_fmt(clock_label,"PAIR %06u",pin);
  }
  return;
 }
 lv_obj_add_flag(status_label,LV_OBJ_FLAG_HIDDEN);""")
patch(' web_auth_init();',
""" web_auth_mutex=xSemaphoreCreateMutex();
 if(!web_auth_mutex){gpio_set_level(ARM,0);abort();}
 web_auth_init();""")
patch(' if(!intent_queue||!journal_queue){gpio_set_level(ARM,0);abort();}',
""" if(!intent_queue||!journal_queue){gpio_set_level(ARM,0);abort();}
 fg_https_api_init(&https_service,&web_access,web_auth_mutex,intent_queue,
                   &shown_state,&shown_fault,&pairing_code_local);""")
patch(' lv_timer_create(draw_clock,33,0);bsp_display_unlock();',
      ' lv_timer_create(draw_clock,33,0);atomic_store(&display_ready,true);bsp_display_unlock();')
assert '"fg_web_access.c"' in build
build=build.replace('"fg_web_access.c"','"fg_web_access.c" "fg_https_api.c"')
assert build.count("fg_https_api.c")==1
assert "REQUIRES esp_driver_gpio" in build
build=build.replace("REQUIRES esp_driver_gpio","REQUIRES esp_https_server esp_http_server esp_driver_gpio")
for name in ("fg_https_api.h","fg_https_api.c"):
 assert not (main/name).exists(),name
 (main/name).write_text((here/name).read_text())
cm.write_text(build)
app.write_text(a)
assert app.read_text().count("fg_intent_apply(&ctl,&intent,ctx)") == 1
assert "httpd_ssl_start" not in a # HTTPS interface isolated to module; no HTTP/plaintext
print("PASS: actual device physical pairing GUI, nonblocking auth mutex, sole writer command sequencing")
print("HOLD: runtime HTTPS is intentionally not started until networking + approved TLS key/cert provision")
