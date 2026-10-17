#pragma once
#include <stdint.h>
#include <stdbool.h>
typedef enum { FG_BOOT, FG_OFF, FG_STARTING, FG_RUN, FG_FAULT } fg_state;
typedef struct {
 fg_state state; bool arm,led[2]; uint8_t phase[7],phase_index[7];
 uint64_t next_step[7],start_at,last_hb,last_sequence; bool hb;
 const char *fault;
} fg_control;
typedef enum {
 FG_BUTTON_NONE,
 FG_BUTTON_VIEW_TOGGLE,
 FG_BUTTON_MOTORS_TOGGLE,
 FG_BUTTON_LIGHTS_TOGGLE,
 FG_BUTTON_REQUEST_PAIRING
} fg_button_action;
typedef struct {
 bool raw[2],stable[2],consumed[2],chord_active,chord_fired;
 uint64_t raw_changed_at[2],pressed_at[2],chord_started_at;
} fg_buttons;
void fg_init(fg_control *c);
void fg_fail(fg_control *c,const char *reason);
void fg_stop(fg_control *c);
void fg_boot_ok(fg_control *c);
bool fg_start(fg_control *c,uint64_t sequence,uint64_t now,bool authorized,bool healthy);
bool fg_clear(fg_control *c,bool explicit_request,bool healthy);
void fg_prepare(fg_control *c,uint64_t now,bool healthy);
void fg_ports(const fg_control *c,uint8_t out[4]);
bool fg_heartbeat(fg_control *c,uint64_t now,bool verified);
void fg_buttons_init(fg_buttons *b,uint64_t now_us);
fg_button_action fg_buttons_update(fg_buttons *b,bool sw1_pressed,bool sw2_pressed,uint64_t now_us);
