#include "dial_motor_timing.h"

#define MICROSECONDS_PER_MINUTE_MILLI_RPM UINT64_C(60000000000)

bool dial_motor_timing_init(dial_motor_timing_t *timing,
                            uint32_t full_steps_per_revolution,
                            uint16_t microstep_divisor,
                            uint16_t rpm_milli) {
  if (timing == 0 || full_steps_per_revolution == 0 ||
      microstep_divisor == 0 || rpm_milli == 0) {
    return false;
  }

  const uint64_t denominator =
      (uint64_t)full_steps_per_revolution * (uint64_t)microstep_divisor *
      (uint64_t)rpm_milli;
  if (denominator == 0 || denominator > MICROSECONDS_PER_MINUTE_MILLI_RPM) {
    return false;
  }

  const uint64_t base_interval =
      MICROSECONDS_PER_MINUTE_MILLI_RPM / denominator;
  if (base_interval == 0 || base_interval > UINT32_MAX) {
    return false;
  }

  const dial_motor_timing_t initialized = {
      .denominator = denominator,
      .period_remainder =
          MICROSECONDS_PER_MINUTE_MILLI_RPM % denominator,
      .remainder_accumulator = 0,
      .base_interval_us = (uint32_t)base_interval,
  };
  *timing = initialized;
  return true;
}

uint32_t dial_motor_timing_next_interval_us(dial_motor_timing_t *timing) {
  if (timing == 0 || timing->denominator == 0 ||
      timing->base_interval_us == 0 ||
      timing->period_remainder >= timing->denominator) {
    return 0;
  }

  uint32_t interval_us = timing->base_interval_us;
  if (timing->period_remainder != 0) {
    const uint64_t until_carry =
        timing->denominator - timing->period_remainder;
    if (timing->remainder_accumulator >= until_carry) {
      timing->remainder_accumulator -= until_carry;
      if (interval_us == UINT32_MAX) {
        return 0;
      }
      ++interval_us;
    } else {
      timing->remainder_accumulator += timing->period_remainder;
    }
  }
  return interval_us;
}
