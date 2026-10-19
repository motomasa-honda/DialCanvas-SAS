#!/usr/bin/env python3
"""Patch exactly vetted product archive source; fail if anchors drift. No network producer yet."""
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument("firmware");args=parser.parse_args()
here=Path(__file__).resolve().parent
main=Path(args.firmware)/"main";app=main/"app_main.c";cm=main/"CMakeLists.txt"
a=app.read_text();old_cmake=cm.read_text()
def once(before,after):
 global a
 assert a.count(before)==1,("unexpected product-source anchor",before)
 a=a.replace(before,after)
once('#include "fg_intent.h"','#include "fg_intent.h"\n#include "fg_web_access.h"\n#include "esp_random.h"')
once('static atomic_bool status_page,pairing_requested;','static atomic_bool status_page,pairing_requested;\nstatic atomic_uint pairing_code_local;\nstatic fg_web_access web_access;')
marker='static const fg_journal_io journal_io={.context=NULL,.read=journal_read,.write=journal_write};'
integration=r"""
/* Only SHA256 credential digests, never bearer secrets or pairing codes, go to NVS.
 * Storage failure refuses pairing. The web endpoint is NOT registered in G5-05/part-1.
 */
static bool web_auth_save(void *ctx,const fg_web_credentials *slots){
 (void)ctx;nvs_handle_t n;
 if(nvs_open("fg_web",NVS_READWRITE,&n)!=ESP_OK)return false;
 esp_err_t err=nvs_set_blob(n,"roles",slots,sizeof(*slots));
 if(err==ESP_OK)err=nvs_commit(n);
 nvs_close(n);return err==ESP_OK;
}
static bool web_auth_random(void *ctx,uint8_t *dst,size_t n){
 (void)ctx;if(!dst||!n)return false;
 esp_fill_random(dst,n);return true;
}
static void web_auth_init(void){
 fg_web_credentials saved={0};nvs_handle_t n;
 if(nvs_open("fg_web",NVS_READONLY,&n)==ESP_OK){
  size_t len=sizeof(saved);
  if(nvs_get_blob(n,"roles",&saved,&len)!=ESP_OK||len!=sizeof(saved))memset(&saved,0,sizeof(saved));
  nvs_close(n);
 }
 fg_web_access_init(&web_access,saved,web_auth_save,web_auth_random,NULL);
}
"""
once(marker,marker+"\n"+integration)
before='atomic_store(&pairing_requested,ctl.state==FG_OFF&&!ctl.arm);\n   /* The safe physical request is implemented; AP/TLS provisioning remains open. */'
after='atomic_store(&pairing_requested,ctl.state==FG_OFF&&!ctl.arm);\n   if(ctl.state==FG_OFF&&!ctl.arm){\n    uint32_t local_code=0;\n    if(fg_web_open_local_pairing(&web_access,now/1000U,&local_code))atomic_store(&pairing_code_local,local_code);\n   }\n   /* Pair code is local-only; TLS transport is NOT active. Do not send motor intents from HTTP. */'
once(before,after)
once('ESP_ERROR_CHECK(nvs_flash_init());','ESP_ERROR_CHECK(nvs_flash_init());\n web_auth_init();')
assert old_cmake.count('"fg_intent.c"')==1
cm.write_text(old_cmake.replace('"fg_intent.c"','"fg_intent.c" "fg_web_access.c"'))
app.write_text(a)
for fname in ("fg_web_access.c","fg_web_access.h"):
 dst=main/fname
 assert not dst.exists()
 dst.write_text((here/fname).read_text())
assert 'fg_web_open_local_pairing(&web_access,now/1000U' in a
assert a.count('xQueueReceive(intent_queue,&intent,0)')==1
assert 'httpd_start' not in a and 'httpd_ssl_start' not in a
print("PASS product source physical pairing uses GPIO chord and NVS digest state only; no unauthenticated HTTP producer")
