#ifndef FG_OUTPUT_GUARD_H
#define FG_OUTPUT_GUARD_H
#include <stdbool.h>
#include <stdint.h>
#include "control.h"
typedef struct {
 void *context;
 bool (*fault_healthy)(void *context); /* live hardware FAULT positive = healthy */
 bool (*verified_apply)(void *context,const uint8_t phase_and_led[4]);
 void (*write_arm)(void *context,bool enabled);
} fg_output_io;
/* Execute only in controller task after fg_prepare(). On any failure ARM is
   immediately deasserted and controller latched FAULT. No watchdog substitute. */
bool fg_output_commit(fg_control *controller,const fg_output_io *io);
#endif
