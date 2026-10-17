#ifndef FG_INTENT_H
#define FG_INTENT_H
#include <stdbool.h>
#include <stdint.h>
#include "control.h"
/* Sole writer is the existing D7 control task. This is a request-only adapter;
   there is no second motor state machine and no raw phase/ARM command. */
typedef enum {
 FG_INTENT_START_ALL=1, FG_INTENT_STOP_ALL, FG_INTENT_CLEAR_FAULT,
 FG_INTENT_LIGHTS_SET
} fg_intent_kind;
typedef struct {
 fg_intent_kind kind;
 uint64_t sequence;
 bool authenticated;
 bool explicit_request;
 bool lights_on;
} fg_intent;
typedef struct {bool hardware_healthy;bool arm_is_low;uint64_t now_us;} fg_intent_context;
/* Must be called only by the 5ms control task; NOT a thread-safe endpoint. */
bool fg_intent_apply(fg_control *controller,const fg_intent *intent,fg_intent_context context);
#endif
