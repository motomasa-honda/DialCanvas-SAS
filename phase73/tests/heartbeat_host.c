#include "control.h"
#include "fg_heartbeat_config.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    _Static_assert(FG_HEARTBEAT_TOGGLE_US==40000ULL,"incorrect toggle");
    _Static_assert(FG_HEARTBEAT_FALL_PERIOD_US==80000ULL,"incorrect falling period");
    fg_control c;
    fg_init(&c);fg_boot_ok(&c);
    assert(c.state==FG_OFF&&!c.arm&&!c.hb);
    assert(!fg_heartbeat(&c,39999,true));
    assert(fg_heartbeat(&c,40000,true)&&c.hb);
    assert(!fg_heartbeat(&c,79999,true));
    assert(fg_heartbeat(&c,80000,true)&&!c.hb);
    assert(fg_heartbeat(&c,120000,true)&&c.hb);
    assert(fg_heartbeat(&c,160000,true)&&!c.hb);
    assert(!fg_heartbeat(&c,200000,false));
    c.phase[0]=3;
    assert(!fg_heartbeat(&c,240000,true));
    assert(c.state==FG_FAULT&&!c.arm);
    assert(!fg_heartbeat(&c,280000,true));
    puts("PASS: 80ms nominal falling period, fail on unhealthy and illegal phases");
    return 0;
}
