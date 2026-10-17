#include "fg_web_access.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static fg_web_credentials saved;
static bool save_ok=true,random_ok=true;
static unsigned char n=11;
static bool save(void *arg,const fg_web_credentials *c){(void)arg;if(!save_ok)return false;saved=*c;return true;}
static bool randbytes(void *arg,uint8_t *d,size_t z){(void)arg;if(!random_ok)return false;for(size_t i=0;i<z;i++)d[i]=++n;return true;}
int main(void){
 fg_web_access a;fg_web_access_init(&a,saved,save,randbytes,0);uint32_t code=0;uint8_t admin[32],oper[32],viewer[32],wrong[32];
 assert(!fg_web_permit(FG_WEB_NO_ROLE,"POST","/v1/motors/start"));
 assert(fg_web_claim_admin(&a,0,123456,wrong)==FG_WEB_DENIED);
 assert(fg_web_open_local_pairing(&a,1000,&code)&&code>=100000&&code<=999999);
 for(unsigned i=0;i<FG_WEB_PAIR_MAX_TRIES;i++)
  assert(fg_web_claim_admin(&a,2000,code==100000?100001:100000,wrong)==FG_WEB_DENIED);
 assert(!fg_web_open_local_pairing(&a,2000,&code));
 assert(fg_web_claim_admin(&a,2500,code,wrong)==FG_WEB_DENIED);
 assert(fg_web_open_local_pairing(&a,302000,&code));
 save_ok=false;assert(fg_web_claim_admin(&a,302001,code,wrong)==FG_WEB_PERSIST_FAILED);
 assert(!a.credentials.by_role[FG_WEB_ADMIN-1].active);
 save_ok=true;assert(fg_web_claim_admin(&a,302002,code,admin)==FG_WEB_OK);
 assert(fg_web_claim_admin(&a,302003,code,wrong)==FG_WEB_DENIED);
 assert(fg_web_authenticate(&a,admin,32)==FG_WEB_ADMIN);
 assert(fg_web_authenticate(&a,admin,31)==FG_WEB_NO_ROLE);
 assert(!fg_web_permit(FG_WEB_ADMIN,"GET","/v1/motors/start"));
 assert(!fg_web_permit(FG_WEB_ADMIN,"POST","/v1/raw_gpio"));
 assert(fg_web_issue_role(&a,FG_WEB_VIEWER,FG_WEB_OPERATOR,wrong)==FG_WEB_DENIED);
 assert(fg_web_issue_role(&a,FG_WEB_ADMIN,FG_WEB_OPERATOR,oper)==FG_WEB_OK);
 assert(fg_web_issue_role(&a,FG_WEB_ADMIN,FG_WEB_VIEWER,viewer)==FG_WEB_OK);
 assert(fg_web_authenticate(&a,oper,32)==FG_WEB_OPERATOR&&fg_web_authenticate(&a,viewer,32)==FG_WEB_VIEWER);
 assert(!fg_web_permit(FG_WEB_VIEWER,"POST","/v1/motors/start"));
 assert(fg_web_permit(FG_WEB_OPERATOR,"POST","/v1/motors/start"));
 assert(!fg_web_permit(FG_WEB_OPERATOR,"POST","/v1/fault/clear"));
 assert(fg_web_permit(FG_WEB_ADMIN,"POST","/v1/fault/clear"));
 fg_web_access b;fg_web_access_init(&b,saved,save,randbytes,0);
 assert(fg_web_authenticate(&b,admin,32)==FG_WEB_ADMIN);
 assert(fg_web_authenticate(&b,oper,32)==FG_WEB_OPERATOR);
 random_ok=false;assert(!fg_web_open_local_pairing(&b,400000,&code));
 random_ok=true;assert(fg_web_open_local_pairing(&b,400000,&code));
 assert(fg_web_claim_admin(&b,460000,code,wrong)==FG_WEB_DENIED);
 puts("PASS physically opened pairing window, five-failure lockout, persisted token-digest role ACL, deny-by-default");
}
