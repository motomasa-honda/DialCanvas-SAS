# G5-05: HTTPS pairing/role API — Part 1 real product integration (WORKING)

This is an actual code delta against the existing SHA-pinned ESP32-P4 product firmware archive, not a new abstract product skeleton.

- A physical **SW1+SW2 five-second chord** in existing control task creates a **60 second local-only six-digit pairing challenge**, only while OFF and ARM=0.
- 5 wrong attempts lock pairing for 5 minutes. No pairing without physical action. Token 32 bytes from ESP secure hardware randomness. NVS persists **SHA-256 token digests** before issue; NVS failure prevents token issuance.
- Role authorization recognizes VIEWER/OPERATOR/ADMIN. No raw GPIO/write endpoints. Viewer cannot start; operator cannot clear fault; only ADMIN may issue other roles.
- Incoming network requests are **not registered at all** at this stage. ESP32-P4 board uses external Wi-Fi coprocessor and needs confirmed provisioned network, HTTPS certificate installation, protected REST routes, mutexes between control task and network task, and physical monitor HIL. Tokens stay unretrievable until these complete.
- `apply_product.py` patches actual product main.c (known unique anchors) and CMake to compile the module; control task remains sole writer for `fg_intent`; eFuse EN=GND and all phase OEs HIGH remain unmodified in physical hardware.
- Tests are **risk-specific**, not quantity-driven: physical pairing precondition, brute force lockout, save fails closed, reboot role persistence, role-denied raw hardware operations, expiry and secure RNG failure.
- Product build on **real ESP32-P4 IDF 5.5.2** and C host tests are CI acceptance. Not a claim G5-05 DONE until HTTPS transport/paired network operations actually exist.

Current 48-scope project counter remains **20/48 DONE_SCOPE**, G5-05 **WORKING**, manufacturing **0/6**, SW review evidence **11/14** unchanged. No purchasing, fabrication, firmware flashing, energization, or merging main.
