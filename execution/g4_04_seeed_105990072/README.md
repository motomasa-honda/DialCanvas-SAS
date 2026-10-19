# Seeed 105990072 source-CAD review

## Result

The vendor EAGLE source contains a panelized board file. Parsing the smallest closed layer-20 outline enclosing the populated circuit gives a **nominal PCB envelope of 35.0 × 19.3 mm**. The 50 × 41 mm per-axis reservation therefore leaves a centered bare-PCB clearance of 7.5 mm per side in X and 10.85 mm per side in Y. The motor driver board has **no mounting holes inside its PCB outline**.

The separately published motor drawing identifies model `CX28BYJ48-08`: body Ø28±0.1 mm, two mounting holes Ø4.2±0.15 mm at 35±0.2 mm centers, body depth 19.1±0.2 mm, shaft Ø5±0.1 mm with 13.5±0.2 mm projection, and Ø9±0.2 mm shaft boss. The factory lead is shown as 250±10 mm, UL1061 26AWG. These are source drawing dimensions, not measured incoming parts.

The exact EAGLE footprints and board/schematic connectivity resolve the headers as follows. “IN1” through “IN4” refer to the ULN2003 input pins 1B through 4B respectively.

| Connector | Pad | Signal / connection | Pitch |
| --- | ---: | --- | ---: |
| J5 control | 1 | VM | 2.54 mm |
| J5 control | 2 | VCC / ULN2003 COM | 2.54 mm |
| J5 control | 3 | GND / ULN2003 E | 2.54 mm |
| J5 control | 4 | IN4 / ULN2003 4B | 2.54 mm |
| J5 control | 5 | IN3 / ULN2003 3B | 2.54 mm |
| J5 control | 6 | IN2 / ULN2003 2B | 2.54 mm |
| J5 control | 7 | IN1 / ULN2003 1B | 2.54 mm |
| J4 motor | 1 | VMOTOR | 2.54 mm |
| J4 motor | 2 | ULN2003 4C | 2.54 mm |
| J4 motor | 3 | ULN2003 3C | 2.54 mm |
| J4 motor | 4 | ULN2003 2C | 2.54 mm |
| J4 motor | 5 | ULN2003 1C | 2.54 mm |

The schematic device mapping explicitly maps J4 symbol pins `P$1`…`P$5` to footprint pads `1`…`5`, and J5 symbol pins `1`…`7` to footprint pads `1`…`7`. Thus J4 pad/net order is established from two independent source files: schematic pin → package pad → board contact/net → ULN2003 collector. In J4 package-local coordinates, pad 1 is at `(5.08, 0)` mm and pad 5 at `(-5.08, 0)` mm; the placed board element is rotated `R270`. This establishes the source-CAD pad identity and order, but it does not establish a user-facing viewing direction or the conductor colors on an as-received cable. Preserve the connector's keyed/latch orientation in the harness drawing and confirm every supplied conductor by continuity before fixing a wire-color-to-pad table.

J5 is the vendor `H7-2.54` seven-position through-hole footprint; J4 is the vendor `JST5-2.54` five-position through-hole footprint. The largest source pad drills are 0.889 mm (J5) and 0.8128 mm (J4). Verify the supplied cable and mating connector before choosing harness ends; the EAGLE footprint name does not identify the mating housing vendor or its retention force.

**Connector discrepancy:** the motor drawing calls out a white `XHP-5` housing at 2.5 mm pitch, while the driver board EAGLE J4 pad centers are 2.54 mm pitch. This is 0.04 mm per interval, or 0.16 mm across the first-to-fifth center distance. JST's XH catalog specifies the series as 2.5 mm pitch. Direct plug compatibility is therefore **not accepted** from the drawings alone. The low-risk design route is a documented short adapter harness or an exact connector replacement selected after confirming the supplied board revision; do not force the motor plug onto the board header.

## Scope and remaining acceptance

The archived vendor files, extracted board and schematic, SHA-256 evidence, and deterministic parser are kept here. Run:

```sh
python3 execution/g4_04_seeed_105990072/check_vendor_cad.py
```

This is a static parse of the vendor source, not proof that a purchased production unit has the same revision or dimensions. The no-hole board needs a removable edge-capture or pocket in each axis cassette. That retention must preserve independent service access and avoid stressing solder joints. Connector insertion/removal clearance and wire bend radius must be added outside the bare-board rectangle. The 35 mm motor mount span and 35 mm PCB width both approach the 44 mm sled width; retain the motor's Ø3.5 mm lug radii, Ø4.2 mm holes, fastener washers, wall thickness, tool access, and gear-shaft alignment in the next local CAD pass. Actual received-unit dimensions, shaft/coupler fit, loaded torque/current/temperature, noise, and seven-axis operation remain unverified.

Status remains **G4-04 OPEN / FG-026 OPEN / G3-08 HARDWARE_WAIT**. No part has been ordered, powered, fabricated, or approved for manufacturing. Motor enable and driver OE remain inhibited.

## Source provenance

- Manufacturer page and linked CAD archive: <https://wiki.seeedstudio.com/Gear_Stepper_Motor_Driver_Pack/>
- Official JST XH 2.5 mm series catalog: <https://www.jst-mfg.com/product/pdf/eng/eXH.pdf>
- Direct archive URL and source checksums: [`cad_evidence.json`](cad_evidence.json)
- Vendor files are preserved under [`source/`](source/), without edits.
