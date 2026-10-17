#include "fg_ota_gate.h"
fg_ota_result fg_ota_stage(const fg_ota_source *source,fg_ota_ops *io,
                           size_t expected_bytes,bool motors_off_proven,
                           bool independent_hil_approved){
 if(!source||!source->read||!io||!io->ready||!io->begin_inactive||!io->write||
    !io->finish_verified||!io->select_next_boot||!io->abort||
    expected_bytes<FG_OTA_MIN_IMAGE_BYTES||expected_bytes>FG_OTA_SLOT_CAPACITY)
  return FG_OTA_REJECTED;
 if(!motors_off_proven||!independent_hil_approved||!io->ready(io->context))
  return FG_OTA_READY_NOT_APPROVED;
 if(!io->begin_inactive(io->context,expected_bytes))
  return FG_OTA_FLASH_FAILURE;
 uint8_t buf[FG_OTA_CHUNK_SIZE]={0};
 size_t sent=0;
 while(sent<expected_bytes){
  size_t need=expected_bytes-sent;
  if(need>sizeof(buf))need=sizeof(buf);
  int32_t got=source->read(source->context,buf,need);
  if(got<=0||(size_t)got>need){
   io->abort(io->context);
   return FG_OTA_SOURCE_FAILURE;
  }
  if(!io->write(io->context,buf,(size_t)got)){
   io->abort(io->context);
   return FG_OTA_FLASH_FAILURE;
  }
  sent+=(size_t)got;
 }
 /* esp_ota_end consumes the handle even when signature verification fails;
  * do not double-abort. The old boot selection is unchanged on failure. */
 if(!io->finish_verified(io->context))
  return FG_OTA_SIGNATURE_FAILURE;
 if(!io->select_next_boot(io->context))
  return FG_OTA_BOOT_SELECTION_FAILURE;
 return FG_OTA_STAGED_PENDING_REBOOT;
}
