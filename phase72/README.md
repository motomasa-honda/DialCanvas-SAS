# Forest Guardian — Phase72 TI device pin audit + fail-closed hardware preparation

**Partial engineering deliverable only. No fabrication, motor power, KiCad ERC/DRC or accepted safety test.**

## New verified manufacturer-level decisions

- Selected eFuse `TPS259474LRPW`: **PG pin3 / PGTH pin4 (NO FLT)**, IN pin5, OUT pin6, EN/UVLO pin1. [TI source](https://www.ti.com/lit/ds/symlink/tps25947.pdf).
- Watchdog `TPS3431DRBR`: DRB-8, VDD1/CWD2/EN3/GND4/SET1-5/WDI6/WDO7/ENOUT8; WDI falling edge, 10k CWD pullup to 3V3 and SET1 HIGH = **170–230ms timeout**, 200ms nominal. [TI source](https://www.ti.com/lit/ds/symlink/tps3431.pdf).
- Real logic candidates: `SN74LVC2G74DCUR` **one flip-flop per IC** (two instances required for edge/run functions), `SN74LVC1G04DBVR` falling-edge inverter, `TPS3808G33DBVR` 3V3 POR (RESET open drain, **not 5V supervision**).
- ElectroPeak **MTR-09-024 = nominal 35×31mm**, whereas **MTR-09-004 = 40×20mm**, different SKU. This resolves the vendor catalog discrepancy but NOT the physical module dimensions, holes, pin orientation, and 55mm service motion. Preserve provisional **40×31mm planar mechanical envelope**. [Selected product](https://electropeak.com/five-wire-four-phase-uln2003stepper-motor-driver-board); [other SKU](https://electropeak.com/ul2003-4-phase-stepper-motor-driver).

- **PGTH candidate (CALCULATION ONLY)**: 47kΩ upper / 17.4kΩ lower resistors (1%); output voltage at PGTH thresholds nominal approx **4.44V rising / 4.03V falling**. Resistor extremes plus TI threshold variability bracket roughly **4.32–4.59V rising / 3.92–4.19V falling**. Separate 47kΩ PG pull-up resistor also staged. **PG stays LOW until start-up qualifies and does not indicate every transient overcurrent fault**. This does *not* close the PG/startup fault-latch design. See TI [TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf).

## Implemented GitHub files

- `vendor_contract.json`: six exact TI pad maps (**45 semiconductor pads**), calculated PGTH candidate limits and verified watchdog specification; physical functions still absent marked `NOT_BUILT`. No eFuse drive source.
- `check_vendor.py`: validates part variants, all pads, 7-axis fuse count, operating configuration and 512 abstract combinations. It refuses to count an unsafe/unbuilt circuit as finished; validates the PGTH divider and its resistor/threshold extremes.
- `.github/workflows/phase72-component-review.yml`: reproducible SHA-pinned Phase67 original source + vendor contract CI with evidence.

**[GitHub Actions SUCCESS: run 38748346408](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38748346408)**. Artifact `phase72-manufacturer-pin-review-evidence` ID **11980362759**; SHA256 digest `ae843a6d79d2b94e850ce1b090850703e3c64c15b62644d3a632286830d20419`.

The **companion integrated handoff ZIP** additionally contains a 59-terminal native-format **partial** KiCad schematic (6 TI ICs + 7 resistors); 51 Python host unit tests PASS (incl 3 bypass/short mutants), prior Phase71 23 regression tests PASS, updated open-issues CSV and physical acceptance plan. The KiCad file is intentionally built with **U7 EN held low via 10k pulldown**. Other parts of the gate, STOP, PG blanking, 5V_RAW supervisor, second falling-edge qualifier and qualified external GPIO22 fault **DO NOT EXIST** yet. Neither KiCad CLI/ERC nor real PCB DRC nor hardware power/test has passed.

### Release block

The only valid disposition is **REVIEW / NOT SAFE TO ENERGIZE**. Manufacturing **0/6**; software evidence **11/14**, SW09/SW12/SW14 open. PR must stay Draft and main unchanged, no hardware flashing/purchasing/PCB manufacturing.
