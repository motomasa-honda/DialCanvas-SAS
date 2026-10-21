#ifndef DIAL_MOTOR_TIMING_H
#define DIAL_MOTOR_TIMING_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
  uint64_t denominator;
  uint64_t period_remainder;
  uint64_t remainder_accumulator;
  uint32_t base_interval_us;
} dial_motor_timing_t;

/*
 * Prepare evenly distributed STEP intervals for a stepper motor.
 * rpm_milli is in milli-revolutions per minute; 1600 means 1.6 rpm.
 * The timing state is left unchanged if the requested rate is unsupported.
 * This only calculates intervals; it does not configure or drive GPIO pins.
 */
bool dial_motor_timing_init(dial_motor_timing_t *timing,
                            uint32_t full_steps_per_revolution,
                            uint16_t microstep_divisor,
                            uint16_t rpm_milli);

/* Return the next interval in microseconds, or zero for an uninitialized state. */
uint32_t dial_motor_timing_next_interval_us(dial_motor_timing_t *timing);

#endif
