#include "fg_ota_gate.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef struct{
 size_t left,written;
 unsigned ready,begin,write,end,selected,aborted,read_count;
 bool ready_ok,begin_ok,write_ok,end_ok,select_ok;
 int fail_read_at;
 int fail_write_at;
} mock;
static uint8_t fixture[FG_OTA_SLOT_CAPACITY+1];
static int32_t read_chunk(void *ptr,uint8_t *dst,size_t max){
 mock *s=ptr;
 if((int)(++s->read_count)==s->fail_read_at)return -1;
 if(s->left==0)return 0;
 size_t n=s->left<max?s->left:max;
 memset(dst,0xA5,n);s->left-=n;
 return (int32_t)n;
}
static bool config(void *ctx){mock *s=ctx;s->ready++;return s->ready_ok;}
static bool begin(void *ctx,size_t bytes){
 mock *s=ctx;s->begin++;return s->begin_ok&&bytes<=FG_OTA_SLOT_CAPACITY;
}
static bool write_part(void *ctx,const uint8_t *chunk,size_t n){
 mock *s=ctx;
 s->write++;
 if((int)s->write==s->fail_write_at)return false;
 assert(chunk&&n&&n<=FG_OTA_CHUNK_SIZE);
 for(size_t i=0;i<n;i++)assert(chunk[i]==0xA5);
 s->written+=n;return s->write_ok;
}
static bool end_auth(void *ctx){mock *s=ctx;s->end++;return s->end_ok;}
static bool choose_boot(void *ctx){mock *s=ctx;s->selected++;return s->select_ok;}
static void abort_stage(void *ctx){mock *s=ctx;s->aborted++;}
static mock fresh(size_t total){
 mock x={0};x.left=total;x.ready_ok=x.begin_ok=x.write_ok=x.end_ok=x.select_ok=true;
 x.fail_read_at=-1;x.fail_write_at=-1;return x;
}
static fg_ota_result run(mock *s,size_t size,bool off,bool hil){
 fg_ota_source src={.context=s,.read=read_chunk};
 fg_ota_ops o={.context=s,.ready=config,.begin_inactive=begin,.write=write_part,
  .finish_verified=end_auth,.select_next_boot=choose_boot,.abort=abort_stage};
 return fg_ota_stage(&src,&o,size,off,hil);
}
int main(void){
 (void)fixture;
 mock m=fresh(2049);
 /* No HIL -> no signed app validation, no erase, no flash, no partition choice. */
 assert(run(&m,2049,true,false)==FG_OTA_READY_NOT_APPROVED);
 assert(m.ready==0&&m.begin==0&&m.write==0&&m.selected==0);
 m=fresh(2049);
 assert(run(&m,2049,false,true)==FG_OTA_READY_NOT_APPROVED);
 assert(m.ready==0&&m.begin==0);
 m=fresh(2049);m.ready_ok=false;
 assert(run(&m,2049,true,true)==FG_OTA_READY_NOT_APPROVED);
 assert(m.ready==1&&m.begin==0);
 m=fresh(0);
 assert(run(&m,FG_OTA_MIN_IMAGE_BYTES-1,true,true)==FG_OTA_REJECTED);
 assert(m.ready==0&&m.begin==0);
 m=fresh(0);
 assert(run(&m,FG_OTA_SLOT_CAPACITY+1,true,true)==FG_OTA_REJECTED);
 assert(m.begin==0);
 m=fresh(2049);m.begin_ok=false;
 assert(run(&m,2049,true,true)==FG_OTA_FLASH_FAILURE);
 assert(m.begin==1&&m.write==0&&m.aborted==0&&m.selected==0);
 m=fresh(2049);
 assert(run(&m,2049,true,true)==FG_OTA_STAGED_PENDING_REBOOT);
 assert(m.write==3&&m.written==2049&&m.end==1&&m.selected==1&&m.aborted==0);
 m=fresh(2049);m.fail_read_at=2;
 assert(run(&m,2049,true,true)==FG_OTA_SOURCE_FAILURE);
 assert(m.aborted==1&&m.end==0&&m.selected==0);
 m=fresh(2049);m.fail_write_at=2;
 assert(run(&m,2049,true,true)==FG_OTA_FLASH_FAILURE);
 assert(m.aborted==1&&m.end==0&&m.selected==0);
 m=fresh(2049);m.end_ok=false;
 assert(run(&m,2049,true,true)==FG_OTA_SIGNATURE_FAILURE);
 assert(m.end==1&&m.selected==0&&m.aborted==0);
 m=fresh(2049);m.select_ok=false;
 assert(run(&m,2049,true,true)==FG_OTA_BOOT_SELECTION_FAILURE);
 assert(m.end==1&&m.selected==1&&m.aborted==0);
 m=fresh(FG_OTA_SLOT_CAPACITY);
 assert(run(&m,FG_OTA_SLOT_CAPACITY,true,true)==FG_OTA_STAGED_PENDING_REBOOT);
 assert(m.written==FG_OTA_SLOT_CAPACITY&&m.end==1&&m.selected==1);
 puts("PASS OTA transactional host: HIL/config gate blocks flash, exact slot limit, signed end before select, 3 failure abort paths");
 return 0;
}
