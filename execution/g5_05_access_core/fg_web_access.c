#include "fg_web_access.h"
#include <string.h>
#ifdef FG_WEB_HOST_TEST
#include <openssl/sha.h>
static bool digest(const uint8_t *in,uint8_t out[32]){return SHA256(in,32,out)!=NULL;}
#else
#include "mbedtls/sha256.h"
static bool digest(const uint8_t *in,uint8_t out[32]){return mbedtls_sha256(in,32,out,0)==0;}
#endif
static void wipe(void *p,size_t n){volatile uint8_t *b=p;while(n--)*b++=0;}
static bool constant_equal(const uint8_t *a,const uint8_t *b,size_t n){unsigned x=0;for(size_t i=0;i<n;i++)x|=(unsigned)(a[i]^b[i]);return x==0;}
static bool commit(fg_web_access *a,unsigned role,const uint8_t hash[32]){
 fg_web_credentials proposed=a->credentials;
 proposed.by_role[role].active=true;memcpy(proposed.by_role[role].sha256,hash,32);
 if(!a->save(a->io_context,&proposed))return false;
 a->credentials=proposed;return true;
}
void fg_web_access_init(fg_web_access *a,fg_web_credentials existing,fg_web_save_fn save,fg_web_random_fn random,void *ctx){
 if(!a)return;memset(a,0,sizeof(*a));a->credentials=existing;a->save=save;a->random=random;a->io_context=ctx;
}
void fg_web_access_expire(fg_web_access *a,uint64_t now){
 if(a&&a->open&&now>=a->window_end_ms){a->open=false;a->local_code=0;}
}
bool fg_web_open_local_pairing(fg_web_access *a,uint64_t now,uint32_t *code){
 if(!a||!code||!a->random||!a->save||now>UINT64_MAX-FG_WEB_PAIR_WINDOW_MS)return false;
 if(now<a->lock_end_ms)return false;
 uint8_t seed[4];if(!a->random(a->io_context,seed,4))return false;
 uint32_t v=(uint32_t)seed[0]|((uint32_t)seed[1]<<8)|((uint32_t)seed[2]<<16)|((uint32_t)seed[3]<<24);
 wipe(seed,4);a->local_code=100000u+v%900000u;a->window_end_ms=now+FG_WEB_PAIR_WINDOW_MS;
 a->open=true;a->failures=0;*code=a->local_code;return true;
}
fg_web_result fg_web_claim_admin(fg_web_access *a,uint64_t now,uint32_t code,uint8_t token[32]){
 if(!a||!token||!a->random||!a->save)return FG_WEB_BAD_ARGUMENT;
 memset(token,0,32);fg_web_access_expire(a,now);
 if(!a->open||now<a->lock_end_ms)return FG_WEB_DENIED;
 if(code<100000u||code>999999u||code!=a->local_code){
  if(++a->failures>=FG_WEB_PAIR_MAX_TRIES){
   a->open=false;a->local_code=0;a->lock_end_ms=now>UINT64_MAX-FG_WEB_PAIR_LOCK_MS?UINT64_MAX:now+FG_WEB_PAIR_LOCK_MS;
  }return FG_WEB_DENIED;
 }
 uint8_t raw[32],hash[32];if(!a->random(a->io_context,raw,32))return FG_WEB_DENIED;
 if(!digest(raw,hash)){wipe(raw,32);return FG_WEB_DENIED;}
 if(!commit(a,FG_WEB_ADMIN-1u,hash)){wipe(raw,32);wipe(hash,32);return FG_WEB_PERSIST_FAILED;}
 memcpy(token,raw,32);wipe(raw,32);wipe(hash,32);a->open=false;a->local_code=0;a->failures=0;return FG_WEB_OK;
}
fg_web_result fg_web_issue_role(fg_web_access *a,fg_web_role actor,fg_web_role target,uint8_t token[32]){
 if(!a||!token||!a->random||!a->save||target<FG_WEB_VIEWER||target>FG_WEB_OPERATOR)return FG_WEB_BAD_ARGUMENT;
 memset(token,0,32);if(actor!=FG_WEB_ADMIN)return FG_WEB_DENIED;
 uint8_t raw[32],hash[32];if(!a->random(a->io_context,raw,32))return FG_WEB_DENIED;
 if(!digest(raw,hash)){wipe(raw,32);return FG_WEB_DENIED;}
 if(!commit(a,(unsigned)target-1u,hash)){wipe(raw,32);wipe(hash,32);return FG_WEB_PERSIST_FAILED;}
 memcpy(token,raw,32);wipe(raw,32);wipe(hash,32);return FG_WEB_OK;
}
fg_web_role fg_web_authenticate(const fg_web_access *a,const uint8_t *token,size_t size){
 if(!a||!token||size!=32)return FG_WEB_NO_ROLE;uint8_t hash[32];
 if(!digest(token,hash))return FG_WEB_NO_ROLE;
 fg_web_role role=FG_WEB_NO_ROLE;
 for(unsigned i=0;i<FG_WEB_ROLE_COUNT;i++){
  const fg_web_credential *s=&a->credentials.by_role[i];
  if(s->active&&constant_equal(s->sha256,hash,32))role=(fg_web_role)(i+1u);
 }
 wipe(hash,32);return role;
}
bool fg_web_permit(fg_web_role role,const char *method,const char *path){
 if(!method||!path||role<FG_WEB_VIEWER||role>FG_WEB_ADMIN)return false;
 if(!strcmp(method,"GET")&&!strcmp(path,"/v1/status"))return true;
 if(strcmp(method,"POST"))return false;
 if(!strcmp(path,"/v1/motors/stop")||!strcmp(path,"/v1/motors/start")||!strcmp(path,"/v1/leds"))return role>=FG_WEB_OPERATOR;
 if(!strcmp(path,"/v1/fault/clear")||!strcmp(path,"/v1/token/issue"))return role==FG_WEB_ADMIN;
 return false;
}
