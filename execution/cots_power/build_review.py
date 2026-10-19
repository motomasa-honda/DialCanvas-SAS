#!/usr/bin/env python3
"""Replace the discrete G1-95 buck branch with a named-terminal COTS module.

G1-94's 618 original pin/net bindings stay unchanged. The generated drawing
contains real module terminal names, NOT an invented pad order or footprint.
No power flag, supply waiver, motor grant or production output is added.
"""
import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "g1_94_native_erc_cleanup"
PROJECT = "forest_guardian_cots_aon_review"
PARENT_PROJECT = "forest_guardian_g1_94_real_nc_cleanup_review"
ROOT_UUID = "6c498f0d-d858-4eaa-adb9-b8d5e4383e8a"


def sid(value):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "ForestGuardian:COTS:" + value))


def number(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def expression(text, token):
    start = text.index(token)
    depth = 0
    quote = False
    escape = False
    for pos in range(start, len(text)):
        char = text[pos]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                quote = False
        elif char == '"':
            quote = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    raise ValueError("Unbalanced KiCad expression")


def module_symbol(source, terminals):
    symbol = expression(source, '(symbol "FG_REVIEW:PAD4"')
    symbol = symbol.replace("FG_REVIEW:PAD4", "FG_COTS:D24V5F3").replace("PAD4_", "D24V5F3_")
    symbol = symbol.replace('"REVIEW_ONLY_PAD4"', '"D24V5F3_NAMED_TERMINALS"')
    symbol = symbol.replace('(pin_names (offset 0) (hide yes))', '(pin_names (offset 0.508))')
    # Names are the board's actual VIN/GND/VOUT/SHDN silkscreen identifiers.
    # No positional/numbered PCB pad identity is claimed.
    for i, terminal in enumerate(terminals, 1):
        pin = expression(symbol, f'(pin passive line (at -10.16 {number((2.5-i)*2.54)}')
        replacement = pin.replace("(pin passive line", f"(pin {terminal['electrical_type']} line", 1)
        replacement = replacement.replace(f'(name "P{i}"', f'(name "{terminal["name"]}"')
        replacement = replacement.replace(f'(number "{i}"', f'(number "{terminal["name"]}"')
        symbol = symbol.replace(pin, replacement, 1)
    return symbol


def instance(ref, lib, value, x, y):
    return f'''  (symbol (lib_id "{lib}") (at {number(x)} {number(y)} 0) (unit 1)
    (in_bom no) (on_board no) (dnp no) (uuid "{sid(ref+':instance')}")
    (property "Reference" "{ref}" (at {number(x+2.54)} {number(y-12.7)} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (at {number(x+2.54)} {number(y+12.7)} 0) (effects (font (size 1.05 1.05))))
    (property "Footprint" "" (at {number(x)} {number(y)} 0) (effects (font (size 1 1))))
    (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
  )'''


def terminal(rows, drawing, ref, pin, label, net, x, y, nc=False):
    end = number(x + 5.08)
    x, y = number(x), number(y)
    # KiCad9 omits a duplicate name when the pin name equals its number.
    # Observed in native run 39217395526: SHDN/SHDN -> (U46-PadSHDN).
    identity = f"{ref}-Pad{pin}" if str(pin) == label else f"{ref}-{label}-Pad{pin}"
    actual_net = f"unconnected-({identity})" if nc else net
    rows.append(dict(group="COTS", source_ref=ref, source_pin=pin,
                     source_net=actual_net, review_net=actual_net, kicad_ref=ref,
                     wire_end_x=x, wire_end_y=y))
    if nc:
        drawing.append(f'  (no_connect (at {end} {y}) (uuid "{sid(ref+str(pin)+":nc")}"))')
    else:
        drawing.extend([
            f'  (wire (pts (xy {x} {y}) (xy {end} {y})) (stroke (width 0) (type default)) (uuid "{sid(ref+str(pin)+":wire")}"))',
            f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1 1))) (uuid "{sid(ref+str(pin)+":label")}"))'
        ])


def build(output):
    subprocess.run([sys.executable, str(PARENT / "build_review.py")], check=True)
    output.mkdir(parents=True, exist_ok=True)
    data = json.loads((HERE / "components.json").read_text())
    text = (PARENT / (PARENT_PROJECT + ".kicad_sch")).read_text().replace(PARENT_PROJECT, PROJECT)
    rows = json.loads((PARENT / "pin_map_618_clean.json").read_text())
    symbol = module_symbol(text, data["converter"]["terminals"])
    library = expression(text, "(lib_symbols")
    insert = text.index(library) + len(library) - 1
    text = text[:insert] + "\n" + symbol + "\n " + text[insert:]
    text = text.replace('(paper "User" 1450 2700)', '(paper "User" 1450 3000)')
    drawing = []
    for i, item in enumerate(data["converter"]["terminals"], 1):
        terminal(rows, drawing, "U46", item["name"], item["name"], item["net"],
                 48.26, 2743.2 + (i-2.5)*2.54, nc=item["net"] is None)
    drawing.append(instance("U46", "FG_COTS:D24V5F3", "POLOLU_2842_D24V5F3_CANDIDATE", 63.5, 2743.2))
    for i, net in enumerate(("B77__5V_RAW", "GND"), 1):
        terminal(rows, drawing, "J20", i, f"P{i}", net, 160.02, 2743.2+(i-1.5)*2.54)
    drawing.append(instance("J20", "FG_REVIEW:PAD2", "DC_5V_INTERFACE_JACK_PROTECTION_TBD", 175.26, 2743.2))
    text = text.rstrip()[:-1] + "\n" + "\n".join(drawing) + "\n)\n"
    (output / (PROJECT + ".kicad_sch")).write_text(text)
    (output / "FG_COTS.kicad_sym").write_text('(kicad_symbol_lib\n (version 20231120)\n (generator "kicad_symbol_editor")\n' + symbol.replace('"FG_COTS:D24V5F3"', '"D24V5F3"', 1) + '\n)\n')
    (output / "pin_map.json").write_text(json.dumps(rows, indent=2) + "\n")
    with (output / "module_wiring.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["reference", "manufacturer_terminal_name", "net", "scope"])
        for item in data["converter"]["terminals"]:
            writer.writerow(["U46", item["name"], item["net"] or "NC_INTERNAL_PULLUP_TO_VIN", "NO_FOOTPRINT_OR_PHYSICAL_PAD_ORDER"])
    print(f"WROTE {output}: {len(rows)} terminal bindings; module AON upstream of motor eFuse; no motor enable")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "generated")
    build(parser.parse_args().output)
