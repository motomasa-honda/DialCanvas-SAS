#include <dirent.h>
#include <ctype.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "bsp/esp32_p4_wifi6_touch_lcd_xc.h"
#include "dial_input.h"
#include "dial_clock.h"
#include "dial_rtc_ds3231.h"
#include "dial_motor_timing.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_event.h"
#include "esp_heap_caps.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_netif_sntp.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "jpeg_decoder.h"
#include "lvgl.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "cJSON.h"

#define FACE_WIDTH 800
#define FACE_HEIGHT 800
#define FACE_JPEG_MAX_BYTES (8U * 1024U * 1024U)
#define DIAL_JSON_MAX_BYTES 4096U
#define DIAL_ROOT BSP_SD_MOUNT_POINT "/DialCanvas/faces"
#define MAX_DIALS 32U
#define DIAL_NAME_MAX 32U
#define DIAL_PATH_MAX 192U
#define DIAL_NVS_NAMESPACE "dialcanvas"
#define DIAL_NVS_KEY "selected"
#define ENCODER_SAMPLE_MS 2U
#define ENCODER_DEBOUNCE_MS 20U
#define ENCODER_LONG_PRESS_MS 900U
#define ENCODER_QUEUE_DEPTH 16U
#define CLOCK_VALID_AFTER ((time_t)1704067200) /* 2024-01-01 UTC */
#define DIAL_PI 3.14159265358979323846

static const char *TAG = "dialcanvas_cots";
static const EventBits_t WIFI_CONNECTED_BIT = BIT0;
static const EventBits_t WIFI_RETRY_BIT = BIT1;
static EventGroupHandle_t wifi_events;
static int wifi_retry_count;
static bool sntp_started;

typedef struct {
    uint32_t color;
    double length;
    uint8_t width;
} hand_style_t;

typedef struct {
    double center_x;
    double center_y;
    hand_style_t hour;
    hand_style_t minute;
    hand_style_t second;
} dial_style_t;

typedef struct {
    lv_obj_t *line;
    lv_point_precise_t points[2];
    double length_px;
    uint8_t width;
} hand_view_t;

typedef struct {
    lv_obj_t *screen;
    lv_obj_t *time_status;
    lv_obj_t *dial_status;
    lv_obj_t *hub;
    lv_obj_t *face_image;
    lv_obj_t *fallback_ticks[60];
    lv_timer_t *dial_status_timer;
    lv_image_dsc_t face_image_dsc;
    uint8_t *face_pixels;
    hand_view_t hour;
    hand_view_t minute;
    hand_view_t second;
    double center_x;
    double center_y;
    bool has_face_image;
} clock_view_t;

typedef struct {
    char name[DIAL_NAME_MAX + 1U];
    char folder[DIAL_PATH_MAX];
} dial_entry_t;

typedef enum {
    ENCODER_EVENT_ROTATE,
    ENCODER_EVENT_SHORT_PRESS,
    ENCODER_EVENT_LONG_PRESS,
} encoder_event_type_t;

typedef struct {
    encoder_event_type_t type;
    int8_t direction;
} encoder_event_t;

static dial_entry_t dial_catalog[MAX_DIALS];
static size_t dial_count;
static uint16_t preview_index;
static uint16_t selected_index;
static bool preview_has_valid_image;
static bool nvs_ready;
static QueueHandle_t encoder_events;
static QueueHandle_t rtc_sync_queue;
static i2c_master_bus_handle_t rtc_i2c_bus;
static i2c_master_dev_handle_t rtc_i2c_device;
static bool rtc_ready;
static clock_view_t clock_view;
static lv_point_precise_t fallback_tick_points[60][2];

static const dial_style_t default_style = {
    .center_x = 0.5,
    .center_y = 0.5,
    .hour = {.color = 0xe9c27f, .length = 0.27, .width = 8},
    .minute = {.color = 0xf4e7c9, .length = 0.37, .width = 5},
    .second = {.color = 0xef7547, .length = 0.42, .width = 2},
};

#if CONFIG_DIALCANVAS_MOTOR_OUTPUT
#define MOTOR_FULL_STEPS_PER_REV 200U
#define MOTOR_MICROSTEP_DIVISOR 8U
#define MOTOR_OUTPUT_MILLI_RPM 1600U
#define MOTOR_STEP_HIGH_US 10U

static gpio_num_t motor_step_gpio = CONFIG_DIALCANVAS_MOTOR_STEP_GPIO;
static gpio_num_t motor_dir_gpio = CONFIG_DIALCANVAS_MOTOR_DIR_GPIO;
static gpio_num_t motor_enn_gpio = CONFIG_DIALCANVAS_MOTOR_ENN_GPIO;
static esp_timer_handle_t motor_step_timer;
static esp_timer_handle_t motor_pulse_timer;
static dial_motor_timing_t motor_timing;
static atomic_bool motor_running;
static bool motor_output_ready;

static void motor_step_timer_callback(void *arg);
static void motor_pulse_timer_callback(void *arg);

static void motor_fail_safe_from_timer(void)
{
    atomic_store(&motor_running, false);
    (void)gpio_set_level(motor_enn_gpio, 1);
    (void)gpio_set_level(motor_step_gpio, 0);
}

static void motor_disable_output(void)
{
    atomic_store(&motor_running, false);
    /* Disable the driver before stopping timers and clearing STEP. */
    (void)gpio_set_level(motor_enn_gpio, 1);
    if (motor_step_timer != NULL) {
        (void)esp_timer_stop(motor_step_timer);
    }
    if (motor_pulse_timer != NULL) {
        (void)esp_timer_stop(motor_pulse_timer);
    }
    (void)gpio_set_level(motor_step_gpio, 0);
}

static void motor_step_timer_callback(void *arg)
{
    (void)arg;
    if (!atomic_load(&motor_running)) {
        return;
    }

    if (gpio_set_level(motor_step_gpio, 1) != ESP_OK ||
        esp_timer_start_once(motor_pulse_timer, MOTOR_STEP_HIGH_US) != ESP_OK) {
        ESP_LOGE(TAG, "Motor STEP pulse setup failed; disabling ENN");
        motor_fail_safe_from_timer();
        return;
    }

    uint32_t interval_us = dial_motor_timing_next_interval_us(&motor_timing);
    if (interval_us <= MOTOR_STEP_HIGH_US ||
        esp_timer_start_once(motor_step_timer, interval_us) != ESP_OK) {
        ESP_LOGE(TAG, "Motor STEP schedule failed; disabling ENN");
        motor_fail_safe_from_timer();
    }
}

static void motor_pulse_timer_callback(void *arg)
{
    (void)arg;
    (void)gpio_set_level(motor_step_gpio, 0);
}

static bool motor_output_init(void)
{
    const gpio_num_t pins[] = {motor_step_gpio, motor_dir_gpio, motor_enn_gpio};
    for (size_t i = 0; i < sizeof(pins) / sizeof(pins[0]); ++i) {
        if (!GPIO_IS_VALID_GPIO(pins[i])) {
            ESP_LOGE(TAG, "Motor GPIO assignment invalid; output remains disabled");
            return false;
        }
        for (size_t j = i + 1U; j < sizeof(pins) / sizeof(pins[0]); ++j) {
            if (pins[i] == pins[j]) {
                ESP_LOGE(TAG, "Motor GPIO pins overlap; output remains disabled");
                return false;
            }
        }
    }
    if (motor_step_gpio == CONFIG_DIALCANVAS_ENCODER_A_GPIO ||
        motor_step_gpio == CONFIG_DIALCANVAS_ENCODER_B_GPIO ||
        motor_step_gpio == CONFIG_DIALCANVAS_ENCODER_SW_GPIO ||
        motor_dir_gpio == CONFIG_DIALCANVAS_ENCODER_A_GPIO ||
        motor_dir_gpio == CONFIG_DIALCANVAS_ENCODER_B_GPIO ||
        motor_dir_gpio == CONFIG_DIALCANVAS_ENCODER_SW_GPIO ||
        motor_enn_gpio == CONFIG_DIALCANVAS_ENCODER_A_GPIO ||
        motor_enn_gpio == CONFIG_DIALCANVAS_ENCODER_B_GPIO ||
        motor_enn_gpio == CONFIG_DIALCANVAS_ENCODER_SW_GPIO ||
        motor_step_gpio == GPIO_NUM_28 || motor_step_gpio == GPIO_NUM_29 ||
        motor_dir_gpio == GPIO_NUM_28 || motor_dir_gpio == GPIO_NUM_29 ||
        motor_enn_gpio == GPIO_NUM_28 || motor_enn_gpio == GPIO_NUM_29) {
        ESP_LOGE(TAG, "Motor GPIO overlaps encoder/RTC candidate; output remains disabled");
        return false;
    }

    const gpio_config_t output_config = {
        .pin_bit_mask = (1ULL << motor_step_gpio) |
                        (1ULL << motor_dir_gpio) |
                        (1ULL << motor_enn_gpio),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    if (gpio_config(&output_config) != ESP_OK) {
        ESP_LOGE(TAG, "Motor GPIO configuration failed; output remains disabled");
        return false;
    }
    if (gpio_set_level(motor_enn_gpio, 1) != ESP_OK ||
        gpio_set_level(motor_step_gpio, 0) != ESP_OK ||
        gpio_set_level(motor_dir_gpio, 0) != ESP_OK) {
        ESP_LOGE(TAG, "Motor GPIO initialization failed; output remains disabled");
        return false;
    }

    if (!dial_motor_timing_init(&motor_timing, MOTOR_FULL_STEPS_PER_REV,
                                MOTOR_MICROSTEP_DIVISOR,
                                MOTOR_OUTPUT_MILLI_RPM)) {
        ESP_LOGE(TAG, "Motor timing initialization failed");
        (void)gpio_set_level(motor_enn_gpio, 1);
        return false;
    }

    const esp_timer_create_args_t step_timer_args = {
        .callback = motor_step_timer_callback,
        .name = "gear_step",
    };
    const esp_timer_create_args_t pulse_timer_args = {
        .callback = motor_pulse_timer_callback,
        .name = "gear_pulse",
    };
    if (esp_timer_create(&step_timer_args, &motor_step_timer) != ESP_OK ||
        esp_timer_create(&pulse_timer_args, &motor_pulse_timer) != ESP_OK) {
        ESP_LOGE(TAG, "Motor timer initialization failed; output remains disabled");
        if (motor_pulse_timer != NULL) {
            (void)esp_timer_delete(motor_pulse_timer);
            motor_pulse_timer = NULL;
        }
        if (motor_step_timer != NULL) {
            (void)esp_timer_delete(motor_step_timer);
            motor_step_timer = NULL;
        }
        (void)gpio_set_level(motor_enn_gpio, 1);
        return false;
    }

    motor_output_ready = true;
    ESP_LOGW(TAG, "Experimental motor GPIO enabled in build; outputs start disabled");
    return true;
}

static bool motor_start(void)
{
    if (!motor_output_ready || atomic_load(&motor_running)) {
        return false;
    }
    if (!dial_motor_timing_init(&motor_timing, MOTOR_FULL_STEPS_PER_REV,
                                MOTOR_MICROSTEP_DIVISOR,
                                MOTOR_OUTPUT_MILLI_RPM) ||
        gpio_set_level(motor_step_gpio, 0) != ESP_OK ||
        gpio_set_level(motor_dir_gpio, 0) != ESP_OK) {
        (void)gpio_set_level(motor_enn_gpio, 1);
        return false;
    }
    uint32_t first_interval_us =
        dial_motor_timing_next_interval_us(&motor_timing);
    if (first_interval_us == 0U) {
        return false;
    }
    if (gpio_set_level(motor_enn_gpio, 0) != ESP_OK) {
        (void)gpio_set_level(motor_enn_gpio, 1);
        return false;
    }
    atomic_store(&motor_running, true);
    if (esp_timer_start_once(motor_step_timer, first_interval_us) != ESP_OK) {
        motor_disable_output();
        return false;
    }
    return true;
}

static const char *motor_toggle_from_user(void)
{
    if (!motor_output_ready) {
        return "Motor output unavailable";
    }
    if (atomic_load(&motor_running)) {
        motor_disable_output();
        return "Gear motor stopped";
    }
    return motor_start() ? "Gear motor started" : "Motor start failed";
}
#else
static bool motor_output_init(void)
{
    ESP_LOGI(TAG, "Motor GPIO output is disabled by build configuration");
    return true;
}

static const char *motor_toggle_from_user(void)
{
    return "Motor GPIO disabled in this build";
}
#endif

static esp_err_t rtc_read_registers(uint8_t first_register, uint8_t *data,
                                    size_t data_length)
{
    if (!rtc_ready || data == NULL || data_length == 0U) {
        return ESP_ERR_INVALID_STATE;
    }
    return i2c_master_transmit_receive(rtc_i2c_device, &first_register,
                                       sizeof(first_register), data,
                                       data_length, 100);
}

static bool rtc_init(void)
{
    const i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_NUM_1,
        .sda_io_num = GPIO_NUM_28,
        .scl_io_num = GPIO_NUM_29,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .intr_priority = 0,
        .trans_queue_depth = 0,
        .flags = {.enable_internal_pullup = true},
    };
    esp_err_t result = i2c_new_master_bus(&bus_config, &rtc_i2c_bus);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "External RTC I2C bus unavailable: %s",
                 esp_err_to_name(result));
        return false;
    }

    const i2c_device_config_t device_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = 0x68,
        .scl_speed_hz = 100000,
    };
    result = i2c_master_bus_add_device(rtc_i2c_bus, &device_config,
                                       &rtc_i2c_device);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "External DS3231 not detected on GPIO28/29: %s",
                 esp_err_to_name(result));
        (void)i2c_del_master_bus(rtc_i2c_bus);
        rtc_i2c_bus = NULL;
        return false;
    }

    rtc_ready = true;
    ESP_LOGI(TAG, "External DS3231 bus ready on GPIO28/29 at 100 kHz");
    return true;
}

static bool rtc_restore_system_time(void)
{
    uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {0};
    uint8_t status_register = 0U;
    const uint8_t status_address = 0x0fU;
    esp_err_t result = rtc_read_registers(0x00U, registers, sizeof(registers));
    if (result == ESP_OK) {
        result = rtc_read_registers(status_address, &status_register,
                                    sizeof(status_register));
    }
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Could not read external RTC: %s", esp_err_to_name(result));
        return false;
    }

    int64_t unix_seconds = 0;
    if (!dial_rtc_ds3231_decode_utc(registers, status_register, &unix_seconds)) {
        ESP_LOGW(TAG, "External RTC is unset or contains invalid calendar data");
        return false;
    }

    const struct timeval rtc_time = {
        .tv_sec = (time_t)unix_seconds,
        .tv_usec = 0,
    };
    if (settimeofday(&rtc_time, NULL) != 0) {
        ESP_LOGW(TAG, "Could not restore system time from external RTC");
        return false;
    }
    ESP_LOGI(TAG, "System time restored from external DS3231");
    return true;
}

static bool rtc_write_utc(int64_t unix_seconds)
{
    uint8_t registers[DIAL_RTC_DS3231_TIME_REGISTER_COUNT] = {0};
    if (!rtc_ready || !dial_rtc_ds3231_encode_utc(unix_seconds, registers)) {
        return false;
    }

    uint8_t write_buffer[DIAL_RTC_DS3231_TIME_REGISTER_COUNT + 1U] = {0};
    write_buffer[0] = 0x00U;
    memcpy(&write_buffer[1], registers, sizeof(registers));
    esp_err_t result = i2c_master_transmit(rtc_i2c_device, write_buffer,
                                           sizeof(write_buffer), 100);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Could not write external RTC time: %s",
                 esp_err_to_name(result));
        return false;
    }

    uint8_t status_register = 0U;
    result = rtc_read_registers(0x0fU, &status_register, sizeof(status_register));
    if (result == ESP_OK && (status_register & 0x80U) != 0U) {
        const uint8_t clear_oscillator_stop[2] = {
            0x0fU, (uint8_t)(status_register & (uint8_t)~0x80U),
        };
        result = i2c_master_transmit(rtc_i2c_device, clear_oscillator_stop,
                                     sizeof(clear_oscillator_stop), 100);
    }
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "RTC time written but status update failed: %s",
                 esp_err_to_name(result));
        return false;
    }
    ESP_LOGI(TAG, "External DS3231 updated from SNTP");
    return true;
}

static void rtc_sync_worker_task(void *arg)
{
    (void)arg;
    int64_t unix_seconds = 0;
    for (;;) {
        if (xQueueReceive(rtc_sync_queue, &unix_seconds, portMAX_DELAY) == pdTRUE) {
            (void)rtc_write_utc(unix_seconds);
        }
    }
}

static void rtc_sntp_sync_callback(struct timeval *time_value)
{
    if (time_value == NULL || rtc_sync_queue == NULL) {
        return;
    }
    const int64_t unix_seconds = (int64_t)time_value->tv_sec;
    (void)xQueueOverwrite(rtc_sync_queue, &unix_seconds);
}

static void start_rtc_sync_worker(void)
{
    if (!rtc_ready) {
        return;
    }
    rtc_sync_queue = xQueueCreate(1U, sizeof(int64_t));
    if (rtc_sync_queue == NULL ||
        xTaskCreate(rtc_sync_worker_task, "rtc_sync", 3072, NULL, 4, NULL) != pdPASS) {
        if (rtc_sync_queue != NULL) {
            vQueueDelete(rtc_sync_queue);
            rtc_sync_queue = NULL;
        }
        ESP_LOGW(TAG, "Could not create RTC update worker; SNTP still available");
    }
}

static bool json_object_has_only(const cJSON *object,
                                 const char *const *allowed,
                                 size_t allowed_count)
{
    if (!cJSON_IsObject(object)) {
        return false;
    }

    for (const cJSON *item = object->child; item != NULL; item = item->next) {
        bool found = false;
        for (size_t i = 0; i < allowed_count; ++i) {
            if (item->string != NULL && strcmp(item->string, allowed[i]) == 0) {
                found = true;
                break;
            }
        }
        if (!found) {
            return false;
        }
    }
    return true;
}

static bool json_read_number(const cJSON *object, const char *key,
                             double minimum, double maximum, double *out)
{
    const cJSON *item = cJSON_GetObjectItemCaseSensitive(object, key);
    if (item == NULL) {
        return true;
    }
    if (!cJSON_IsNumber(item) || !isfinite(item->valuedouble) ||
        item->valuedouble < minimum ||
        item->valuedouble > maximum) {
        return false;
    }
    *out = item->valuedouble;
    return true;
}

static bool json_read_color(const cJSON *object, const char *key, uint32_t *out)
{
    const cJSON *item = cJSON_GetObjectItemCaseSensitive(object, key);
    if (item == NULL) {
        return true;
    }
    if (!cJSON_IsString(item) || item->valuestring == NULL ||
        strlen(item->valuestring) != 7 || item->valuestring[0] != '#') {
        return false;
    }

    for (size_t i = 1; i < 7; ++i) {
        if (!isxdigit((unsigned char)item->valuestring[i])) {
            return false;
        }
    }
    *out = (uint32_t)strtoul(item->valuestring + 1, NULL, 16);
    return true;
}

static bool json_read_hand(const cJSON *hands, const char *name,
                           hand_style_t *style)
{
    static const char *const hand_keys[] = {"color", "length", "width"};
    const cJSON *hand = cJSON_GetObjectItemCaseSensitive(hands, name);
    if (hand == NULL) {
        return true;
    }
    if (!json_object_has_only(hand, hand_keys,
                              sizeof(hand_keys) / sizeof(hand_keys[0]))) {
        return false;
    }

    if (cJSON_GetObjectItemCaseSensitive(hand, "color") == NULL ||
        cJSON_GetObjectItemCaseSensitive(hand, "length") == NULL ||
        cJSON_GetObjectItemCaseSensitive(hand, "width") == NULL) {
        return false;
    }

    const cJSON *width = cJSON_GetObjectItemCaseSensitive(hand, "width");
    double parsed_width = style->width;
    if (width != NULL) {
        if (!cJSON_IsNumber(width) || !isfinite(width->valuedouble) ||
            width->valuedouble < 1.0 ||
            width->valuedouble > 32.0 || floor(width->valuedouble) != width->valuedouble) {
            return false;
        }
        parsed_width = width->valuedouble;
    }

    if (!json_read_color(hand, "color", &style->color) ||
        !json_read_number(hand, "length", 0.0, 0.5, &style->length)) {
        return false;
    }
    style->width = (uint8_t)parsed_width;
    return true;
}

static bool load_dial_style(const char *json_path, dial_style_t *style)
{
    *style = default_style;
    FILE *file = fopen(json_path, "rb");
    if (file == NULL) {
        ESP_LOGI(TAG, "No dial.json; using built-in hand defaults");
        return false;
    }

    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return false;
    }
    long file_size = ftell(file);
    if (file_size <= 0 || file_size > (long)DIAL_JSON_MAX_BYTES ||
        fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return false;
    }

    char *json_text = malloc((size_t)file_size + 1U);
    if (json_text == NULL) {
        fclose(file);
        return false;
    }
    size_t bytes_read = fread(json_text, 1, (size_t)file_size, file);
    fclose(file);
    if (bytes_read != (size_t)file_size) {
        free(json_text);
        return false;
    }
    json_text[file_size] = '\0';

    cJSON *root = cJSON_ParseWithLength(json_text, (size_t)file_size);
    free(json_text);
    if (root == NULL) {
        ESP_LOGW(TAG, "dial.json parse failed; using built-in defaults");
        return false;
    }

    static const char *const root_keys[] = {"version", "name", "center", "hands"};
    static const char *const center_keys[] = {"x", "y"};
    static const char *const hands_keys[] = {"hour", "minute", "second"};
    bool valid = json_object_has_only(root, root_keys,
                                      sizeof(root_keys) / sizeof(root_keys[0]));
    const cJSON *version = cJSON_GetObjectItemCaseSensitive(root, "version");
    valid = valid && cJSON_IsNumber(version) && version->valuedouble == 1.0;

    const cJSON *name = cJSON_GetObjectItemCaseSensitive(root, "name");
    if (valid && name != NULL) {
        valid = cJSON_IsString(name) && name->valuestring != NULL &&
                strlen(name->valuestring) >= 1 && strlen(name->valuestring) <= 32;
    }

    const cJSON *center = cJSON_GetObjectItemCaseSensitive(root, "center");
    if (valid && center != NULL) {
        valid = json_object_has_only(center, center_keys,
                                     sizeof(center_keys) / sizeof(center_keys[0])) &&
                cJSON_GetObjectItemCaseSensitive(center, "x") != NULL &&
                cJSON_GetObjectItemCaseSensitive(center, "y") != NULL &&
                json_read_number(center, "x", 0.0, 1.0, &style->center_x) &&
                json_read_number(center, "y", 0.0, 1.0, &style->center_y);
    }

    const cJSON *hands = cJSON_GetObjectItemCaseSensitive(root, "hands");
    if (valid && hands != NULL) {
        valid = json_object_has_only(hands, hands_keys,
                                     sizeof(hands_keys) / sizeof(hands_keys[0])) &&
                json_read_hand(hands, "hour", &style->hour) &&
                json_read_hand(hands, "minute", &style->minute) &&
                json_read_hand(hands, "second", &style->second);
    }

    cJSON_Delete(root);
    if (!valid) {
        *style = default_style;
        ESP_LOGW(TAG, "dial.json values invalid; using built-in defaults");
    }
    return valid;
}

static uint8_t *read_face_jpeg(const char *jpeg_path, size_t *size_out)
{
    *size_out = 0;
    if (jpeg_path == NULL || jpeg_path[0] == '\0') {
        return NULL;
    }
    FILE *file = fopen(jpeg_path, "rb");
    if (file == NULL || fseek(file, 0, SEEK_END) != 0) {
        if (file != NULL) {
            fclose(file);
        }
        return NULL;
    }

    long file_size = ftell(file);
    if (file_size <= 0 || file_size > (long)FACE_JPEG_MAX_BYTES ||
        fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        ESP_LOGW(TAG, "face.jpg must be nonempty and no larger than 8 MiB");
        return NULL;
    }

    uint8_t *jpeg = heap_caps_malloc((size_t)file_size,
                                     MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (jpeg == NULL) {
        jpeg = heap_caps_malloc((size_t)file_size, MALLOC_CAP_8BIT);
    }
    if (jpeg == NULL) {
        fclose(file);
        ESP_LOGW(TAG, "No memory for face.jpg input");
        return NULL;
    }

    size_t bytes_read = fread(jpeg, 1, (size_t)file_size, file);
    fclose(file);
    if (bytes_read != (size_t)file_size) {
        heap_caps_free(jpeg);
        ESP_LOGW(TAG, "Short read from face.jpg");
        return NULL;
    }
    *size_out = (size_t)file_size;
    return jpeg;
}

static bool decode_face_image(const char *jpeg_path, uint8_t **pixels_out)
{
    *pixels_out = NULL;
    size_t jpeg_size = 0;
    uint8_t *jpeg = read_face_jpeg(jpeg_path, &jpeg_size);
    if (jpeg == NULL) {
        return false;
    }

    esp_jpeg_image_cfg_t jpeg_cfg = {
        .indata = jpeg,
        .indata_size = (uint32_t)jpeg_size,
        .out_format = JPEG_IMAGE_FORMAT_RGB565,
        .out_scale = JPEG_IMAGE_SCALE_0,
        .flags = {.swap_color_bytes = 0},
    };
    esp_jpeg_image_output_t image_info = {0};
    if (esp_jpeg_get_image_info(&jpeg_cfg, &image_info) != ESP_OK ||
        image_info.width != FACE_WIDTH || image_info.height != FACE_HEIGHT ||
        image_info.output_len != FACE_WIDTH * FACE_HEIGHT * sizeof(uint16_t)) {
        ESP_LOGW(TAG, "face.jpg must be baseline 800x800 JPEG");
        heap_caps_free(jpeg);
        return false;
    }

    const size_t pixel_bytes = FACE_WIDTH * FACE_HEIGHT * sizeof(uint16_t);
    uint8_t *pixels = heap_caps_malloc(pixel_bytes,
                                       MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (pixels == NULL) {
        pixels = heap_caps_malloc(pixel_bytes, MALLOC_CAP_8BIT);
    }
    if (pixels == NULL) {
        ESP_LOGW(TAG, "No memory for decoded face image");
        heap_caps_free(jpeg);
        return false;
    }

    jpeg_cfg.outbuf = pixels;
    jpeg_cfg.outbuf_size = (uint32_t)pixel_bytes;
    esp_jpeg_image_output_t decoded = {0};
    esp_err_t decode_result = esp_jpeg_decode(&jpeg_cfg, &decoded);
    heap_caps_free(jpeg);
    if (decode_result != ESP_OK || decoded.width != FACE_WIDTH ||
        decoded.height != FACE_HEIGHT || decoded.output_len != pixel_bytes) {
        ESP_LOGW(TAG, "face.jpg decode failed: %s", esp_err_to_name(decode_result));
        heap_caps_free(pixels);
        return false;
    }
    *pixels_out = pixels;
    return true;
}

static lv_image_dsc_t make_face_image_descriptor(uint8_t *pixels)
{
    const size_t pixel_bytes = FACE_WIDTH * FACE_HEIGHT * sizeof(uint16_t);
    return (lv_image_dsc_t){
        .header = {
            .magic = LV_IMAGE_HEADER_MAGIC,
            .cf = LV_COLOR_FORMAT_RGB565,
            .flags = 0,
            .w = FACE_WIDTH,
            .h = FACE_HEIGHT,
            .stride = FACE_WIDTH * sizeof(uint16_t),
            .reserved_2 = 0,
        },
        .data_size = (uint32_t)pixel_bytes,
        .data = pixels,
        .reserved = NULL,
        .reserved_2 = NULL,
    };
}

static void polar_point(double center_x, double center_y, double radius,
                        double degrees, lv_point_precise_t *point)
{
    const double radians = degrees * (DIAL_PI / 180.0);
    point->x = (lv_value_precise_t)lround(center_x + radius * sin(radians));
    point->y = (lv_value_precise_t)lround(center_y - radius * cos(radians));
}

static lv_obj_t *create_line(lv_obj_t *parent, lv_point_precise_t points[2],
                             uint32_t color, uint8_t width)
{
    lv_obj_t *line = lv_line_create(parent);
    lv_line_set_points_mutable(line, points, 2);
    lv_obj_set_style_line_color(line, lv_color_hex(color), LV_PART_MAIN);
    lv_obj_set_style_line_width(line, width, LV_PART_MAIN);
    lv_obj_set_style_line_rounded(line, true, LV_PART_MAIN);
    return line;
}

static void set_segment_geometry(lv_obj_t *line, lv_point_precise_t points[2],
                                 int32_t x1, int32_t y1, int32_t x2, int32_t y2,
                                 uint8_t line_width)
{
    const int32_t margin = ((int32_t)line_width + 1) / 2 + 2;
    int32_t left = (x1 < x2 ? x1 : x2) - margin;
    int32_t top = (y1 < y2 ? y1 : y2) - margin;
    int32_t right = (x1 > x2 ? x1 : x2) + margin;
    int32_t bottom = (y1 > y2 ? y1 : y2) + margin;
    if (left < 0) left = 0;
    if (top < 0) top = 0;
    if (right >= FACE_WIDTH) right = FACE_WIDTH - 1;
    if (bottom >= FACE_HEIGHT) bottom = FACE_HEIGHT - 1;

    points[0].x = (lv_value_precise_t)(x1 - left);
    points[0].y = (lv_value_precise_t)(y1 - top);
    points[1].x = (lv_value_precise_t)(x2 - left);
    points[1].y = (lv_value_precise_t)(y2 - top);
    lv_obj_set_pos(line, left, top);
    lv_obj_set_size(line, right - left + 1, bottom - top + 1);
    lv_obj_invalidate(line);
}

static void create_fallback_face(clock_view_t *view)
{
    for (size_t i = 0; i < 60; ++i) {
        const double angle = (double)i * 6.0;
        const double inner_radius = (i % 5 == 0) ? 350.0 : 365.0;
        const double outer_radius = 382.0;
        polar_point(view->center_x, view->center_y,
                    inner_radius, angle, &fallback_tick_points[i][0]);
        polar_point(view->center_x, view->center_y,
                    outer_radius, angle, &fallback_tick_points[i][1]);
        view->fallback_ticks[i] = create_line(view->screen,
                                              fallback_tick_points[i],
                                              0xb08b55,
                                              (i % 5 == 0) ? 4 : 2);
        set_segment_geometry(view->fallback_ticks[i], fallback_tick_points[i],
                             (int32_t)fallback_tick_points[i][0].x,
                             (int32_t)fallback_tick_points[i][0].y,
                             (int32_t)fallback_tick_points[i][1].x,
                             (int32_t)fallback_tick_points[i][1].y,
                             (i % 5 == 0) ? 4 : 2);
    }
}

static void update_hand(hand_view_t *hand, double center_x, double center_y,
                        double angle);

static void create_hand(clock_view_t *view, hand_view_t *hand,
                        const hand_style_t *style)
{
    hand->length_px = style->length * FACE_WIDTH;
    hand->width = style->width;
    hand->points[0] = (lv_point_precise_t){0};
    hand->points[1] = (lv_point_precise_t){0};
    hand->line = create_line(view->screen, hand->points, style->color, style->width);
    update_hand(hand, view->center_x, view->center_y, 0.0);
}

static void apply_hand_style(hand_view_t *hand, const hand_style_t *style)
{
    hand->length_px = style->length * FACE_WIDTH;
    hand->width = style->width;
    lv_obj_set_style_line_color(hand->line, lv_color_hex(style->color),
                                LV_PART_MAIN);
    lv_obj_set_style_line_width(hand->line, style->width, LV_PART_MAIN);
}

static void update_hand(hand_view_t *hand, double center_x, double center_y,
                        double angle)
{
    const double radians = angle * (DIAL_PI / 180.0);
    const int32_t x1 = (int32_t)lround(center_x);
    const int32_t y1 = (int32_t)lround(center_y);
    const int32_t x2 = (int32_t)lround(center_x + hand->length_px * sin(radians));
    const int32_t y2 = (int32_t)lround(center_y - hand->length_px * cos(radians));
    set_segment_geometry(hand->line, hand->points, x1, y1, x2, y2, hand->width);
}

static void clock_tick(lv_timer_t *timer)
{
    clock_view_t *view = lv_timer_get_user_data(timer);
    struct timeval now = {0};
    if (gettimeofday(&now, NULL) != 0 || now.tv_sec < CLOCK_VALID_AFTER) {
        lv_label_set_text(view->time_status, "TIME NOT SET");
        lv_obj_clear_flag(view->time_status, LV_OBJ_FLAG_HIDDEN);
        return;
    }

    struct tm local_time = {0};
    if (localtime_r(&now.tv_sec, &local_time) == NULL) {
        lv_label_set_text(view->time_status, "TIME ERROR");
        lv_obj_clear_flag(view->time_status, LV_OBJ_FLAG_HIDDEN);
        return;
    }

    dial_clock_angles_t angles;
    if (!dial_clock_get_angles((uint8_t)local_time.tm_hour,
                               (uint8_t)local_time.tm_min,
                               (uint8_t)local_time.tm_sec,
                               (uint16_t)(now.tv_usec / 1000), &angles)) {
        return;
    }

    update_hand(&view->hour, view->center_x, view->center_y, angles.hour);
    update_hand(&view->minute, view->center_x, view->center_y, angles.minute);
    update_hand(&view->second, view->center_x, view->center_y, angles.second);
    lv_obj_add_flag(view->time_status, LV_OBJ_FLAG_HIDDEN);
}

static void show_dial_status(clock_view_t *view, const char *message)
{
    lv_label_set_text(view->dial_status, message);
    lv_obj_clear_flag(view->dial_status, LV_OBJ_FLAG_HIDDEN);
    if (view->dial_status_timer != NULL) {
        lv_timer_reset(view->dial_status_timer);
        lv_timer_resume(view->dial_status_timer);
    }
}

static void hide_dial_status(lv_timer_t *timer)
{
    clock_view_t *view = lv_timer_get_user_data(timer);
    lv_obj_add_flag(view->dial_status, LV_OBJ_FLAG_HIDDEN);
    lv_timer_pause(timer);
}

static bool set_face_pixels(clock_view_t *view, uint8_t *new_pixels)
{
    if (new_pixels == NULL) {
        return false;
    }
    uint8_t *old_pixels = view->face_pixels;
    view->face_pixels = new_pixels;
    view->face_image_dsc = make_face_image_descriptor(new_pixels);

    if (view->face_image == NULL) {
        view->face_image = lv_image_create(view->screen);
        if (view->face_image == NULL) {
            view->face_pixels = old_pixels;
            if (new_pixels != NULL) {
                heap_caps_free(new_pixels);
            }
            ESP_LOGW(TAG, "LVGL could not create the face image object");
            return false;
        }
        lv_obj_center(view->face_image);
    }

    if (new_pixels == NULL) {
        lv_obj_add_flag(view->face_image, LV_OBJ_FLAG_HIDDEN);
        view->has_face_image = false;
    } else {
        lv_image_set_src(view->face_image, &view->face_image_dsc);
        lv_obj_clear_flag(view->face_image, LV_OBJ_FLAG_HIDDEN);
        lv_obj_invalidate(view->face_image);
        for (size_t i = 0; i < 60U; ++i) {
            if (view->fallback_ticks[i] != NULL) {
                lv_obj_add_flag(view->fallback_ticks[i], LV_OBJ_FLAG_HIDDEN);
            }
        }
        view->has_face_image = true;
    }
    if (old_pixels != NULL) {
        heap_caps_free(old_pixels);
    }
    return view->has_face_image;
}

static void apply_dial_style(clock_view_t *view, const dial_style_t *style)
{
    view->center_x = style->center_x * FACE_WIDTH;
    view->center_y = style->center_y * FACE_HEIGHT;
    apply_hand_style(&view->hour, &style->hour);
    apply_hand_style(&view->minute, &style->minute);
    apply_hand_style(&view->second, &style->second);
    update_hand(&view->hour, view->center_x, view->center_y, 0.0);
    update_hand(&view->minute, view->center_x, view->center_y, 0.0);
    update_hand(&view->second, view->center_x, view->center_y, 0.0);
    lv_obj_set_pos(view->hub, (int32_t)view->center_x - 9,
                   (int32_t)view->center_y - 9);
}

static void create_clock_view(clock_view_t *view, const dial_style_t *style,
                              uint8_t *initial_pixels)
{
    view->screen = lv_screen_active();
    lv_obj_set_style_bg_color(view->screen, lv_color_hex(0x080907), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(view->screen, LV_OPA_COVER, LV_PART_MAIN);
    view->center_x = style->center_x * FACE_WIDTH;
    view->center_y = style->center_y * FACE_HEIGHT;
    if (initial_pixels != NULL) {
        (void)set_face_pixels(view, initial_pixels);
    }
    if (!view->has_face_image) {
        create_fallback_face(view);
    }

    create_hand(view, &view->hour, &style->hour);
    create_hand(view, &view->minute, &style->minute);
    create_hand(view, &view->second, &style->second);

    view->hub = lv_obj_create(view->screen);
    lv_obj_remove_style_all(view->hub);
    lv_obj_set_size(view->hub, 18, 18);
    lv_obj_set_style_radius(view->hub, LV_RADIUS_CIRCLE, LV_PART_MAIN);
    lv_obj_set_style_bg_color(view->hub, lv_color_hex(0xe9c27f), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(view->hub, LV_OPA_COVER, LV_PART_MAIN);
    lv_obj_set_pos(view->hub, (int32_t)view->center_x - 9,
                   (int32_t)view->center_y - 9);

    view->time_status = lv_label_create(view->screen);
    lv_label_set_text(view->time_status, "TIME NOT SET");
    lv_obj_set_style_text_color(view->time_status, lv_color_hex(0xf4e7c9), LV_PART_MAIN);
    lv_obj_set_style_text_font(view->time_status, &lv_font_montserrat_16, LV_PART_MAIN);
    lv_obj_align(view->time_status, LV_ALIGN_BOTTOM_MID, 0, -28);

    view->dial_status = lv_label_create(view->screen);
    lv_obj_set_style_text_color(view->dial_status, lv_color_hex(0xf4e7c9), LV_PART_MAIN);
    lv_obj_set_style_text_font(view->dial_status, &lv_font_montserrat_16, LV_PART_MAIN);
    lv_obj_align(view->dial_status, LV_ALIGN_BOTTOM_MID, 0, -56);
    lv_obj_add_flag(view->dial_status, LV_OBJ_FLAG_HIDDEN);
    view->dial_status_timer = lv_timer_create(hide_dial_status, 2500, view);
    if (view->dial_status_timer != NULL) {
        lv_timer_pause(view->dial_status_timer);
    }

    lv_timer_create(clock_tick, 16, view);
}

static bool wifi_setup_step(esp_err_t result, const char *operation)
{
    if (result == ESP_OK) {
        return true;
    }
    ESP_LOGW(TAG, "Wi-Fi setup stopped at %s: %s", operation,
             esp_err_to_name(result));
    return false;
}

static bool wifi_setup_step_allow_existing(esp_err_t result,
                                           const char *operation)
{
    if (result == ESP_ERR_INVALID_STATE) {
        return true;
    }
    return wifi_setup_step(result, operation);
}

static void start_sntp_after_ip(void)
{
    if (sntp_started) {
        return;
    }
    esp_sntp_config_t config = ESP_NETIF_SNTP_DEFAULT_CONFIG("pool.ntp.org");
    config.smooth_sync = true;
    config.start = true;
    config.sync_cb = rtc_sntp_sync_callback;
    esp_err_t result = esp_netif_sntp_init(&config);
    if (result == ESP_OK) {
        sntp_started = true;
        ESP_LOGI(TAG, "SNTP started after Wi-Fi connection");
    } else {
        ESP_LOGW(TAG, "SNTP startup failed: %s", esp_err_to_name(result));
    }
}

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
    (void)arg;
    (void)event_data;
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        (void)esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (wifi_retry_count < CONFIG_DIALCANVAS_WIFI_RETRY_LIMIT) {
            ++wifi_retry_count;
            (void)esp_wifi_connect();
        } else {
            xEventGroupSetBits(wifi_events, WIFI_RETRY_BIT);
        }
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        wifi_retry_count = 0;
        xEventGroupSetBits(wifi_events, WIFI_CONNECTED_BIT);
    }
}

static bool wifi_start_station(void)
{
    esp_err_t result = esp_netif_init();
    if (!wifi_setup_step_allow_existing(result, "esp_netif_init")) return false;
    result = esp_event_loop_create_default();
    if (!wifi_setup_step_allow_existing(result,
                                        "esp_event_loop_create_default")) return false;
    if (esp_netif_create_default_wifi_sta() == NULL) {
        ESP_LOGW(TAG, "Could not create station network interface");
        return false;
    }

    wifi_init_config_t init_config = WIFI_INIT_CONFIG_DEFAULT();
    result = esp_wifi_init(&init_config);
    if (!wifi_setup_step(result, "esp_wifi_init")) return false;

    esp_event_handler_instance_t wifi_instance;
    esp_event_handler_instance_t ip_instance;
    result = esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                                 wifi_event_handler, NULL,
                                                 &wifi_instance);
    if (!wifi_setup_step(result, "register Wi-Fi event")) return false;
    result = esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP,
                                                 wifi_event_handler, NULL,
                                                 &ip_instance);
    if (!wifi_setup_step(result, "register IP event")) return false;

    const char *ssid = CONFIG_DIALCANVAS_WIFI_SSID;
    const char *password = CONFIG_DIALCANVAS_WIFI_PASSWORD;
    wifi_config_t wifi_config = {0};
    const size_t ssid_length = strlen(ssid);
    const size_t password_length = strlen(password);
    if (ssid_length == 0 || ssid_length >= sizeof(wifi_config.sta.ssid) ||
        password_length >= sizeof(wifi_config.sta.password) ||
        (password_length > 0 && password_length < 8)) {
        ESP_LOGW(TAG, "Wi-Fi SSID/password length is invalid");
        return false;
    }
    memcpy(wifi_config.sta.ssid, ssid, ssid_length + 1);
    memcpy(wifi_config.sta.password, password, password_length + 1);
    wifi_config.sta.threshold.authmode = password_length == 0 ?
                                         WIFI_AUTH_OPEN : WIFI_AUTH_WPA2_PSK;

    result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (!wifi_setup_step(result, "esp_wifi_set_mode")) return false;
    result = esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    if (!wifi_setup_step(result, "esp_wifi_set_config")) return false;
    result = esp_wifi_start();
    if (!wifi_setup_step(result, "esp_wifi_start")) return false;
    return true;
}

static void wifi_time_task(void *arg)
{
    (void)arg;
    wifi_events = xEventGroupCreate();
    if (wifi_events == NULL || !wifi_start_station()) {
        ESP_LOGW(TAG, "Wi-Fi unavailable; clock display continues without sync");
        vTaskDelete(NULL);
        return;
    }

    for (;;) {
        EventBits_t bits = xEventGroupWaitBits(wifi_events,
                                               WIFI_CONNECTED_BIT | WIFI_RETRY_BIT,
                                               pdTRUE, pdFALSE, portMAX_DELAY);
        if ((bits & WIFI_CONNECTED_BIT) != 0) {
            start_sntp_after_ip();
        }
        if ((bits & WIFI_RETRY_BIT) != 0) {
            ESP_LOGI(TAG, "Wi-Fi retry scheduled in 30 seconds");
            vTaskDelay(pdMS_TO_TICKS(30000));
            wifi_retry_count = 0;
            (void)esp_wifi_connect();
        }
    }
}

static void start_wifi_time_task(void)
{
    if (CONFIG_DIALCANVAS_WIFI_SSID[0] == '\0') {
        ESP_LOGI(TAG, "Wi-Fi credentials not configured; set them in menuconfig");
        return;
    }
    if (!nvs_ready) {
        ESP_LOGW(TAG, "NVS unavailable; Wi-Fi time sync is disabled");
        return;
    }
    if (xTaskCreate(wifi_time_task, "clock_wifi", 6144, NULL, 5, NULL) != pdPASS) {
        ESP_LOGW(TAG, "Could not create Wi-Fi time task");
    }
}

static bool valid_dial_name(const char *name)
{
    return dial_name_is_safe(name);
}

static void scan_dials(bool sd_available)
{
    dial_count = 0;
    if (!sd_available) {
        return;
    }

    DIR *directory = opendir(DIAL_ROOT);
    if (directory == NULL) {
        ESP_LOGI(TAG, "No DialCanvas/faces folder on microSD");
        return;
    }

    struct dirent *entry;
    while ((entry = readdir(directory)) != NULL) {
        if (!valid_dial_name(entry->d_name)) {
            continue;
        }

        char folder[DIAL_PATH_MAX];
        char face_path[DIAL_PATH_MAX];
        int folder_length = snprintf(folder, sizeof(folder), "%s/%s",
                                     DIAL_ROOT, entry->d_name);
        int face_length = snprintf(face_path, sizeof(face_path), "%s/face.jpg",
                                   folder);
        if (folder_length <= 0 || (size_t)folder_length >= sizeof(folder) ||
            face_length <= 0 || (size_t)face_length >= sizeof(face_path)) {
            continue;
        }

        struct stat folder_stat;
        struct stat face_stat;
        if (stat(folder, &folder_stat) != 0 || !S_ISDIR(folder_stat.st_mode) ||
            stat(face_path, &face_stat) != 0 || !S_ISREG(face_stat.st_mode) ||
            face_stat.st_size <= 0 || face_stat.st_size > FACE_JPEG_MAX_BYTES) {
            continue;
        }

        dial_entry_t candidate = {0};
        memcpy(candidate.name, entry->d_name, strlen(entry->d_name) + 1U);
        memcpy(candidate.folder, folder, (size_t)folder_length + 1U);

        const char *existing_names[MAX_DIALS];
        for (size_t i = 0; i < dial_count; ++i) {
            existing_names[i] = dial_catalog[i].name;
        }
        size_t insert_at = dial_catalog_insertion_index(
            existing_names, dial_count, MAX_DIALS, candidate.name);
        if (insert_at == SIZE_MAX) {
            continue;
        }

        size_t new_count = dial_count;
        if (new_count < MAX_DIALS) {
            ++new_count;
        }
        for (size_t i = new_count - 1U; i > insert_at; --i) {
            dial_catalog[i] = dial_catalog[i - 1U];
        }
        dial_catalog[insert_at] = candidate;
        dial_count = new_count;
    }
    closedir(directory);
    ESP_LOGI(TAG, "Found %u candidate dial(s) on microSD", (unsigned)dial_count);
}

static int find_dial_index(const char *name)
{
    if (name == NULL || name[0] == '\0') {
        return -1;
    }
    for (size_t i = 0; i < dial_count; ++i) {
        if (strcmp(dial_catalog[i].name, name) == 0) {
            return (int)i;
        }
    }
    return -1;
}

static bool read_selected_dial_name(char name[DIAL_NAME_MAX + 1U])
{
    if (!nvs_ready) {
        return false;
    }
    nvs_handle_t handle;
    if (nvs_open(DIAL_NVS_NAMESPACE, NVS_READONLY, &handle) != ESP_OK) {
        return false;
    }
    size_t length = DIAL_NAME_MAX + 1U;
    esp_err_t result = nvs_get_str(handle, DIAL_NVS_KEY, name, &length);
    nvs_close(handle);
    if (result != ESP_OK || length == 0U || length > DIAL_NAME_MAX + 1U) {
        return false;
    }
    return valid_dial_name(name);
}

static bool save_selected_dial_name(const char *name)
{
    if (!nvs_ready) {
        return false;
    }
    nvs_handle_t handle;
    esp_err_t result = nvs_open(DIAL_NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Could not open NVS for dial selection: %s",
                 esp_err_to_name(result));
        return false;
    }
    result = nvs_set_str(handle, DIAL_NVS_KEY, name);
    if (result == ESP_OK) {
        result = nvs_commit(handle);
    }
    nvs_close(handle);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Could not save dial selection: %s", esp_err_to_name(result));
        return false;
    }
    return true;
}

static bool load_dial_paths(uint16_t index, char face_path[DIAL_PATH_MAX],
                            char json_path[DIAL_PATH_MAX])
{
    if (index >= dial_count) {
        return false;
    }
    int face_length = snprintf(face_path, DIAL_PATH_MAX, "%s/face.jpg",
                               dial_catalog[index].folder);
    int json_length = snprintf(json_path, DIAL_PATH_MAX, "%s/dial.json",
                               dial_catalog[index].folder);
    return face_length > 0 && face_length < DIAL_PATH_MAX &&
           json_length > 0 && json_length < DIAL_PATH_MAX;
}

static bool try_initial_dial(uint16_t index, uint8_t **pixels_out,
                             dial_style_t *style_out)
{
    char face_path[DIAL_PATH_MAX];
    char json_path[DIAL_PATH_MAX];
    if (!load_dial_paths(index, face_path, json_path) ||
        !decode_face_image(face_path, pixels_out)) {
        ESP_LOGW(TAG, "Initial dial is unreadable: %s", dial_catalog[index].name);
        return false;
    }
    (void)load_dial_style(json_path, style_out);
    return true;
}

static uint16_t choose_initial_dial(uint8_t **pixels_out, dial_style_t *style_out)
{
    *pixels_out = NULL;
    *style_out = default_style;
    if (dial_count == 0U) {
        return 0;
    }

    bool attempted[MAX_DIALS] = {false};
    char saved_name[DIAL_NAME_MAX + 1U] = {0};
    int saved_index = read_selected_dial_name(saved_name) ?
                      find_dial_index(saved_name) : -1;
    int forest_index = find_dial_index("Forest");
    int priority[2] = {saved_index, forest_index};
    for (size_t i = 0; i < 2U; ++i) {
        int index = priority[i];
        if (index >= 0 && !attempted[index]) {
            attempted[index] = true;
            if (try_initial_dial((uint16_t)index, pixels_out, style_out)) {
                return (uint16_t)index;
            }
        }
    }
    for (size_t i = 0; i < dial_count; ++i) {
        if (!attempted[i] &&
            try_initial_dial((uint16_t)i, pixels_out, style_out)) {
            return (uint16_t)i;
        }
    }
    return 0;
}

static void preview_dial(uint16_t requested_index, int8_t direction)
{
    if (dial_count == 0U) {
        return;
    }

    uint16_t candidate = requested_index;
    for (size_t attempts = 0; attempts < dial_count; ++attempts) {
        char face_path[DIAL_PATH_MAX];
        char json_path[DIAL_PATH_MAX];
        uint8_t *pixels = NULL;
        if (load_dial_paths(candidate, face_path, json_path) &&
            decode_face_image(face_path, &pixels)) {
            dial_style_t style;
            (void)load_dial_style(json_path, &style);
            ESP_ERROR_CHECK(bsp_display_lock(portMAX_DELAY));
            if (!set_face_pixels(&clock_view, pixels)) {
                show_dial_status(&clock_view, "Could not create dial image");
                bsp_display_unlock();
                return;
            }
            apply_dial_style(&clock_view, &style);
            preview_index = candidate;
            preview_has_valid_image = true;
            char message[80];
            (void)snprintf(message, sizeof(message), "Preview: %s  |  press to select",
                           dial_catalog[candidate].name);
            show_dial_status(&clock_view, message);
            bsp_display_unlock();
            return;
        }

        ESP_LOGW(TAG, "Skipping unreadable dial: %s", dial_catalog[candidate].name);
        candidate = dial_index_step(candidate, (uint16_t)dial_count, direction);
    }

    ESP_ERROR_CHECK(bsp_display_lock(portMAX_DELAY));
    show_dial_status(&clock_view, "No readable face.jpg found");
    bsp_display_unlock();
}

static void handle_encoder_event(const encoder_event_t *event)
{
    if (event->type == ENCODER_EVENT_ROTATE) {
        if (dial_count == 0U) {
            return;
        }
        uint16_t next = dial_index_step(preview_index, (uint16_t)dial_count,
                                        event->direction);
        preview_dial(next, event->direction);
        return;
    }

    ESP_ERROR_CHECK(bsp_display_lock(portMAX_DELAY));
    if (event->type == ENCODER_EVENT_SHORT_PRESS && dial_count > 0U) {
        if (!preview_has_valid_image) {
            show_dial_status(&clock_view, "No readable face to select");
            bsp_display_unlock();
            return;
        }
        selected_index = preview_index;
        bool saved = save_selected_dial_name(dial_catalog[selected_index].name);
        char message[80];
        (void)snprintf(message, sizeof(message), saved ? "Selected: %s" :
                       "Selected for this session: %s",
                       dial_catalog[selected_index].name);
        show_dial_status(&clock_view, message);
        ESP_LOGI(TAG, "Selected dial %s (saved=%s)",
                 dial_catalog[selected_index].name, saved ? "yes" : "no");
    } else if (event->type == ENCODER_EVENT_LONG_PRESS) {
        const char *motor_status = motor_toggle_from_user();
        show_dial_status(&clock_view, motor_status);
        ESP_LOGI(TAG, "Encoder long press: %s", motor_status);
    }
    bsp_display_unlock();
}

static void encoder_action_task(void *arg)
{
    (void)arg;
    encoder_event_t event;
    for (;;) {
        if (xQueueReceive(encoder_events, &event, portMAX_DELAY) == pdTRUE) {
            handle_encoder_event(&event);
        }
    }
}

static bool start_encoder_tasks(void)
{
    const gpio_num_t pin_a = CONFIG_DIALCANVAS_ENCODER_A_GPIO;
    const gpio_num_t pin_b = CONFIG_DIALCANVAS_ENCODER_B_GPIO;
    const gpio_num_t pin_sw = CONFIG_DIALCANVAS_ENCODER_SW_GPIO;
    if (!GPIO_IS_VALID_GPIO(pin_a) || !GPIO_IS_VALID_GPIO(pin_b) ||
        !GPIO_IS_VALID_GPIO(pin_sw) || pin_a == pin_b || pin_a == pin_sw ||
        pin_b == pin_sw) {
        ESP_LOGE(TAG, "Encoder GPIO assignment invalid; encoder disabled");
        return false;
    }

    gpio_config_t input_config = {
        .pin_bit_mask = (1ULL << pin_a) | (1ULL << pin_b) | (1ULL << pin_sw),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t result = gpio_config(&input_config);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Encoder GPIO setup failed: %s", esp_err_to_name(result));
        return false;
    }

    encoder_events = xQueueCreate(ENCODER_QUEUE_DEPTH, sizeof(encoder_event_t));
    if (encoder_events == NULL) {
        ESP_LOGE(TAG, "Could not create encoder event queue");
        return false;
    }
    if (xTaskCreate(encoder_action_task, "dial_actions", 6144, NULL, 5, NULL) != pdPASS) {
        vQueueDelete(encoder_events);
        encoder_events = NULL;
        ESP_LOGE(TAG, "Could not create encoder action task");
        return false;
    }

    ESP_LOGI(TAG, "Encoder inputs configured on GPIO %d/%d/%d",
             (int)pin_a, (int)pin_b, (int)pin_sw);
    return true;
}

static void encoder_poll_task(void *arg)
{
    (void)arg;
    const gpio_num_t pin_a = CONFIG_DIALCANVAS_ENCODER_A_GPIO;
    const gpio_num_t pin_b = CONFIG_DIALCANVAS_ENCODER_B_GPIO;
    const gpio_num_t pin_sw = CONFIG_DIALCANVAS_ENCODER_SW_GPIO;
    uint8_t previous_state = (uint8_t)((gpio_get_level(pin_a) << 1) |
                                       gpio_get_level(pin_b));
    int8_t transition_accumulator = 0;
    bool stable_pressed = false;
    bool previous_raw_pressed = false;
    int64_t raw_change_us = esp_timer_get_time();
    int64_t press_start_us = 0;
    bool long_press_sent = false;

    for (;;) {
        uint8_t current_state = (uint8_t)((gpio_get_level(pin_a) << 1) |
                                          gpio_get_level(pin_b));
        transition_accumulator += dial_encoder_transition(previous_state,
                                                           current_state);
        previous_state = current_state;
        if (transition_accumulator >= 4) {
            encoder_event_t event = {.type = ENCODER_EVENT_ROTATE, .direction = 1};
            (void)xQueueSend(encoder_events, &event, 0);
            transition_accumulator = 0;
        } else if (transition_accumulator <= -4) {
            encoder_event_t event = {.type = ENCODER_EVENT_ROTATE, .direction = -1};
            (void)xQueueSend(encoder_events, &event, 0);
            transition_accumulator = 0;
        }

        int64_t now_us = esp_timer_get_time();
        bool raw_pressed = gpio_get_level(pin_sw) == 0;
        if (raw_pressed != previous_raw_pressed) {
            previous_raw_pressed = raw_pressed;
            raw_change_us = now_us;
        }
        if (raw_pressed != stable_pressed &&
            now_us - raw_change_us >= (int64_t)ENCODER_DEBOUNCE_MS * 1000) {
            stable_pressed = raw_pressed;
            if (stable_pressed) {
                press_start_us = now_us;
                long_press_sent = false;
            } else if (!long_press_sent) {
                encoder_event_t event = {
                    .type = ENCODER_EVENT_SHORT_PRESS,
                    .direction = 0,
                };
                (void)xQueueSend(encoder_events, &event, 0);
            }
        }
        if (stable_pressed && !long_press_sent &&
            now_us - press_start_us >= (int64_t)ENCODER_LONG_PRESS_MS * 1000) {
            encoder_event_t event = {
                .type = ENCODER_EVENT_LONG_PRESS,
                .direction = 0,
            };
            (void)xQueueSend(encoder_events, &event, 0);
            long_press_sent = true;
        }
        TickType_t sample_delay = pdMS_TO_TICKS(ENCODER_SAMPLE_MS);
        vTaskDelay(sample_delay == 0U ? 1U : sample_delay);
    }
}

static bool init_nvs(void)
{
    esp_err_t result = nvs_flash_init();
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "NVS unavailable; no automatic erase attempted: %s",
                 esp_err_to_name(result));
        return false;
    }
    return true;
}

static void start_encoder_poll_task(void)
{
    if (!start_encoder_tasks()) {
        return;
    }
    if (xTaskCreate(encoder_poll_task, "encoder_poll", 3072, NULL, 6, NULL) != pdPASS) {
        ESP_LOGE(TAG, "Could not create encoder polling task");
    }
}

void app_main(void)
{
    setenv("TZ", "JST-9", 1);
    tzset();

    (void)motor_output_init();

    nvs_ready = init_nvs();

    lv_display_t *display = bsp_display_start();
    if (display == NULL) {
        ESP_LOGE(TAG, "Waveshare display initialization failed");
        return;
    }

    if (rtc_init()) {
        (void)rtc_restore_system_time();
        start_rtc_sync_worker();
    }

    ESP_ERROR_CHECK(bsp_display_backlight_on());

    esp_err_t sd_result = bsp_sdcard_mount();
    if (sd_result != ESP_OK) {
        ESP_LOGW(TAG, "microSD unavailable; using fallback face (%s)",
                 esp_err_to_name(sd_result));
    }

    scan_dials(sd_result == ESP_OK);
    uint8_t *initial_pixels = NULL;
    dial_style_t style;
    selected_index = choose_initial_dial(&initial_pixels, &style);
    preview_index = selected_index;

    ESP_ERROR_CHECK(bsp_display_lock(portMAX_DELAY));
    create_clock_view(&clock_view, &style, initial_pixels);
    preview_has_valid_image = clock_view.has_face_image;
    if (dial_count > 0U && !preview_has_valid_image) {
        show_dial_status(&clock_view, "No readable face.jpg found");
    }
    bsp_display_unlock();

    start_encoder_poll_task();
    start_wifi_time_task();

    ESP_LOGI(TAG, "3.4C clock view started; face image: %s",
             clock_view.has_face_image ? "loaded" : "fallback");
}
