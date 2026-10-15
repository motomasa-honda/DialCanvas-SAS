# Forest Guardian / DialCanvas Desk Edition — Phase73

## Two actual D-FF pin connections, but NO motor-power permission

Phase72 source-derived `U_EDGE` / `U_RUN` are two **single** SN74LVC2G74DCUR D-FFs; Q1 to D2, both CLK from inverter output, D1 HIGH, both active-low CLEAR tied to the open-drain TPS3431 WDO and TPS3808G33 RESET_N. Exactly 59 manufacturer-numbered terminals are allocated across 22 labeled review nets in [`connectivity.json`](./connectivity.json). The output of second FF `HB_TWO_EDGE_Q_ISOLATED` is **NOT** wired to power. U7/TPS259474LRPW EN is still pulled to GND through 10k.

**This is NOT a completed hardware safety device.** STOP loop, independent manual rearm/fault latch, 5V supervisor, PG post-startup qualified fault detection, full eFuse current/slew passives, footprint approval, KiCad native ERC and PCB DRC remain unimplemented. Power rail is not permitted; gates 0/6 and SW 11/14 unchanged.

### Verified source timing mismatch

Immutable Phase67 product `app_main.c::recovery_probe` and `control.c::fg_heartbeat` both switch the GPIO28 heartbeat after a literal **50,000µs HALF period**. Two transitions are required per TPS3431 falling edge: nominal **100ms**, not the 80ms prior design recommendation. **Measured real time/jitter is unavailable.**

The [isolated candidate patch](./patches/phase73-heartbeat-80ms.patch) adds one shared constant `FG_HEARTBEAT_TOGGLE_US=40000` to both source modules: nominal 80ms falling-edge period. Minimum datasheet watchdog timeout 170ms minus nominal period 80ms = 90ms arithmetic margin, **not a measured worst-case margin**. It preserves ARM=0 when running `recovery_probe`; physically resetting WDO must not permit power to auto-resume.

### Reproducible evidence

- [`check_qualifier.py`](./check_qualifier.py): direct pad audit against Phase72 vendor contract, exhaustive 10,240 shift transition steps and six intentionally broken wiring mutations. [GitHub Actions PASS: Phase73 static review](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38815945772).
- [`tests/heartbeat_host.c`](./tests/heartbeat_host.c): execute actual candidate `control.c` logic (40ms half-cycle, 80ms falling, input validation, phase invalid fail).
- [Phase73 ESP32-P4 candidate target build](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38816666855) layers Phase69 safe RAW recovery and Phase73 heartbeat on SHA-pinned Phase67 firmware, candidate RAW A/B partition, ESP-IDF 5.5.2. **PASS** on run 38816666855: physical device is NOT flashed or tested, but actual reviewed ESP32-P4 BIN 881,856 bytes, SHA256 `d839baf2483459ffaf83352f684a0a308b5642c544f2b3868e7f77b30ddd68e3`; partition table SHA256 `77a23ddc01b5fa76ce377dc7bbdc9e9bd4511131c047736305c44f57425e5a5a`. Host C test executed successfully in CI. Artifact ID **12010529661**, archive SHA256 `6e197ed192172daa6dcd9e0d1c27961b9eb2cfa053af7b6e6641b8a18439a4e5`.
- The companion Phase73 integrated handoff ZIP also contains native-format **review-only** KiCad schematic and host tests. There is NO KiCad ERC PASS, real circuit operation or DRC PASS.

No original D7 CAD, approved partitions, `main`, eFuse enable source, or hardware flashing was changed. Draft PR #2 only.
