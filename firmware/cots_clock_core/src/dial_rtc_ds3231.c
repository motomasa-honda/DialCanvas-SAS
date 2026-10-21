#include "dial_rtc_ds3231.h"

#include <stddef.h>

#define DS3231_STATUS_OSF 0x80U
#define UNIX_SECONDS_AT_2000_01_01 INT64_C(946684800)
#define UNIX_SECONDS_AT_2100_01_01 INT64_C(4102444800)

static bool decode_bcd(uint8_t raw, uint8_t mask, uint8_t maximum,
                       uint8_t *value_out)
{
    const uint8_t masked_value = raw & mask;
    const uint8_t ones = masked_value & 0x0fU;
    const uint8_t tens = (masked_value >> 4) & 0x0fU;
    if (ones > 9U || tens > 9U) {
        return false;
    }

    const uint8_t value = (uint8_t)(tens * 10U + ones);
    if (value > maximum) {
        return false;
    }
    *value_out = value;
    return true;
}

static uint8_t encode_bcd(uint8_t value)
{
    return (uint8_t)(((value / 10U) << 4) | (value % 10U));
}

static bool is_leap_year(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

static uint8_t days_in_month(int year, uint8_t month)
{
    static const uint8_t month_days[12] = {
        31U, 28U, 31U, 30U, 31U, 30U,
        31U, 31U, 30U, 31U, 30U, 31U,
    };
    if (month == 2U && is_leap_year(year)) {
        return 29U;
    }
    return month_days[month - 1U];
}

/* Days relative to 1970-01-01; valid for Gregorian dates. */
static int64_t days_from_civil(int year, uint8_t month, uint8_t day)
{
    year -= month <= 2U;
    const int era = (year >= 0 ? year : year - 399) / 400;
    const unsigned year_of_era = (unsigned)(year - era * 400);
    const unsigned adjusted_month =
        (unsigned)((int)month + (month > 2U ? -3 : 9));
    const unsigned day_of_year =
        (153U * adjusted_month + 2U) / 5U + (unsigned)day - 1U;
    const unsigned day_of_era = year_of_era * 365U + year_of_era / 4U -
                                year_of_era / 100U + day_of_year;
    return (int64_t)era * INT64_C(146097) + (int64_t)day_of_era - 719468;
}

static void civil_from_days(int64_t days, int *year_out, uint8_t *month_out,
                            uint8_t *day_out)
{
    days += 719468;
    const int64_t era = (days >= 0 ? days : days - 146096) / 146097;
    const unsigned day_of_era =
        (unsigned)(days - era * INT64_C(146097));
    const unsigned year_of_era =
        (day_of_era - day_of_era / 1460U + day_of_era / 36524U -
         day_of_era / 146096U) / 365U;
    int year = (int)year_of_era + (int)(era * 400);
    const unsigned day_of_year =
        day_of_era - (365U * year_of_era + year_of_era / 4U -
                      year_of_era / 100U);
    const unsigned month_prime = (5U * day_of_year + 2U) / 153U;
    const unsigned day =
        day_of_year - (153U * month_prime + 2U) / 5U + 1U;
    const int month = (int)month_prime + (month_prime < 10U ? 3 : -9);
    year += month <= 2;

    *year_out = year;
    *month_out = (uint8_t)month;
    *day_out = (uint8_t)day;
}

bool dial_rtc_ds3231_decode_utc(
    const uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT],
    uint8_t status_register, int64_t *unix_seconds_out)
{
    if (registers == NULL || unix_seconds_out == NULL ||
        (status_register & DS3231_STATUS_OSF) != 0U ||
        (registers[0] & 0x80U) != 0U || (registers[1] & 0x80U) != 0U ||
        (registers[2] & 0x80U) != 0U || (registers[3] & 0xf8U) != 0U ||
        (registers[4] & 0xc0U) != 0U ||
        (registers[5] & 0x60U) != 0U ||
        (registers[5] & 0x80U) != 0U) {
        return false;
    }

    uint8_t second = 0U;
    uint8_t minute = 0U;
    uint8_t hour = 0U;
    uint8_t day = 0U;
    uint8_t month = 0U;
    uint8_t year_2digit = 0U;
    if (!decode_bcd(registers[0], 0x7fU, 59U, &second) ||
        !decode_bcd(registers[1], 0x7fU, 59U, &minute) ||
        !decode_bcd(registers[4], 0x3fU, 31U, &day) ||
        !decode_bcd(registers[5], 0x1fU, 12U, &month) ||
        !decode_bcd(registers[6], 0xffU, 99U, &year_2digit) ||
        registers[3] < 1U || registers[3] > 7U || day < 1U || month < 1U) {
        return false;
    }

    if ((registers[2] & 0x40U) != 0U) {
        uint8_t hour_12 = 0U;
        if (!decode_bcd(registers[2], 0x1fU, 12U, &hour_12) ||
            hour_12 < 1U) {
            return false;
        }
        hour = (uint8_t)(hour_12 % 12U);
        if ((registers[2] & 0x20U) != 0U) {
            hour = (uint8_t)(hour + 12U);
        }
    } else if (!decode_bcd(registers[2], 0x3fU, 23U, &hour)) {
        return false;
    }

    const int year = 2000 + year_2digit;
    if (day > days_in_month(year, month)) {
        return false;
    }

    const int64_t days = days_from_civil(year, month, day);
    const int64_t unix_seconds = days * INT64_C(86400) +
                                 (int64_t)hour * 3600 +
                                 (int64_t)minute * 60 + second;
    if (unix_seconds < UNIX_SECONDS_AT_2000_01_01 ||
        unix_seconds >= UNIX_SECONDS_AT_2100_01_01) {
        return false;
    }

    *unix_seconds_out = unix_seconds;
    return true;
}

bool dial_rtc_ds3231_encode_utc(
    int64_t unix_seconds,
    uint8_t registers_out[DIAL_RTC_DS3231_TIME_REGISTER_COUNT])
{
    if (registers_out == NULL || unix_seconds < UNIX_SECONDS_AT_2000_01_01 ||
        unix_seconds >= UNIX_SECONDS_AT_2100_01_01) {
        return false;
    }

    const int64_t days = unix_seconds / INT64_C(86400);
    const int64_t seconds_in_day = unix_seconds % INT64_C(86400);
    int year = 0;
    uint8_t month = 0U;
    uint8_t day = 0U;
    civil_from_days(days, &year, &month, &day);
    const uint8_t hour = (uint8_t)(seconds_in_day / 3600);
    const uint8_t minute = (uint8_t)((seconds_in_day % 3600) / 60);
    const uint8_t second = (uint8_t)(seconds_in_day % 60);
    const uint8_t weekday =
        (uint8_t)(((days + 4) % 7) + 1); /* DS3231: Sunday=1. */

    const uint8_t encoded[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {
        encode_bcd(second),
        encode_bcd(minute),
        encode_bcd(hour),
        weekday,
        encode_bcd(day),
        encode_bcd(month),
        encode_bcd((uint8_t)(year - 2000)),
    };
    for (size_t i = 0U; i < DIAL_RTC_DS3231_TIME_REGISTER_COUNT; ++i) {
        registers_out[i] = encoded[i];
    }
    return true;
}
