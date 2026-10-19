#include "fg_intent.h"
#include <stdint.h>
bool fg_intent_apply(fg_control *c,const fg_intent *i,fg_intent_context ctx){
 if(!c||!i||!i->authenticated||!i->explicit_request)return false;
 switch(i->kind){
 case FG_INTENT_START_ALL:
  if(i->sequence==0||i->sequence==UINT64_MAX)return false;
  return fg_start(c,i->sequence,ctx.now_us,true,ctx.hardware_healthy);
 case FG_INTENT_STOP_ALL:
  fg_stop(c);return true;
 case FG_INTENT_CLEAR_FAULT:
  /* Clearing a fault requires physical health and verified ARM deassertion. */
  if(!ctx.arm_is_low)return false;
  return fg_clear(c,true,ctx.hardware_healthy);
 case FG_INTENT_LIGHTS_SET:
  c->led[0]=c->led[1]=i->lights_on;return true;
 default:return false;
 }
}
