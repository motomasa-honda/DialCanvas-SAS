idf_component_register(
    SRCS "app_main.c"
    INCLUDE_DIRS "."
    REQUIRES cots_clock_core esp32_p4_wifi6_touch_lcd_xc esp_jpeg lvgl json heap log freertos esp_netif esp_event esp_timer nvs_flash esp_wifi_remote esp_driver_gpio esp_driver_i2c
)
