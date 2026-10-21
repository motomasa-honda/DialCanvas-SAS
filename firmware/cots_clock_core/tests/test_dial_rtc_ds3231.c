#include "dial_rtc_ds3231.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static void test_utc_round_trip_and_weekday(void)
{
    const int64_t expected = INT64_C(1709296496); /* 2024-03-01 12:34:56 UTC */
    uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {0};
    assert(dial_rtc_ds3231_encode_utc(expected, registers));
    assert(registers[0] == 0x56U);
    assert(registers[1] == 0x34U);
    assert(registers[2] == 0x12U);
    assert(registers[3] == 6U); /* Friday */
    assert(registers[4] == 0x01U);
    assert(registers[5] == 0x03U);
    assert(registers[6] == 0x24U);

    int64_t decoded = 0;
    assert(dial_rtc_ds3231_decode_utc(registers, 0U, &decoded));
    assert(decoded == expected);
}

static void test_leap_day_and_twelve_hour_mode(void)
{
    const uint8_t leap_day[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {
        0x00U, 0x00U, 0x52U, 5U, 0x29U, 0x02U, 0x24U,
    };
    int64_t decoded = 0;
    assert(dial_rtc_ds3231_decode_utc(leap_day, 0U, &decoded));
    assert(decoded == INT64_C(1709164800)); /* 2024-02-29 00:00:00 UTC */

    const uint8_t pm_noon[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {
        0x00U, 0x00U, 0x72U, 5U, 0x29U, 0x02U, 0x24U,
    };
    assert(dial_rtc_ds3231_decode_utc(pm_noon, 0U, &decoded));
    assert(decoded == INT64_C(1709208000)); /* 2024-02-29 12:00:00 UTC */
}

static void test_invalid_or_unset_data_is_rejected(void)
{
    uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {
        0x00U, 0x00U, 0x00U, 5U, 0x29U, 0x02U, 0x23U,
    };
    int64_t decoded = INT64_C(12345);
    assert(!dial_rtc_ds3231_decode_utc(registers, 0U, &decoded));
    assert(decoded == INT64_C(12345));

    registers[4] = 0x29U;
    registers[6] = 0x24U;
    assert(!dial_rtc_ds3231_decode_utc(registers, 0x80U, &decoded));
    assert(!dial_rtc_ds3231_decode_utc(registers, 0U, NULL));

    registers[0] = 0x6aU;
    assert(!dial_rtc_ds3231_decode_utc(registers, 0U, &decoded));
    registers[0] = 0x00U;
    registers[4] = 0x31U;
    registers[5] = 0x04U;
    assert(!dial_rtc_ds3231_decode_utc(registers, 0U, &decoded));
}

static void test_supported_epoch_range(void)
{
    uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {0};
    int64_t decoded = 0;
    const int64_t first_supported = INT64_C(946684800);
    const int64_t first_unsupported = INT64_C(4102444800);

    assert(dial_rtc_ds3231_encode_utc(INT64_C(946684800), registers));
    assert(registers[4] == 0x01U && registers[5] == 0x01U &&
           registers[6] == 0x00U);

    for (int64_t timestamp = first_supported + 12345;
         timestamp < first_unsupported; timestamp += INT64_C(86400)) {
        assert(dial_rtc_ds3231_encode_utc(timestamp, registers));
        assert(dial_rtc_ds3231_decode_utc(registers, 0U, &decoded));
        assert(decoded == timestamp);
    }

    assert(dial_rtc_ds3231_encode_utc(INT64_C(4102444799), registers));
    assert(dial_rtc_ds3231_decode_utc(registers, 0U, &decoded));
    assert(decoded == INT64_C(4102444799));
    assert(!dial_rtc_ds3231_encode_utc(INT64_C(4102444800), registers));
    assert(!dial_rtc_ds3231_encode_utc(INT64_C(946684799), registers));
    assert(!dial_rtc_ds3231_encode_utc(INT64_C(946684800), NULL));
}

int main(void)
{
    test_utc_round_trip_and_weekday();
    test_leap_day_and_twelve_hour_mode();
    test_invalid_or_unset_data_is_rejected();
    test_supported_epoch_range();
    puts("PASS: DS3231 UTC encode/decode");
    return 0;
}
