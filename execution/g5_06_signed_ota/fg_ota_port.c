#include "fg_ota_port.h"
#include "sdkconfig.h"
#include <string.h>
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_partition.h"
#define FG_APP_A_ADDR 0x10000u
#define FG_APP_B_ADDR 0x390000u
static const char *TAG="fg_signed_ota";
typedef struct {
 esp_ota_handle_t handle;
 const esp_partition_t *target;
 bool handle_open;
} fg_esp_ota;

static bool configured(void *context){
 (void)context;
 /* No assurance from a home-made SHA or HTTP alone. The IDF must be configured
  * to authenticate signed app images ON UPDATE and roll back failed first boot.
  * Hardware secure boot is not silently enabled. */
#if defined(CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT) && CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT && \
    defined(CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT) && CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT && \
    defined(CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE) && CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE
 return esp_ota_get_app_partition_count()==2;
#else
 return false;
#endif
}
static bool exact_inactive_slot(void *context,size_t bytes){
 fg_esp_ota *s=context;
 if(!s||bytes<FG_OTA_MIN_IMAGE_BYTES||bytes>FG_OTA_SLOT_CAPACITY)return false;
 const esp_partition_t *running=esp_ota_get_running_partition();
 const esp_partition_t *target=esp_ota_get_next_update_partition(NULL);
 if(!running||!target||running==target)return false;
 if(running->type!=ESP_PARTITION_TYPE_APP||target->type!=ESP_PARTITION_TYPE_APP)return false;
 if(running->size!=FG_OTA_SLOT_CAPACITY||target->size!=FG_OTA_SLOT_CAPACITY)return false;
 const bool pair=
  (running->address==FG_APP_A_ADDR&&target->address==FG_APP_B_ADDR&&
    running->subtype==ESP_PARTITION_SUBTYPE_APP_OTA_0&&
    target->subtype==ESP_PARTITION_SUBTYPE_APP_OTA_1)||
  (running->address==FG_APP_B_ADDR&&target->address==FG_APP_A_ADDR&&
    running->subtype==ESP_PARTITION_SUBTYPE_APP_OTA_1&&
    target->subtype==ESP_PARTITION_SUBTYPE_APP_OTA_0);
 if(!pair)return false;
 esp_ota_img_states_t state=ESP_OTA_IMG_UNDEFINED;
 if(esp_ota_get_state_partition(running,&state)==ESP_OK&&
    (state==ESP_OTA_IMG_PENDING_VERIFY||state==ESP_OTA_IMG_INVALID||
     state==ESP_OTA_IMG_ABORTED))return false;
 s->target=target;
 return esp_ota_begin(target,bytes,&s->handle)==ESP_OK?(s->handle_open=true):false;
}
static bool stage_write(void *context,const uint8_t *data,size_t bytes){
 fg_esp_ota *s=context;
 return s&&s->handle_open&&data&&bytes&&esp_ota_write(s->handle,data,bytes)==ESP_OK;
}
static bool stage_close_verified(void *context){
 fg_esp_ota *s=context;
 if(!s||!s->handle_open)return false;
 s->handle_open=false;
 /* IDF checks the signed image cryptographically at esp_ota_end only in
  * CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT builds. */
 return esp_ota_end(s->handle)==ESP_OK;
}
static bool set_boot(void *context){
 fg_esp_ota *s=context;
 if(!s||s->handle_open||!s->target)return false;
 return esp_ota_set_boot_partition(s->target)==ESP_OK;
}
static void stage_abort(void *context){
 fg_esp_ota *s=context;
 if(s&&s->handle_open){(void)esp_ota_abort(s->handle);s->handle_open=false;}
}
fg_ota_result fg_ota_native_stage_for_review(const fg_ota_source *source,size_t bytes){
 fg_esp_ota s={0};
 fg_ota_ops ops={
  .context=&s,.ready=configured,.begin_inactive=exact_inactive_slot,
  .write=stage_write,.finish_verified=stage_close_verified,
  .select_next_boot=set_boot,.abort=stage_abort
 };
 /* Neither the G1 independent stop circuit nor the 7-axis HIL is certified.
  * BOTH values MUST remain false until physical acceptance. This causes
  * fg_ota_stage to return before esp_ota_begin/erase/write. */
 return fg_ota_stage(source,&ops,bytes,false,false);
}
void fg_ota_boot_guard_unqualified(void){
#if defined(CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE) && CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE
 const esp_partition_t *running=esp_ota_get_running_partition();
 if(!running)return;
 esp_ota_img_states_t state=ESP_OTA_IMG_UNDEFINED;
 if(esp_ota_get_state_partition(running,&state)!=ESP_OK)return;
 if(state==ESP_OTA_IMG_PENDING_VERIFY){
  /* Motor safety HIL is NOT qualified. New app may never mark itself VALID.
   * Attempt return to prior confirmed application now; if unavailable remain
   * in safe/locked state, never fabricate a successful self-test. */
  ESP_LOGE(TAG,"New OTA image is not physically qualified: request rollback");
  esp_err_t e=esp_ota_mark_app_invalid_rollback_and_reboot();
  if(e!=ESP_OK)ESP_LOGE(TAG,"Rollback impossible (%d); remain review locked",(int)e);
 }
#else
 ESP_LOGI(TAG,"OTA rollback not enabled; OTA operations remain disabled");
#endif
}
