#include "fg_net_service.h"
#include <string.h>
#include "nvs.h"
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
#if !defined(CONFIG_NVS_ENCRYPTION) || !CONFIG_NVS_ENCRYPTION
 ESP_LOGW(TAG,"encrypted NVS not configured; no WiFi, no TLS, no plaintext fallback");
 return false;
#else
 memset(s->ssid,0,sizeof(s->ssid));
 memset(s->password,0,sizeof(s->password));
 s->cert_len=s->key_len=0;
 nvs_handle_t h;
 if(nvs_open("fg_secure_web",NVS_READONLY,&h)!=ESP_OK)return false;
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
