#pragma once
#include "fg_ota_gate.h"
/* Review firmware explicitly blocks OTA writes: no hardware HIL certificate. */
fg_ota_result fg_ota_native_stage_for_review(const fg_ota_source *source,
                                               size_t size);
/* Called only AFTER physical ARM is forced LOW at startup.
 * On unqualified OTA first boot, request rollback; NEVER mark app valid. */
/* False means app_main MUST stop before control/network tasks are created.
 * In pending-verify state rollback may reboot; returning is always failure. */
bool fg_ota_boot_guard_unqualified(void);
