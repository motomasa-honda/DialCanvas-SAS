#include "control.h"
#include <string.h>
static const int8_t direction[7]={1,-1,1,-1,1,-1,1};
/* Fixed internal rates: 20..32 wave-drive steps/s, no user speed control. */
static const uint32_t period_us[7]={31250,38462,33333,45455,35714,41667,50000};
void fg_init(fg_control *c){memset(c,0,sizeof(*c));c->state=FG_BOOT;c->led[0]=c->led[1]=true;}
static void zero(fg_control *c){c->arm=false;memset(c->phase,0,sizeof(c->phase));}
void fg_fail(fg_control *c,const char *reason){zero(c);c->state=FG_FAULT;c->fault=reason;}
void fg_stop(fg_control *c){zero(c);if(c->state==FG_RUN||c->state==FG_STARTING)c->state=FG_OFF;}
void fg_boot_ok(fg_control *c){if(c->state==FG_BOOT){zero(c);c->state=FG_OFF;}}
bool fg_start(fg_control *c,uint64_t sequence,uint64_t now,bool authorized,bool healthy){
 if(!authorized||sequence<=c->last_sequence)return false;
 c->last_sequence=sequence;
 if(c->state!=FG_OFF||!healthy)return false;
 c->state=FG_STARTING;c->arm=true;c->start_at=now;return true;
}
bool fg_clear(fg_control *c,bool explicit_request,bool healthy){
 if(c->state!=FG_FAULT||!explicit_request||!healthy)return false;
 zero(c);c->state=FG_OFF;c->fault=0;return true;
}
void fg_prepare(fg_control *c,uint64_t now,bool healthy){
 if(!healthy){fg_fail(c,"physical_fault");return;}
 if(c->state==FG_STARTING){
  if(now-c->start_at<100000)return;
  c->state=FG_RUN;
  for(unsigned i=0;i<7;i++){c->phase_index[i]=0;c->phase[i]=1;c->next_step[i]=now+period_us[i];}
 }
 if(c->state!=FG_RUN)return;
 for(unsigned i=0;i<7;i++){
  if(now<c->next_step[i])continue;
  if(now-c->next_step[i]>5000){fg_fail(c,"phase_deadline");return;}
  c->phase_index[i]=(uint8_t)((c->phase_index[i]+direction[i]+4)%4);
  c->phase[i]=(uint8_t)(1u<<c->phase_index[i]);c->next_step[i]+=period_us[i];
 }
}
void fg_ports(const fg_control *c,uint8_t out[4]){
 out[0]=c->phase[0]|(uint8_t)(c->phase[1]<<4);out[1]=c->phase[2]|(uint8_t)(c->phase[3]<<4);
 out[2]=c->phase[4]|(uint8_t)(c->phase[5]<<4);
 out[3]=c->phase[6]|(uint8_t)(c->led[0]<<4)|(uint8_t)(c->led[1]<<5);
}
bool fg_heartbeat(fg_control *c,uint64_t now,bool verified){
 if(!verified||(c->state!=FG_OFF&&c->state!=FG_STARTING&&c->state!=FG_RUN))return false;
 for(unsigned i=0;i<7;i++)if(c->phase[i] && (c->phase[i]&(c->phase[i]-1))) {fg_fail(c,"multiple_phase");return false;}
 if(now-c->last_hb<50000)return false;
 c->hb=!c->hb;c->last_hb=now;return true;
}
void fg_buttons_init(fg_buttons *b,uint64_t now){memset(b,0,sizeof(*b));b->raw_changed_at[0]=b->raw_changed_at[1]=now;}
fg_button_action fg_buttons_update(fg_buttons *b,bool sw1,bool sw2,uint64_t now){
 bool input[2]={sw1,sw2},released[2]={false,false};
 for(unsigned i=0;i<2;i++){
  if(input[i]!=b->raw[i]){b->raw[i]=input[i];b->raw_changed_at[i]=now;}
  if(b->raw[i]!=b->stable[i]&&now-b->raw_changed_at[i]>=30000){
   b->stable[i]=b->raw[i];
   if(b->stable[i]){b->pressed_at[i]=now;b->consumed[i]=false;}
   else released[i]=true;
  }
 }
 if(b->stable[0]&&b->stable[1]&&!b->chord_active){
  b->chord_active=true;b->chord_fired=false;b->chord_started_at=now;
  b->consumed[0]=b->consumed[1]=true;
 }
 if(b->chord_active){
  if(b->stable[0]&&b->stable[1]&&!b->chord_fired&&now-b->chord_started_at>=5000000){
   b->chord_fired=true;return FG_BUTTON_REQUEST_PAIRING;
  }
  if(!b->stable[0]&&!b->stable[1]){
   b->chord_active=false;b->chord_fired=false;b->consumed[0]=b->consumed[1]=false;
  }
  return FG_BUTTON_NONE;
 }
 if(released[0]){
  uint64_t held=now-b->pressed_at[0];b->consumed[0]=false;
  if(held>=30000&&held<2000000)return FG_BUTTON_VIEW_TOGGLE;
 }
 if(released[1]){
  uint64_t held=now-b->pressed_at[1];bool consumed=b->consumed[1];b->consumed[1]=false;
  if(!consumed&&held>=30000&&held<2000000)return FG_BUTTON_MOTORS_TOGGLE;
 }
 if(b->stable[1]&&!b->stable[0]&&!b->consumed[1]&&now-b->pressed_at[1]>=2000000){
  b->consumed[1]=true;return FG_BUTTON_LIGHTS_TOGGLE;
 }
 return FG_BUTTON_NONE;
}
