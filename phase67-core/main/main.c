/* Target-compiled functional probe using exact Forest Guardian Phase66 core
 * sources; no physical GPIO, motor driver, flash or BSP interfaces.
 * Compilation succeeds only when real fg_control/intent/output_guard link. */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "esp_log.h"
#include "control.h"
#include "fg_intent.h"
#include "fg_output_guard.h"

typedef struct {
    bool physical_fault_clear;
    bool verified;
    bool arm_output;
    unsigned verify_calls;
    unsigned arm_writes;
} virtual_outputs;

static bool fault_ok(void *arg) {
    return ((virtual_outputs *)arg)->physical_fault_clear;
}
static bool apply_verified(void *arg, const uint8_t bytes[4]) {
    virtual_outputs *v=(virtual_outputs *)arg;
    v->verify_calls++;
    (void)bytes;
    return v->verified;
}
static void set_arm(void *arg, bool enabled) {
    virtual_outputs *v=(virtual_outputs *)arg;
    v->arm_output=enabled;
    v->arm_writes++;
}
#define REQUIRE(expr) do { if(!(expr)) { ESP_LOGE("FG67","FAIL: %s:%d: %s",__FILE__,__LINE__,#expr); abort(); } } while(0)
#include <stdlib.h>
void app_main(void) {
    fg_control controller;
    fg_init(&controller);
    REQUIRE(controller.state==FG_BOOT);
    fg_boot_ok(&controller);
    REQUIRE(controller.state==FG_OFF && !controller.arm);

    fg_intent i={.kind=FG_INTENT_START_ALL,.sequence=1,.authenticated=false,.explicit_request=true};
    fg_intent_context ctx={.now_us=1000000,.hardware_healthy=true,.arm_is_low=true};
    REQUIRE(!fg_intent_apply(&controller,&i,ctx));
    REQUIRE(controller.state==FG_OFF);
    i.authenticated=true;
    REQUIRE(fg_intent_apply(&controller,&i,ctx));
    REQUIRE(controller.state==FG_STARTING);
    fg_prepare(&controller,ctx.now_us+100000,true);
    REQUIRE(controller.state==FG_RUN);
    REQUIRE(!fg_intent_apply(&controller,&i,ctx)); /* replay refused */

    virtual_outputs virtual_hw={.physical_fault_clear=true,.verified=true};
    fg_output_io ops={.context=&virtual_hw,.fault_healthy=fault_ok,.verified_apply=apply_verified,.write_arm=set_arm};
    REQUIRE(fg_output_commit(&controller,&ops));
    REQUIRE(virtual_hw.arm_output && virtual_hw.verify_calls==1);
    virtual_hw.physical_fault_clear=false;
    REQUIRE(!fg_output_commit(&controller,&ops));
    REQUIRE(controller.state==FG_FAULT && !controller.arm && !virtual_hw.arm_output);
    i.kind=FG_INTENT_CLEAR_FAULT;
    REQUIRE(!fg_intent_apply(&controller,&i,ctx)); /* unhealthy hardware */
    ctx.hardware_healthy=true;ctx.arm_is_low=false;
    REQUIRE(!fg_intent_apply(&controller,&i,ctx)); /* ARM not verified low */
    ctx.arm_is_low=true;
    REQUIRE(fg_intent_apply(&controller,&i,ctx));
    REQUIRE(controller.state==FG_OFF && !controller.arm);
    ESP_LOGI("FG67","PASS: real motor control, intent, ARM guard linked (virtual IO only)");
}
