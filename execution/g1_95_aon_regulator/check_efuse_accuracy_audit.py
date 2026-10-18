#!/usr/bin/env python3
"""Reproduce the TPS259474 accuracy discrepancy without inventing a limit."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "efuse_accuracy_audit.json").read_text(encoding="utf-8"))

def verify():
    assert d["sku"] == "TPS259474LRPW"
    assert d["sources"]["ti_datasheet_rev_c"] == "https://www.ti.com/lit/ds/symlink/tps25947.pdf"
    table = d["datasheet_electrical_characteristics"]
    nominal = table["equation_constant_ohm_amp"] / table["r_ilm_ohm"]
    deviation = 100 * (table["table_min_limit_a"] / nominal - 1)
    assert round(nominal, 6) == table["equation_nominal_limit_a"]
    assert round(deviation, 2) == table["min_deviation_from_equation_percent"]
    assert abs(deviation + 15.36) < 0.02
    assert d["design_value_r_ilm_ohm"] == 2210
    assert round(3334 / 2210, 6) == d["design_equation_typical_a_not_guaranteed"]
    assert d["design_guaranteed_min_a"] is None
    assert d["disposition"] == "HOLD_TPS259474_MINIMUM_CURRENT_UNRESOLVED"
    assert d["safety"]["motor_power_enabled"] is False
    assert d["safety"]["hardware_release"] is False
    assert d["safety"]["manufacturer_release_gates_closed"] == 0


if __name__ == "__main__":
    verify()
    print("PASS: TI source discrepancy reproduced; no guaranteed minimum inferred")
