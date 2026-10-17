#ifndef FG_WEB_ACCESS_H
#define FG_WEB_ACCESS_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define FG_WEB_TOKEN_BYTES 32u
#define FG_WEB_ROLE_COUNT 3u
#define FG_WEB_PAIR_WINDOW_MS 60000u
#define FG_WEB_PAIR_MAX_TRIES 5u
#define FG_WEB_PAIR_LOCK_MS 300000u
typedef enum {FG_WEB_NO_ROLE=0,FG_WEB_VIEWER=1,FG_WEB_OPERATOR=2,FG_WEB_ADMIN=3} fg_web_role;
typedef enum {FG_WEB_DENIED=0,FG_WEB_OK=1,FG_WEB_BAD_ARGUMENT=2,FG_WEB_PERSIST_FAILED=3} fg_web_result;
typedef struct {bool active;uint8_t sha256[32];} fg_web_credential;
typedef struct {fg_web_credential by_role[FG_WEB_ROLE_COUNT];} fg_web_credentials;
typedef bool (*fg_web_save_fn)(void*,const fg_web_credentials*);
typedef bool (*fg_web_random_fn)(void*,uint8_t*,size_t);
typedef struct {
 fg_web_credentials credentials;
 uint32_t local_code;
 uint64_t window_end_ms,lock_end_ms;
 unsigned failures;
 bool open;
 fg_web_save_fn save;
 fg_web_random_fn random;
 void *io_context;
} fg_web_access;
void fg_web_access_init(fg_web_access*,fg_web_credentials,fg_web_save_fn,fg_web_random_fn,void*);
bool fg_web_open_local_pairing(fg_web_access*,uint64_t,uint32_t*);
fg_web_result fg_web_claim_admin(fg_web_access*,uint64_t,uint32_t,uint8_t[FG_WEB_TOKEN_BYTES]);
fg_web_result fg_web_issue_role(fg_web_access*,fg_web_role,fg_web_role,uint8_t[FG_WEB_TOKEN_BYTES]);
fg_web_role fg_web_authenticate(const fg_web_access*,const uint8_t*,size_t);
bool fg_web_permit(fg_web_role,const char*,const char*);
void fg_web_access_expire(fg_web_access*,uint64_t);
#endif
