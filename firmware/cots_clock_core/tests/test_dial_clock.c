#include "dial_clock.h"

#include <assert.h>
#include <math.h>
#include <stdio.h>

static void assert_near(double actual, double expected, double epsilon) {
  assert(fabs(actual - expected) <= epsilon);
}

static double forward_delta(double before, double after) {
  double delta = after - before;
  if (delta < 0.0) {
    delta += 360.0;
  }
  return delta;
}

static void test_midnight_and_noon_are_zero(void) {
  dial_clock_angles_t angles;
  assert(dial_clock_get_angles(0, 0, 0, 0, &angles));
  assert_near(angles.hour, 0.0, 1e-12);
  assert_near(angles.minute, 0.0, 1e-12);
  assert_near(angles.second, 0.0, 1e-12);

  assert(dial_clock_get_angles(12, 0, 0, 0, &angles));
  assert_near(angles.hour, 0.0, 1e-12);
  assert_near(angles.minute, 0.0, 1e-12);
  assert_near(angles.second, 0.0, 1e-12);
}

static void test_fractional_seconds_move_all_hands(void) {
  dial_clock_angles_t angles;
  assert(dial_clock_get_angles(12, 15, 30, 500, &angles));
  assert_near(angles.second, 183.0, 1e-9);
  assert_near(angles.minute, 93.05, 1e-9);
  assert_near(angles.hour, 7.754166666666667, 1e-9);
}

static void test_day_wrap_is_continuous(void) {
  dial_clock_angles_t before;
  dial_clock_angles_t after;
  assert(dial_clock_get_angles(23, 59, 59, 999, &before));
  assert(dial_clock_get_angles(0, 0, 0, 0, &after));

  assert(before.hour < 360.0 && before.minute < 360.0 &&
         before.second < 360.0);
  assert(forward_delta(before.hour, after.hour) < 0.00001);
  assert(forward_delta(before.minute, after.minute) < 0.00011);
  assert(forward_delta(before.second, after.second) < 0.0061);
}

static void test_hour_wrap_is_continuous(void) {
  dial_clock_angles_t before;
  dial_clock_angles_t after;
  assert(dial_clock_get_angles(11, 59, 59, 999, &before));
  assert(dial_clock_get_angles(12, 0, 0, 0, &after));

  assert(forward_delta(before.hour, after.hour) < 0.00001);
  assert(forward_delta(before.minute, after.minute) < 0.00011);
  assert(forward_delta(before.second, after.second) < 0.0061);
}

static void test_invalid_time_does_not_modify_output(void) {
  dial_clock_angles_t angles = {.hour = 1.0, .minute = 2.0, .second = 3.0};

  assert(!dial_clock_get_angles(24, 0, 0, 0, &angles));
  assert(!dial_clock_get_angles(0, 60, 0, 0, &angles));
  assert(!dial_clock_get_angles(0, 0, 60, 0, &angles));
  assert(!dial_clock_get_angles(0, 0, 0, 1000, &angles));
  assert(!dial_clock_get_angles(0, 0, 0, 0, 0));

  assert_near(angles.hour, 1.0, 1e-12);
  assert_near(angles.minute, 2.0, 1e-12);
  assert_near(angles.second, 3.0, 1e-12);
}

int main(void) {
  test_midnight_and_noon_are_zero();
  test_fractional_seconds_move_all_hands();
  test_day_wrap_is_continuous();
  test_hour_wrap_is_continuous();
  test_invalid_time_does_not_modify_output();
  puts("PASS: continuous clock-hand angle core");
  return 0;
}
