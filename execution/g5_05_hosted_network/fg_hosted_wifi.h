#pragma once
/* Espressif Hosted station over board's ESP32-C6 SDIO coprocessor.
 * This file NEVER flashes or configures ESP32-C6 slave firmware. */
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
typedef struct {
 atomic_bool ip_ready;
 atomic_uint disconnect_count;
 bool started;
} fg_hosted_wifi;
bool fg_hosted_wifi_start(fg_hosted_wifi *s,const char *ssid,const char *pass);
bool fg_hosted_wifi_ip_ready(const fg_hosted_wifi *s);
