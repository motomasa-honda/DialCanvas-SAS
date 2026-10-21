#ifndef DIAL_RTC_DS3231_H
#define DIAL_RTC_DS3231_H

#include <stdbool.h>
#include <stdint.h>

#define DIAL_RTC_DS3231_TIME_REGISTER_COUNT 7U

/* DS3231 calendar values are stored as UTC to match gettimeofday/SNTP. */
bool dial_rtc_ds3231_decode_utc(
    const uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT],
    uint8_t status_register, int64_t *unix_seconds_out);
bool dial_rtc_ds3231_encode_utc(
    int64_t unix_seconds,
    uint8_t registers_out[DIAL_RTC_DS3231_TIME_REGISTER_COUNT]);

#endif
