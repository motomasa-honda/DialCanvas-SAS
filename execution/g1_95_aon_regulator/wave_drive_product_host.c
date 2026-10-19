#include "control.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static const uint64_t duration_us = 20000000ULL;

static uint8_t output_phase(const uint8_t ports[4], unsigned axis) {
    switch (axis) {
        case 0: return ports[0] & 0x0f;
        case 1: return ports[0] >> 4;
        case 2: return ports[1] & 0x0f;
        case 3: return ports[1] >> 4;
        case 4: return ports[2] & 0x0f;
        case 5: return ports[2] >> 4;
        default: return ports[3] & 0x0f;
    }
}

static void assert_outputs_are_one_hot(const fg_control *c) {
    uint8_t ports[4];
    fg_ports(c, ports);
    for (unsigned axis = 0; axis < 7; ++axis) {
        uint8_t phase = output_phase(ports, axis);
        assert(phase == c->phase[axis]);
        assert(phase != 0);
        assert((phase & (phase - 1)) == 0);
    }
}

int main(void) {
    static const uint8_t direction[7] = {1, 3, 1, 3, 1, 3, 1};
    static const uint32_t periods[7] = {31250, 38462, 33333, 45455, 35714, 41667, 50000};
    fg_control c;
    fg_init(&c);
    fg_boot_ok(&c);
    assert(c.state == FG_OFF && !c.arm);
    for (unsigned axis = 0; axis < 7; ++axis) assert(c.phase[axis] == 0);
    assert(fg_start(&c, 1, 0, true, true));
    fg_prepare(&c, 99999, true);
    assert(c.state == FG_STARTING);
    for (unsigned axis = 0; axis < 7; ++axis) assert(c.phase[axis] == 0);
    fg_prepare(&c, 100000, true);
    assert(c.state == FG_RUN && c.arm);
    assert_outputs_are_one_hot(&c);
    for (unsigned axis = 0; axis < 7; ++axis) {
        assert(c.phase[axis] == 1);
        assert(c.next_step[axis] == 100000 + periods[axis]);
    }

    uint64_t now = 100000;
    uint64_t until = now + duration_us;
    uint64_t previous_transition[7] = {100000,100000,100000,100000,100000,100000,100000};
    uint32_t transitions[7] = {0};
    double slowest_rpm = 100.0, fastest_rpm = 0.0;
    while (true) {
        uint64_t next = UINT64_MAX;
        for (unsigned axis = 0; axis < 7; ++axis)
            if (c.next_step[axis] < next) next = c.next_step[axis];
        if (next > until) break;
        now = next;
        uint8_t before[7], before_index[7];
        for (unsigned axis = 0; axis < 7; ++axis) {
            before[axis] = c.phase[axis];
            before_index[axis] = c.phase_index[axis];
        }
        fg_prepare(&c, now, true);
        assert(c.state == FG_RUN && c.arm);
        assert_outputs_are_one_hot(&c);
        for (unsigned axis = 0; axis < 7; ++axis) {
            if (c.phase[axis] == before[axis]) continue;
            uint8_t expected_index = (uint8_t)((before_index[axis] + direction[axis]) % 4);
            assert(c.phase[axis] == (uint8_t)(1u << expected_index));
            uint64_t gap = now - previous_transition[axis];
            assert(gap == periods[axis]);
            double rpm = 60000000.0 / ((double)gap * 516.0);
            assert(rpm > 0.0 && rpm < 6.0);
            if (rpm < slowest_rpm) slowest_rpm = rpm;
            if (rpm > fastest_rpm) fastest_rpm = rpm;
            previous_transition[axis] = now;
            transitions[axis]++;
        }
    }
    for (unsigned axis = 0; axis < 7; ++axis) assert(transitions[axis] >= 350);
    assert(slowest_rpm > 2.30 && slowest_rpm < 2.35);
    assert(fastest_rpm > 3.70 && fastest_rpm < 3.75);

    fg_stop(&c);
    assert(c.state == FG_OFF && !c.arm);
    for (unsigned axis = 0; axis < 7; ++axis) assert(c.phase[axis] == 0);
    assert(fg_start(&c, 2, now + 1000, true, true));
    fg_prepare(&c, now + 101000, true);
    assert(c.state == FG_RUN && c.arm);
    assert_outputs_are_one_hot(&c);
    fg_prepare(&c, now + 102000, false);
    assert(c.state == FG_FAULT && !c.arm);
    for (unsigned axis = 0; axis < 7; ++axis) assert(c.phase[axis] == 0);
    printf("PASS: SHA-pinned product firmware runs one-hot wave drive; candidate output %.3f..%.3f RPM (calculated), no physical motor test\n",
           slowest_rpm, fastest_rpm);
    return 0;
}
