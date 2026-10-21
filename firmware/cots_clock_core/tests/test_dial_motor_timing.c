#include "dial_motor_timing.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static void test_one_point_six_rpm_has_exact_average_rate(void) {
  dial_motor_timing_t timing = {0};
  assert(dial_motor_timing_init(&timing, 200, 8, 1600));

  uint64_t elapsed_us = 0;
  uint32_t short_intervals = 0;
  uint32_t long_intervals = 0;
  for (uint32_t pulse = 0; pulse < 2560; ++pulse) {
    const uint32_t interval_us = dial_motor_timing_next_interval_us(&timing);
    assert(interval_us == 23437 || interval_us == 23438);
    elapsed_us += interval_us;
    short_intervals += interval_us == 23437;
    long_intervals += interval_us == 23438;
  }

  assert(elapsed_us == UINT64_C(60000000));
  assert(short_intervals == 1280);
  assert(long_intervals == 1280);
}

static void test_invalid_rates_leave_state_unchanged(void) {
  dial_motor_timing_t timing = {
      .denominator = 7,
      .period_remainder = 3,
      .remainder_accumulator = 2,
      .base_interval_us = 9,
  };

  assert(!dial_motor_timing_init(&timing, 0, 8, 1600));
  assert(!dial_motor_timing_init(&timing, 200, 0, 1600));
  assert(!dial_motor_timing_init(&timing, 200, 8, 0));
  assert(!dial_motor_timing_init(&timing, UINT32_MAX, UINT16_MAX, UINT16_MAX));
  assert(timing.denominator == 7);
  assert(timing.period_remainder == 3);
  assert(timing.remainder_accumulator == 2);
  assert(timing.base_interval_us == 9);
}

static void test_uninitialized_timing_returns_zero(void) {
  dial_motor_timing_t timing = {0};
  assert(dial_motor_timing_next_interval_us(&timing) == 0);
  assert(dial_motor_timing_next_interval_us(0) == 0);
}

int main(void) {
  test_one_point_six_rpm_has_exact_average_rate();
  test_invalid_rates_leave_state_unchanged();
  test_uninitialized_timing_returns_zero();
  puts("PASS: fractional single-stepper timing core");
  return 0;
}
