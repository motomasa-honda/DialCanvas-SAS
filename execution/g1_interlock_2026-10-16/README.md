# G1 physical manual re-arm latch transition: 71 pads → 85 pads (2026-10-16)

Reworked source-accurate Phase74 partial KiCad9 schematic by introducing U_ARM, a manufacturer pin-mapped TI SN74LVC2G74DCUR and two-terminal normally-open manual rearm header. Two isolated 10k pull-downs provide default logic in the review diagram. Previous Phase74 71 endpoints/24 nets become 85 endpoints/29 named nets, and all existing STOP/5V/PG/heartbeat nodes are preserved.

CRITICAL: CLK rearm debouncer, D=qualified two-edge+ARM-low hardware, PG-falling fault latch, 28-phase inhibit and manufacturer footprint/real KiCad ERC/PCB DRC are UNBUILT. U_ARM.Q is ISOLATED; U7.EN remains only with existing 10k GND resistor. No permission to energize motors. Vendor TPS3431 SET1 disabling watchdog can leave WDO unasserted; welded NC STOP also is not detected.

Full verified archive: Forest_Guardian_G1_Independent_Latch_85Pins_Review_2026-10-16.zip (54,132 bytes, 21 files), SHA256 9e21d7beb0491a64feed7e505ab7ef9da679c12f9e7dc7ea729b9a8fdae31409. Contains actual 61KB editable KiCad9 partial schematic, exact Phase72/73 generator, original Phase74 source, new Python generator, 85-pin CSV, 13 safety blockers, ten independent ideal-logical tests, 256x5 combinations, 20,000 random transitions, 8 wrong wiring cases and full content manifest verification. Those full tests PASS locally, but GitHub CI checks only summarized immutable review status and source-bound manufacturer pin contract; it cannot claim native ERC/physical safety.

TI source: https://www.ti.com/lit/ds/symlink/sn74lvc2g74.pdf ; https://www.ti.com/lit/ds/symlink/tps25947.pdf ; https://www.ti.com/lit/ds/symlink/tps3808.pdf ; https://www.ti.com/lit/ds/symlink/tps3431.pdf .

G1-05/G1-06 still WORKING, 19/48 DONE_SCOPE, 0/6 manufacturing, SW11/14. No purchasing, cutting, power, flashing or main merge.