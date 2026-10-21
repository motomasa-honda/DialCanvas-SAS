#include "dial_clock.h"

bool dial_clock_get_angles(uint8_t hour24, uint8_t minute, uint8_t second,
                           uint16_t millisecond,
                           dial_clock_angles_t *out) {
  if (out == 0 || hour24 >= 24 || minute >= 60 || second >= 60 ||
      millisecond >= 1000) {
    return false;
  }

  const double seconds_with_fraction =
      (double)second + (double)millisecond / 1000.0;
  const double minutes_with_fraction =
      (double)minute + seconds_with_fraction / 60.0;

  dial_clock_angles_t result = {
      .hour = ((double)(hour24 % 12) + minutes_with_fraction / 60.0) * 30.0,
      .minute = minutes_with_fraction * 6.0,
      .second = seconds_with_fraction * 6.0,
  };

  *out = result;
  return true;
}
