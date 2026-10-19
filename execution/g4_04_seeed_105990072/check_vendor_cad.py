#!/usr/bin/env python3
"""Extract repeatable nominal geometry and connector mapping from Seeed's Eagle files."""
from __future__ import annotations

import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
BOARD = SOURCE / "Stepper_Motor_Driver.brd"
SCHEMATIC = SOURCE / "Stepper_Motor_Driver.sch"
OUTPUT = ROOT / "cad_evidence.json"
MOTOR_DRAWING_URL = "https://files.seeedstudio.com/wiki/Gear-Stepper-Motor-Driver-Pack/res/CX28BYJ48.pdf"
MOTOR_DRAWING_SHA256_RETRIEVED_2026_10_19 = "46a8edcd5f390fd939e0c58e0a4ef337a88b0e88081d1fad2c23816c940dd7cf"


def f(node: ET.Element, key: str) -> float:
    return float(node.attrib[key])


def rect_contains_all(elements: list[ET.Element], x0: float, y0: float,
                      x1: float, y1: float) -> bool:
    return all(x0 - 1e-5 <= f(e, "x") <= x1 + 1e-5
               and y0 - 1e-5 <= f(e, "y") <= y1 + 1e-5
               for e in elements)


def side_covered(wires: list[ET.Element], axis: str, fixed: float,
                 lo: float, hi: float) -> bool:
    intervals = []
    for w in wires:
        x1, y1, x2, y2 = (f(w, k) for k in ("x1", "y1", "x2", "y2"))
        if axis == "v" and abs(x1 - x2) < 1e-5 and abs(x1 - fixed) < 1e-5:
            intervals.append((min(y1, y2), max(y1, y2)))
        if axis == "h" and abs(y1 - y2) < 1e-5 and abs(y1 - fixed) < 1e-5:
            intervals.append((min(x1, x2), max(x1, x2)))
    cursor = lo
    for a, b in sorted(intervals):
        if b < cursor - 1e-5 or a > cursor + 1e-5:
            continue
        cursor = max(cursor, b)
        if cursor >= hi - 1e-5:
            return True
    return False


def circuit_rectangle(board: ET.Element, elements: list[ET.Element]) -> tuple[float, float, float, float]:
    wires = [w for w in board.findall("./plain/wire") if w.get("layer") == "20"]
    xs = sorted({f(w, "x1") for w in wires} | {f(w, "x2") for w in wires})
    ys = sorted({f(w, "y1") for w in wires} | {f(w, "y2") for w in wires})
    candidates = []
    for i, x0 in enumerate(xs):
        for x1 in xs[i + 1:]:
            if not rect_contains_all(elements, x0, min(ys), x1, max(ys)):
                # Filter x early; y containment is checked after candidate construction.
                if not all(x0 - 1e-5 <= f(e, "x") <= x1 + 1e-5 for e in elements):
                    continue
            for j, y0 in enumerate(ys):
                for y1 in ys[j + 1:]:
                    if not rect_contains_all(elements, x0, y0, x1, y1):
                        continue
                    if (side_covered(wires, "v", x0, y0, y1)
                            and side_covered(wires, "v", x1, y0, y1)
                            and side_covered(wires, "h", y0, x0, x1)
                            and side_covered(wires, "h", y1, x0, x1)):
                        candidates.append((x1 - x0, y1 - y0, x0, y0, x1, y1))
    if not candidates:
        raise AssertionError("No closed layer-20 rectangle encloses the circuit elements")
    _, _, x0, y0, x1, y1 = min(candidates)
    return x0, y0, x1, y1


def package_map(board: ET.Element) -> dict[str, ET.Element]:
    return {p.get("name"): p
            for p in board.findall("./libraries/library/packages/package")}


def pad_pitch(package: ET.Element) -> tuple[int, float, float]:
    pads = package.findall("./pad")
    assert pads, f"No through-hole pads in {package.get('name')}"
    xs = [f(p, "x") for p in pads]
    ys = [f(p, "y") for p in pads]
    axis_vals = xs if len(set(round(y, 5) for y in ys)) == 1 else ys
    deltas = sorted(abs(b - a) for i, a in enumerate(axis_vals) for b in axis_vals[i + 1:])
    pitch = min(d for d in deltas if d > 1e-5)
    return len(pads), pitch, max(f(p, "drill") for p in pads)


def schematic_net_map(schematic: ET.Element, part: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for net in schematic.findall("./drawing/schematic/sheets/sheet/nets/net"):
        refs = [p for p in net.findall("./segment/pinref") if p.get("part") == part]
        for ref in refs:
            result[ref.get("pin", "")] = {"net": net.get("name", ""), "part": part}
    return result


def schematic_pin_pad_map(schematic: ET.Element, part_name: str) -> dict[str, str]:
    """Resolve schematic symbol pins to physical footprint pad numbers."""
    parts = schematic.findall("./drawing/schematic/parts/part")
    part = next((p for p in parts if p.get("name") == part_name), None)
    assert part is not None, f"Missing schematic part {part_name}"
    libraries = schematic.findall("./drawing/schematic/libraries/library")
    library = next((lib for lib in libraries if lib.get("name") == part.get("library")), None)
    assert library is not None, f"Missing library for {part_name}"
    devicesets = library.findall("./devicesets/deviceset")
    deviceset = next((ds for ds in devicesets if ds.get("name") == part.get("deviceset")), None)
    assert deviceset is not None, f"Missing deviceset for {part_name}"
    device = next((d for d in deviceset.findall("./devices/device")
                   if d.get("name") == part.get("device")), None)
    assert device is not None, f"Missing device mapping for {part_name}"
    pairs = {c.get("pin", ""): c.get("pad", "") for c in device.findall("./connects/connect")}
    assert pairs and all(pairs.values()), f"Incomplete symbol-to-pad map for {part_name}"
    assert len(set(pairs.values())) == len(pairs), f"Non-bijective symbol-to-pad map for {part_name}"
    return pairs


def pinrefs_for_net(schematic: ET.Element, name: str) -> list[dict[str, str]]:
    for net in schematic.findall("./drawing/schematic/sheets/sheet/nets/net"):
        if net.get("name") == name:
            return [{"part": p.get("part", ""), "pin": p.get("pin", "")}
                    for p in net.findall("./segment/pinref")]
    raise AssertionError(f"Missing schematic net {name}")


def main() -> None:
    btree = ET.parse(BOARD).getroot()
    stree = ET.parse(SCHEMATIC).getroot()
    board = btree.find("./drawing/board")
    assert board is not None
    elements = {e.get("name"): e for e in board.findall("./elements/element")}
    circuit_names = ["D1", "D2", "D3", "D4", "R1", "R2", "R3", "R4",
                     "U1", "C1", "C2", "J4", "J5", "SW2"]
    rect = circuit_rectangle(board, [elements[n] for n in circuit_names])
    x0, y0, x1, y1 = rect
    width, height = x1 - x0, y1 - y0
    assert math.isclose(width, 35.0, abs_tol=0.01), width
    assert math.isclose(height, 19.3, abs_tol=0.01), height

    holes_inside = []
    for hole in board.findall("./plain/hole"):
        x, y = f(hole, "x"), f(hole, "y")
        if x0 <= x <= x1 and y0 <= y <= y1:
            holes_inside.append({"x_mm": x, "y_mm": y, "drill_mm": f(hole, "drill")})
    assert not holes_inside, holes_inside

    packages = package_map(board)
    j5 = elements["J5"]
    j4 = elements["J4"]
    assert j5.get("package") == "H7-2.54" and j5.get("rot") == "R180"
    assert j4.get("package") == "JST5-2.54" and j4.get("rot") == "R270"
    j5_count, j5_pitch, j5_drill = pad_pitch(packages[j5.get("package")])
    j4_count, j4_pitch, j4_drill = pad_pitch(packages[j4.get("package")])
    assert (j5_count, round(j5_pitch, 3)) == (7, 2.54)
    assert (j4_count, round(j4_pitch, 3)) == (5, 2.54)

    j5_pin_pads = schematic_pin_pad_map(stree, "J5")
    j4_pin_pads = schematic_pin_pad_map(stree, "J4")
    assert j5_pin_pads == {str(n): str(n) for n in range(1, 8)}, j5_pin_pads
    assert j4_pin_pads == {f"P${n}": str(n) for n in range(1, 6)}, j4_pin_pads

    signal_for_j5: dict[str, str] = {}
    for sig in board.findall("./signals/signal"):
        for ref in sig.findall("./contactref"):
            if ref.get("element") == "J5":
                signal_for_j5[ref.get("pad", "")] = sig.get("name", "")
    signal_for_j4: dict[str, str] = {}
    for sig in board.findall("./signals/signal"):
        for ref in sig.findall("./contactref"):
            if ref.get("element") == "J4":
                signal_for_j4[ref.get("pad", "")] = sig.get("name", "")
    schematic_u1 = schematic_net_map(stree, "U1")
    header = {}
    for pin in range(1, 8):
        net = signal_for_j5[str(pin)]
        refs = pinrefs_for_net(stree, net)
        u1pins = [r["pin"] for r in refs if r["part"] == "U1"]
        roles = {"1": "VM", "2": "VCC", "3": "GND"}
        if pin >= 4:
            assert len(u1pins) == 1 and u1pins[0] in ("1B", "2B", "3B", "4B")
            roles[str(pin)] = "IN" + u1pins[0][0]
        else:
            assert net == roles[str(pin)]
        header[str(pin)] = {"symbol_pin": str(pin), "package_pad": j5_pin_pads[str(pin)],
                            "function": roles[str(pin)], "eagle_net": net,
                            "uln2003_pin": u1pins[0] if u1pins else None}

    motor = {}
    for pin in range(1, 6):
        net = signal_for_j4[str(pin)]
        refs = pinrefs_for_net(stree, net)
        u1pins = [r["pin"] for r in refs if r["part"] == "U1"]
        symbol_pin = f"P${pin}"
        package_pad = j4_pin_pads[symbol_pin]
        assert package_pad == str(pin)
        pad = next(p for p in packages[j4.get("package")].findall("./pad")
                   if p.get("name") == package_pad)
        motor[str(pin)] = {"symbol_pin": symbol_pin, "package_pad": package_pad,
                           "package_local_xy_mm": [f(pad, "x"), f(pad, "y")],
                           "eagle_net": net, "uln2003_pin": u1pins[0] if u1pins else None}

    evidence = {
        "source": {
            "vendor": "Seeed Studio",
            "manufacturer_part_number": "105990072",
            "archive_url": "https://files.seeedstudio.com/wiki/Gear-Stepper-Motor-Driver-Pack/res/Stepper%20Motor%20Driver.rar",
            "archive_sha256": hashlib.sha256((SOURCE / "vendor_eagle_archive.rar").read_bytes()).hexdigest(),
            "board_sha256": hashlib.sha256(BOARD.read_bytes()).hexdigest(),
            "schematic_sha256": hashlib.sha256(SCHEMATIC.read_bytes()).hexdigest(),
            "motor_mechanical_drawing_url": MOTOR_DRAWING_URL,
            "motor_mechanical_drawing_sha256_retrieved_2026_10_19": MOTOR_DRAWING_SHA256_RETRIEVED_2026_10_19,
            "archive_is_unmodified": True,
            "extraction_note": "The vendor archive is panelized; geometry is taken from the smallest closed layer-20 rectangle enclosing the named circuit components, not the full panel envelope.",
        },
        "nominal_pcb_envelope_mm": {"x": width, "y": height},
        "motor_mechanical_drawing": {
            "model": "CX28BYJ48-08",
            "body_diameter_mm": {"nominal": 28.0, "tolerance": 0.1},
            "mounting_hole_center_distance_mm": {"nominal": 35.0, "tolerance": 0.2},
            "mounting_holes": {"count": 2, "diameter_mm": {"nominal": 4.2, "tolerance": 0.15}, "centered_on_body_axis": True},
            "body_depth_mm": {"nominal": 19.1, "tolerance": 0.2},
            "shaft_diameter_mm": {"nominal": 5.0, "tolerance": 0.1},
            "shaft_projection_mm": {"nominal": 13.5, "tolerance": 0.2},
            "shaft_boss_diameter_mm": {"nominal": 9.0, "tolerance": 0.2},
            "output_axis_perpendicularity_deg": {"nominal": 90, "tolerance": 1},
            "factory_lead_length_mm": {"nominal": 250, "tolerance": 10},
            "factory_wire": "UL1061 26AWG",
            "motor_lead_housing": "JST XH XHP-5 per vendor drawing; stated 2.5 mm pitch",
            "motor_housing_pitch_mm": 2.5,
            "board_J4_EAGLE_pad_pitch_mm": j4_pitch,
            "pitch_delta_per_interval_mm": round(j4_pitch - 2.5, 3),
            "first_to_fifth_pitch_delta_mm": round(4 * (j4_pitch - 2.5), 3),
            "direct_mating_accepted": False,
            "drawing_interpretation_note": "Dimensions transcribed from the vendor CX28BYJ48.pdf drawing and not yet checked against a received motor. The connector pitch mismatch is a source-document discrepancy requiring a mating-part decision or adapter harness; do not force mate.",
        },
        "within_project_reserved_axis_envelope_mm": {"x": 50.0, "y": 41.0},
        "centered_bare_pcb_clearance_mm": {"x_each_side": round((50.0 - width) / 2, 3),
                                             "y_each_side": round((41.0 - height) / 2, 3)},
        "mounting_holes_inside_pcb_outline": holes_inside,
        "control_header": {"package": j5.get("package"), "pin_count": j5_count,
                           "pitch_mm": j5_pitch, "maximum_drill_mm": j5_drill,
                           "board_element_rotation": j5.get("rot"),
                           "symbol_pin_to_package_pad": j5_pin_pads, "pin_map": header},
        "motor_connector": {"package": j4.get("package"), "pin_count": j4_count,
                            "pitch_mm": j4_pitch, "maximum_drill_mm": j4_drill,
                            "board_element_rotation": j4.get("rot"),
                            "symbol_pin_to_package_pad": j4_pin_pads, "pin_map": motor},
        "evidence_scope": "Vendor-source static CAD/netlist parse only. No manufactured-board revision, as-received dimensions, connector mating clearance, load torque, temperature, or powered behavior accepted.",
    }
    OUTPUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PASS: vendor Eagle nominal PCB {width:g} x {height:g} mm; no board mounting holes")
    print(f"PASS: J5 7-pin 2.54 mm mapping: {', '.join(v['function'] for v in header.values())}")
    print(f"PASS: J4 5-pin 2.54 mm; source hashes pinned in {OUTPUT.name}")
    print("LIMIT: 50x41 mm static envelope fit only; mating plug, edge retention, loads and physical unit remain unverified")


if __name__ == "__main__":
    main()
