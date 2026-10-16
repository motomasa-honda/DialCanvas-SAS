#include "fg_net_service.h"
#include <string.h>
#include "nvs.h"
#include "nvs_flash.h"
#include "esp_partition.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
static const char *TAG="fg_net";
static void wipe(void *v,size_t n){volatile uint8_t *b=v;while(n--)*b++=0;}
static bool has_pem(const uint8_t *data,size_t len,const char *prefix){
 size_t n=strlen(prefix);
 if(len<=n||memcmp(data,prefix,n)!=0)return false;
 return data[len-1]==0 && memchr(data,0,len)==data+len-1;
}
bool fg_net_load_protected_nvs(fg_net_credentials *s){
 if(!s)return false;
 /*
  * Requiring CONFIG_NVS_ENCRYPTION is a compile-time safety gate.
  * Enabling NVS encryption can need flash-encryption/eFuse provisioning:
  * DO NOT enable or flash without independent user manufacturing approval.
  */
#if !defined(CONFIG_NVS_ENCRYPTION) || !CONFIG_NVS_ENCRYPTION || \
    !defined(CONFIG_NVS_SEC_KEY_PROTECT_USING_FLASH_ENC) || \
    !CONFIG_NVS_SEC_KEY_PROTECT_USING_FLASH_ENC
 ESP_LOGW(TAG,"Flash Encryption-protected NVS is not provisioned; WiFi and TLS stay disabled");
 return false;
#else
 /* G5-05: NEVER read TLS private keys or WiFi password from general NVS.
  * Key partition must exist AND have already been provisioned by an approved
  * manufacturing process. Never generate/erase keys from this network task. */
 const esp_partition_t *key_part=esp_partition_find_first(
     ESP_PARTITION_TYPE_DATA,ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,"nvs_keys");
 if(!key_part)return false;
 nvs_sec_cfg_t cfg={0};
 if(nvs_flash_read_security_cfg(key_part,&cfg)!=ESP_OK){
  wipe(&cfg,sizeof(cfg));return false;
 }
 esp_err_t init=nvs_flash_secure_init_partition("fg_cfg",&cfg);
 wipe(&cfg,sizeof(cfg));
 if(init!=ESP_OK){
  ESP_LOGE(TAG,"dedicated secure NVS partition cannot be initialized; offline");
  return false;
 }
 memset(s->ssid,0,sizeof(s->ssid));
 memset(s->password,0,sizeof(s->password));
 s->cert_len=s->key_len=0;
 nvs_handle_t h;
 if(nvs_open_from_partition("fg_cfg","fg_secure_web",NVS_READONLY,&h)!=ESP_OK)return false;
 size_t ssid_len=sizeof(s->ssid),pw_len=sizeof(s->password);
 size_t cert_len=sizeof(s->cert),key_len=sizeof(s->private_key);
 esp_err_t e1=nvs_get_str(h,"sta_ssid",s->ssid,&ssid_len);
 esp_err_t e2=nvs_get_str(h,"sta_pass",s->password,&pw_len);
 esp_err_t e3=nvs_get_blob(h,"tls_cert",s->cert,&cert_len);
 esp_err_t e4=nvs_get_blob(h,"tls_key",s->private_key,&key_len);
 nvs_close(h);
 size_t sn=strnlen(s->ssid,sizeof(s->ssid)),pn=strnlen(s->password,sizeof(s->password));
 bool valid=e1==ESP_OK&&e2==ESP_OK&&e3==ESP_OK&&e4==ESP_OK &&
   ssid_len==sn+1 && sn>=1 && sn<=32 && pw_len==pn+1 && pn>=8 && pn<=63 &&
   cert_len>=64 && cert_len<=sizeof(s->cert) &&
   key_len>=64 && key_len<=sizeof(s->private_key) &&
   has_pem(s->cert,cert_len,"-----BEGIN CERTIFICATE-----") &&
   has_pem(s->private_key,key_len,"-----BEGIN ");
 if(!valid){
  wipe(s->ssid,sizeof(s->ssid));wipe(s->password,sizeof(s->password));
  wipe(s->private_key,sizeof(s->private_key));
  memset(s->cert,0,sizeof(s->cert));s->cert_len=s->key_len=0;
  ESP_LOGE(TAG,"protected provisioning incomplete/invalid; offline");
  return false;
 }
 s->cert_len=cert_len;s->key_len=key_len;
 return true;
#endif
}
void fg_net_service_loop(fg_net_credentials *s,fg_https_api *api){
 if(!s||!api){vTaskDelete(NULL);return;}
 /* On ordinary builds, this returns false before accessing any credentials. */
 if(!fg_net_load_protected_nvs(s)){
  vTaskDelete(NULL);return;
 }
 bool ok=fg_hosted_wifi_start(&s->wifi,s->ssid,s->password);
 wipe(s->ssid,sizeof(s->ssid));
 wipe(s->password,sizeof(s->password));
 if(!ok){
  wipe(s->private_key,sizeof(s->private_key));
  memset(s->cert,0,sizeof(s->cert));vTaskDelete(NULL);return;
 }
 bool online=false;
 for(;;){
  bool ip=fg_hosted_wifi_ip_ready(&s->wifi);
  if(!ip&&online){
   fg_https_stop(api);
   online=false;
   ESP_LOGW(TAG,"IP lost: HTTPS listener stopped");
  }
  if(ip&&!online){
   online=fg_https_start_if_ready(api,true,s->cert,s->cert_len,
                                   s->private_key,s->key_len);
   if(!online)ESP_LOGE(TAG,"HTTPS TLS start rejected; no plaintext fallback");
  }
  vTaskDelay(pdMS_TO_TICKS(250));
 }
}
