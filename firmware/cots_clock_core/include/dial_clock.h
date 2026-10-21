#ifndef DIAL_CLOCK_H
#define DIAL_CLOCK_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
  /* Degrees clockwise from 12 o'clock; each value is in [0, 360). */
  double hour;
  double minute;
  double second;
} dial_clock_angles_t;

/*
 * Calculate continuously swept hand angles from local clock time.
 * Milliseconds carry sub-second motion into all three hands.
 * Returns false for an invalid time or null output; on failure, *out is intact.
 */
bool dial_clock_get_angles(uint8_t hour24, uint8_t minute, uint8_t second,
                           uint16_t millisecond,
                           dial_clock_angles_t *out);

#endif
