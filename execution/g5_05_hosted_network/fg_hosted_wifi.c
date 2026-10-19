#include "fg_hosted_wifi.h"
#include <string.h>
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_log.h"
static const char *TAG="fg_wifi";
static void event(void *ctx,esp_event_base_t base,int32_t id,void *data){
 (void)data;
 fg_hosted_wifi *s=ctx;
 if(base==WIFI_EVENT&&id==WIFI_EVENT_STA_START){
  if(esp_wifi_connect()!=ESP_OK)ESP_LOGE(TAG,"hosted initial connect request failed");
 }else if(base==WIFI_EVENT&&id==WIFI_EVENT_STA_DISCONNECTED){
  atomic_store(&s->ip_ready,false);
  unsigned n=atomic_fetch_add(&s->disconnect_count,1u)+1u;
  /* Fixed retry budget. Never block the control task or automatically arm motors. */
  if(n<=5u){
   if(esp_wifi_connect()!=ESP_OK)ESP_LOGW(TAG,"hosted reconnect request refused");
  }else ESP_LOGE(TAG,"hosted station failed five retries, HTTPS stays offline");
 }else if(base==IP_EVENT&&id==IP_EVENT_STA_GOT_IP){
  atomic_store(&s->ip_ready,true);
  atomic_store(&s->disconnect_count,0u);
 }else if(base==IP_EVENT&&id==IP_EVENT_STA_LOST_IP){
  atomic_store(&s->ip_ready,false);
 }
}
bool fg_hosted_wifi_ip_ready(const fg_hosted_wifi *s){
 return s&&s->started&&atomic_load(&s->ip_ready);
}
bool fg_hosted_wifi_start(fg_hosted_wifi *s,const char *ssid,const char *pass){
 if(!s||!ssid||!pass||s->started)return false;
 size_t sn=strnlen(ssid,33),pn=strnlen(pass,65);
 /* Credentials must be externally provisioned, never compiled in.
  * No open networks / weak passphrases are accepted in this product path. */
 if(sn<1||sn>32||pn<8||pn>63)return false;
 if(esp_netif_init()!=ESP_OK)return false;
 esp_err_t loop=esp_event_loop_create_default();
 if(loop!=ESP_OK&&loop!=ESP_ERR_INVALID_STATE)return false;
 if(!esp_netif_create_default_wifi_sta())return false;
 wifi_init_config_t conf=WIFI_INIT_CONFIG_DEFAULT();
 if(esp_wifi_init(&conf)!=ESP_OK)return false;
 if(esp_wifi_set_storage(WIFI_STORAGE_RAM)!=ESP_OK)return false;
 if(esp_event_handler_register(WIFI_EVENT,ESP_EVENT_ANY_ID,event,s)!=ESP_OK)return false;
 if(esp_event_handler_register(IP_EVENT,IP_EVENT_STA_GOT_IP,event,s)!=ESP_OK)return false;
 if(esp_event_handler_register(IP_EVENT,IP_EVENT_STA_LOST_IP,event,s)!=ESP_OK)return false;
 wifi_config_t wifi={0};
 memcpy(wifi.sta.ssid,ssid,sn);
 memcpy(wifi.sta.password,pass,pn);
 wifi.sta.threshold.authmode=WIFI_AUTH_WPA2_PSK;
 if(esp_wifi_set_mode(WIFI_MODE_STA)!=ESP_OK||
    esp_wifi_set_config(WIFI_IF_STA,&wifi)!=ESP_OK){
  memset(&wifi,0,sizeof(wifi));return false;
 }
 memset(&wifi,0,sizeof(wifi));
 s->started=true;
 atomic_store(&s->ip_ready,false);
 if(esp_wifi_start()!=ESP_OK){s->started=false;return false;}
 return true;
}
