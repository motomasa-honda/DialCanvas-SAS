#pragma once
/* ESP32-P4 HTTPS route handlers. No WiFi start and no certificate provisioning here.
 * Caller MUST prove IP readiness and provide an approved TLS cert/key.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "esp_err.h"
#include "esp_http_server.h"
#include "fg_web_access.h"
#include "fg_intent.h"
typedef struct {
 fg_web_access *auth;
 SemaphoreHandle_t auth_mutex;
 QueueHandle_t intent_queue;
 const atomic_int *shown_state;
 const atomic_int *shown_fault;
 atomic_uint *pairing_code_local;
 httpd_handle_t server;
} fg_https_api;
void fg_https_api_init(fg_https_api*,fg_web_access*,SemaphoreHandle_t,QueueHandle_t,
                       const atomic_int*,const atomic_int*,atomic_uint*);
bool fg_https_start_if_ready(fg_https_api*,bool,
                             const uint8_t*,size_t,const uint8_t*,size_t);
void fg_https_stop(fg_https_api*);
