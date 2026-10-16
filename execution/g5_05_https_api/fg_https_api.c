#include "fg_https_api.h"
#include <string.h>
#include <stdio.h>
#include <limits.h>
#include "esp_https_server.h"
#include "esp_timer.h"
#define TOKEN_HEX_LEN 64
#define MAX_JSON_INPUT 96
static uint64_t now_ms(void){return (uint64_t)esp_timer_get_time()/1000U;}
static void wipe(void *p,size_t n){volatile unsigned char *v=p;while(n--)*v++=0;}
static esp_err_t answer(httpd_req_t *r,const char *status,const char *body){
 httpd_resp_set_status(r,status);
 httpd_resp_set_type(r,"application/json");
 httpd_resp_set_hdr(r,"Cache-Control","no-store");
 httpd_resp_set_hdr(r,"X-Content-Type-Options","nosniff");
 return httpd_resp_sendstr(r,body);
}
static int hex_digit(char c){
 if(c>='0'&&c<='9')return c-'0';
 if(c>='a'&&c<='f')return c-'a'+10;
 if(c>='A'&&c<='F')return c-'A'+10;
 return -1;
}
static bool parse_token(httpd_req_t *r,uint8_t token[32]){
 size_t len=httpd_req_get_hdr_value_len(r,"Authorization");
 if(len!=7+TOKEN_HEX_LEN)return false;
 char h[7+TOKEN_HEX_LEN+1];
 if(httpd_req_get_hdr_value_str(r,"Authorization",h,sizeof(h))!=ESP_OK)return false;
 if(memcmp(h,"Bearer ",7)!=0)return false;
 for(unsigned i=0;i<32;i++){
  int a=hex_digit(h[7+i*2]),b=hex_digit(h[8+i*2]);
  if(a<0||b<0)return false;
  token[i]=(uint8_t)(a*16+b);
 }
 wipe(h,sizeof(h));
 return true;
}
static void hex_write(char *dest,const uint8_t raw[32]){
 static const char alpha[]="0123456789abcdef";
 for(unsigned i=0;i<32;i++){
  dest[2*i]=alpha[raw[i]>>4];dest[2*i+1]=alpha[raw[i]&15];
 }
 dest[64]='\0';
}
static bool read_body(httpd_req_t *r,char text[MAX_JSON_INPUT]){
 if(r->content_len<=0||r->content_len>=MAX_JSON_INPUT)return false;
 int pos=0;
 while(pos<r->content_len){
  int n=httpd_req_recv(r,text+pos,(size_t)(r->content_len-pos));
  if(n<=0)return false;
  pos+=n;
 }
 text[pos]='\0';
 return memchr(text,'\0',(size_t)pos)==NULL;
}
static bool parse_pair_body(const char *text,uint32_t *code){
 /* Strict small literal body eliminates hidden fields and permissive conversions. */
 if(strlen(text)!=15||memcmp(text,"{\"code\":",8)!=0||text[14]!='}')return false;
 uint32_t n=0;
 for(unsigned i=8;i<14;i++){
  if(text[i]<'0'||text[i]>'9')return false;
  n=n*10u+(unsigned)(text[i]-'0');
 }
 if(n<100000u)return false;
 *code=n;return true;
}
static fg_web_role authorized(httpd_req_t *r,fg_https_api *s){
 uint8_t token[32]={0};fg_web_role role=FG_WEB_NO_ROLE;
 if(!parse_token(r,token))return role;
 if(xSemaphoreTake(s->auth_mutex,pdMS_TO_TICKS(200))==pdTRUE){
  role=fg_web_authenticate(s->auth,token,32);
  xSemaphoreGive(s->auth_mutex);
 }
 wipe(token,sizeof(token));return role;
}
static esp_err_t forbidden(httpd_req_t *r,fg_web_role role,const char *method){
 if(role==FG_WEB_NO_ROLE)return answer(r,"401 Unauthorized","{\"error\":\"authentication_required\"}");
 (void)method;return answer(r,"403 Forbidden","{\"error\":\"insufficient_role\"}");
}
static esp_err_t status_get(httpd_req_t *r){
 fg_https_api *s=r->user_ctx;fg_web_role role=authorized(r,s);
 if(!fg_web_permit(role,"GET","/v1/status"))return forbidden(r,role,"GET");
 char json[96];
 snprintf(json,sizeof(json),"{\"state\":%d,\"fault\":%d,\"motor_enable_unverified\":true}",
  atomic_load(s->shown_state),atomic_load(s->shown_fault));
 return answer(r,"200 OK",json);
}
static esp_err_t pair_post(httpd_req_t *r){
 fg_https_api *s=r->user_ctx;char body[MAX_JSON_INPUT];uint32_t code=0;
 if(!read_body(r,body)||!parse_pair_body(body,&code))
  return answer(r,"400 Bad Request","{\"error\":\"invalid_pairing_body\"}");
 if(xSemaphoreTake(s->auth_mutex,pdMS_TO_TICKS(500))!=pdTRUE)
  return answer(r,"503 Service Unavailable","{\"error\":\"auth_busy\"}");
 uint8_t token[32]={0};
 fg_web_result result=fg_web_claim_admin(s->auth,now_ms(),code,token);
 if(!s->auth->open)atomic_store(s->pairing_code_local,0u);
 xSemaphoreGive(s->auth_mutex);
 if(result!=FG_WEB_OK){
  wipe(token,sizeof(token));
  if(result==FG_WEB_PERSIST_FAILED)return answer(r,"503 Service Unavailable","{\"error\":\"storage_unavailable\"}");
  return answer(r,"403 Forbidden","{\"error\":\"pairing_rejected\"}");
 }
 char hex[65];hex_write(hex,token);wipe(token,sizeof(token));
 char response[96];snprintf(response,sizeof(response),"{\"admin_token\":\"%s\"}",hex);
 esp_err_t err=answer(r,"200 OK",response);wipe(hex,sizeof(hex));wipe(response,sizeof(response));return err;
}
static esp_err_t issue_post(httpd_req_t *r){
 fg_https_api *s=r->user_ctx;fg_web_role role=authorized(r,s);
 if(!fg_web_permit(role,"POST","/v1/token/issue"))return forbidden(r,role,"POST");
 char body[MAX_JSON_INPUT];
 if(!read_body(r,body))return answer(r,"400 Bad Request","{\"error\":\"invalid_body\"}");
 fg_web_role target=FG_WEB_NO_ROLE;
 if(strcmp(body,"{\"role\":\"viewer\"}")==0)target=FG_WEB_VIEWER;
 if(strcmp(body,"{\"role\":\"operator\"}")==0)target=FG_WEB_OPERATOR;
 if(target==FG_WEB_NO_ROLE)return answer(r,"400 Bad Request","{\"error\":\"invalid_role\"}");
 if(xSemaphoreTake(s->auth_mutex,pdMS_TO_TICKS(500))!=pdTRUE)
  return answer(r,"503 Service Unavailable","{\"error\":\"auth_busy\"}");
 uint8_t token[32]={0};fg_web_result result=fg_web_issue_role(s->auth,role,target,token);
 xSemaphoreGive(s->auth_mutex);
 if(result!=FG_WEB_OK){wipe(token,sizeof(token));return answer(r,"503 Service Unavailable","{\"error\":\"role_issuance_failed\"}");}
 char hex[65],response[96];hex_write(hex,token);wipe(token,sizeof(token));
 snprintf(response,sizeof(response),"{\"token\":\"%s\"}",hex);
 esp_err_t e=answer(r,"200 OK",response);wipe(hex,sizeof(hex));wipe(response,sizeof(response));return e;
}
static esp_err_t command_post(httpd_req_t *r){
 fg_https_api *s=r->user_ctx;fg_web_role role=authorized(r,s);
 if(!fg_web_permit(role,"POST",r->uri))return forbidden(r,role,"POST");
 if(r->content_len!=0)return answer(r,"400 Bad Request","{\"error\":\"body_not_supported\"}");
 fg_intent i={.authenticated=true,.explicit_request=true};
 /* Real M1 physical interlock + 7-axis HIL are NOT cleared.
  * Remote start and remote fault clear must never enter the 5ms control queue
  * before a separate reviewed hardware release. Local STOP remains available. */
 if(strcmp(r->uri,"/v1/motors/start")==0)
  return answer(r,"423 Locked","{\"error\":\"motor_power_interlock_not_qualified\"}");
 if(strcmp(r->uri,"/v1/fault/clear")==0)
  return answer(r,"423 Locked","{\"error\":\"physical_fault_clear_required\"}");
 if(strcmp(r->uri,"/v1/motors/stop")==0)i.kind=FG_INTENT_STOP_ALL;
 else return answer(r,"404 Not Found","{\"error\":\"unknown_intent\"}");
 /* Network task is producer ONLY. Start sequence assigned by sole control task. */
 if(xQueueSend(s->intent_queue,&i,0)!=pdTRUE)
  return answer(r,"503 Service Unavailable","{\"error\":\"control_queue_full\"}");
 return answer(r,"202 Accepted","{\"queued\":true,\"executed\":false}");
}
void fg_https_api_init(fg_https_api *s,fg_web_access *access,SemaphoreHandle_t lock,
                       QueueHandle_t queue,const atomic_int *state,const atomic_int *fault,
                       atomic_uint *pairing){
 if(!s)return;
 *s=(fg_https_api){.auth=access,.auth_mutex=lock,.intent_queue=queue,
  .shown_state=state,.shown_fault=fault,.pairing_code_local=pairing,.server=NULL};
}
bool fg_https_start_if_ready(fg_https_api *s,bool network_ready,
                             const uint8_t *cert,size_t certlen,const uint8_t *key,size_t keylen){
 if(!s||s->server||!network_ready||!s->auth||!s->auth_mutex||!s->intent_queue||
    !s->shown_state||!s->shown_fault||!s->pairing_code_local||
    !cert||!key||certlen<32||keylen<32||certlen>8192||keylen>8192)return false;
 if(memcmp(cert,"-----BEGIN CERTIFICATE-----",27)!=0||
    memcmp(key,"-----BEGIN ",11)!=0)return false;
 httpd_ssl_config_t cfg=HTTPD_SSL_CONFIG_DEFAULT();
 cfg.transport_mode=HTTPD_SSL_TRANSPORT_SECURE;
 cfg.servercert=cert;cfg.servercert_len=certlen;
 cfg.prvtkey_pem=key;cfg.prvtkey_len=keylen;
 cfg.httpd.max_uri_handlers=8;cfg.httpd.stack_size=10240;
 if(httpd_ssl_start(&s->server,&cfg)!=ESP_OK)return false;
 httpd_uri_t handlers[]={
  {.uri="/v1/pair",.method=HTTP_POST,.handler=pair_post,.user_ctx=s},
  {.uri="/v1/status",.method=HTTP_GET,.handler=status_get,.user_ctx=s},
  {.uri="/v1/token/issue",.method=HTTP_POST,.handler=issue_post,.user_ctx=s},
  {.uri="/v1/motors/start",.method=HTTP_POST,.handler=command_post,.user_ctx=s},
  {.uri="/v1/motors/stop",.method=HTTP_POST,.handler=command_post,.user_ctx=s},
  {.uri="/v1/fault/clear",.method=HTTP_POST,.handler=command_post,.user_ctx=s}
 };
 for(size_t i=0;i<sizeof(handlers)/sizeof(handlers[0]);i++){
  if(httpd_register_uri_handler(s->server,&handlers[i])!=ESP_OK){
   httpd_ssl_stop(s->server);s->server=NULL;return false;
  }
 }
 return true;
}
void fg_https_stop(fg_https_api *s){
 if(s&&s->server){httpd_ssl_stop(s->server);s->server=NULL;}
}
