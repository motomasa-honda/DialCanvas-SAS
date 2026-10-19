#!/usr/bin/env python3
"""Check COTS source boundaries, unchanged inhibition, and optional native output."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from power_budget import estimate, positive

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def verify_data():
    data = json.loads((HERE / "components.json").read_text())
    assert data["status"] == "UNPOWERED_MODULE_INTEGRATION_CANDIDATE"
    assert not any(data["release"].values())
    assert data["selection"]["production_selected"] is False
    assert data["selection"]["aon_converter"] == "Pololu D24V5F3 #2842"
    assert data["adapter"]["rated_v"] == 5 and data["adapter"]["rated_a"] == 5
    for source in data["sources"].values():
        assert "url" in source or (ROOT / source["path"]).is_file()
    # Confirm fan screening remains the existing candidate's rated, not peak, value.
    fan = json.loads((ROOT / data["sources"]["fan"]["path"]).read_text())
    assert data["screening"]["fan_rated_a_not_peak"] == fan["manufacturer_rated_data"]["rated_current_ma"] / 1000
    report = estimate(data)
    assert report["hardware_release"] is False
    assert report["decision"].startswith("HOLD_")
    for name, value in data["unmeasured"].items():
        if value is not None:
            positive(value, name, allow_zero=name in {"seven_driver_board_overhead_5v_peak_a", "other_raw_5v_peak_a"})
    # Scope/status comes from the current ledger; never freeze project done count.
    import csv
    tasks = {r["ID"]: r for r in csv.DictReader((ROOT / "execution/tasks.csv").open())}
    assert set(data["task_ids"]) <= set(tasks)
    print("PASS COTS catalog/load boundaries; no purchase/power/release; current ledger IDs retained")


def verify_generated(output, native=None):
    data = json.loads((HERE / "components.json").read_text())
    old = json.loads((HERE.parent / "g1_94_native_erc_cleanup/pin_map_618_clean.json").read_text())
    rows = json.loads((output / "pin_map.json").read_text())
    assert rows[:len(old)] == old, "Original safety-net membership changed"
    mapping = {(r["kicad_ref"], str(r["source_pin"])): r["review_net"] for r in rows}
    assert len(mapping) == len(rows) == len(old) + 6
    expected = {("U46", x["name"]) for x in data["converter"]["terminals"]} | {("J20", "1"), ("J20", "2")}
    prior = {(r["kicad_ref"], str(r["source_pin"])) for r in old}
    assert set(mapping) - prior == expected
    net = lambda ref, pin: mapping[ref, str(pin)]
    assert net("U46", "VIN") == net("J20", 1) == net("U14", 5) == "B77__5V_RAW"
    assert net("U46", "GND") == net("J20", 2) == net("R4", 2) == "GND"
    assert net("U46", "VOUT") == "3V3_AON"
    assert net("U46", "SHDN") == "unconnected-(U46-SHDN-PadSHDN)"
    assert net("U14", 6) == "5V_MOTOR" and net("U14", 6) != net("U46", "VIN")
    for ref, pin in (("U20", 8), ("U33", 6), ("U36", 6), ("U42", 6), ("U43", 5)):
        assert net(ref, pin) == net("U46", "VOUT")
    assert net("U14", 1) == net("R4", 1) == net("R67", 1) == net("R68", 2)
    assert net("R4", 2) == net("R67", 2) == "GND"
    for ref in ("U15", "U16", "U17", "U18"):
        assert net(ref, 1) == net(ref, 19) == "B78__PHASE_OE_N_FIXED_HIGH"
    text = (output / "forest_guardian_cots_aon_review.kicad_sch").read_text()
    assert "PWR_FLAG" not in text and "TPS62933DRLR" not in text
    assert '(number "VIN"' in text and '(number "VOUT"' in text
    assert '(property "Footprint" ""' in text
    assert '(no_connect (at 53.34 2747.01)' in text
    print("PASS generated candidate: 618 original bindings unchanged; 4 named module terminals + 2 input interface points; EN/OE inhibited")
    if native is not None:
        actual = {}
        root = ET.parse(native / "native.net.xml").getroot()
        for n in root.findall("./nets/net"):
            for p in n.findall("node"):
                key = (p.attrib["ref"], p.attrib["pin"])
                assert key not in actual
                actual[key] = n.attrib["name"].lstrip("/")
        assert actual == mapping, [(k, v, actual.get(k)) for k, v in mapping.items() if actual.get(k) != v][:10]
        erc = json.loads((native / "erc.json").read_text())
        issues = [v for s in erc["sheets"] for v in s["violations"]]
        # Off-board adapter, input protection and return remain UNIMPLEMENTED.
        # This is an exact open-issue register, NOT an ERC clean acceptance.
        assert len(issues) == 2, issues
        assert all(v["type"] == "power_pin_not_driven" and v["severity"] == "error" for v in issues), issues
        print("PASS native netlist matches source; ERC has 2 acknowledged input/return power-source errors; NOT ERC clean")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated", type=Path)
    parser.add_argument("--native", type=Path)
    args = parser.parse_args()
    verify_data()
    if args.native and not args.generated:
        parser.error("--native requires --generated")
    if args.generated:
        verify_generated(args.generated, args.native)
