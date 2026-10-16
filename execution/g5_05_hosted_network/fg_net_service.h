#pragma once
/* The secret-loader is disabled unless ESP-IDF default NVS is encrypted.
 * No hard-coded test password or private key ever enters a product build. */
#include "fg_hosted_wifi.h"
#include "fg_https_api.h"
#include <stdint.h>
#include <stddef.h>
#define FG_NET_CERT_CAP 4096
#define FG_NET_KEY_CAP 4096
typedef struct {
 fg_hosted_wifi wifi;
 char ssid[33],password[65];
 uint8_t cert[FG_NET_CERT_CAP],private_key[FG_NET_KEY_CAP];
 size_t cert_len,key_len;
} fg_net_credentials;
bool fg_net_load_protected_nvs(fg_net_credentials*);
void fg_net_service_loop(fg_net_credentials*,fg_https_api*);
