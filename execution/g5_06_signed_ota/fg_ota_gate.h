#ifndef FG_OTA_GATE_H
#define FG_OTA_GATE_H
/* Transport-agnostic, fail-closed signed app A/B staging transaction.
 * Real ESP-IDF port enforces signed-app verification and rollback at build-time.
 * Review-only: no device, partition, eFuse or OTA source is authorized. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define FG_OTA_SLOT_CAPACITY (0x380000u)
#define FG_OTA_CHUNK_SIZE (1024u)
#define FG_OTA_MIN_IMAGE_BYTES (512u)
typedef enum {
 FG_OTA_REJECTED=0,
 FG_OTA_READY_NOT_APPROVED,
 FG_OTA_SOURCE_FAILURE,
 FG_OTA_FLASH_FAILURE,
 FG_OTA_SIGNATURE_FAILURE,
 FG_OTA_BOOT_SELECTION_FAILURE,
 FG_OTA_STAGED_PENDING_REBOOT
} fg_ota_result;
typedef int32_t (*fg_ota_reader)(void *ctx,uint8_t *buffer,size_t capacity);
/* read() must return 0 only at true transport EOF, including after the
 * declared image byte count. Positive short reads are allowed. */
typedef struct {void *context;fg_ota_reader read;} fg_ota_source;
typedef struct {
 void *context;
 bool (*ready)(void *context);
 bool (*begin_inactive)(void *context,size_t bytes);
 bool (*write)(void *context,const uint8_t *data,size_t length);
 /* Return true ONLY after the platform authenticated the signed app.
  * Consumes the OTA write handle even when returning false. */
 bool (*finish_verified)(void *context);
 /* Never boot-select until finish_verified succeeded. */
 bool (*select_next_boot)(void *context);
 void (*abort)(void *context);
} fg_ota_ops;
/* Both booleans must be demonstrated by physical HIL, not inferred from web auth.
 * No caller in the review product passes true (thus no flash write can start). */
fg_ota_result fg_ota_stage(const fg_ota_source *source,fg_ota_ops *io,
                           size_t expected_bytes,bool motors_off_proven,
                           bool independent_hil_approved);
#endif
