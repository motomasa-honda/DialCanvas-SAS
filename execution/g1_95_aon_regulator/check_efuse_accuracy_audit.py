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
    setpoints = d["datasheet_guaranteed_setpoints"]
    assert setpoints["source_locator"].startswith("TI TPS25947 Rev.C, Table 6-5")
    assert setpoints["limits_are_table_values_not_interpolated"] is True
    rows = setpoints["rows"]
    assert [row["r_ilm_ohm"] for row in rows] == [6650, 3320, 1650, 750, 549]
    assert [(row["min_a"], row["typ_a"], row["max_a"]) for row in rows] == [
        (0.425, 0.500, 0.575), (0.850, 1.007, 1.150),
        (1.800, 2.028, 2.200), (3.960, 4.452, 4.840),
        (5.400, 6.068, 6.600),
    ]
    assert all(row["min_a"] <= row["typ_a"] <= row["max_a"] for row in rows)
    assert setpoints["current_design_r_ilm_is_an_exact_table_setpoint"] is False
    assert setpoints["current_design_guaranteed_min_a"] is None
    assert d["design_value_r_ilm_ohm"] == 2210
    assert round(3334 / 2210, 6) == d["design_equation_typical_a_not_guaranteed"]
    assert d["design_guaranteed_min_a"] is None
    assert d["disposition"] == "HOLD_TPS259474_MINIMUM_CURRENT_UNRESOLVED"
    assert d["safety"]["motor_power_enabled"] is False
    assert d["safety"]["hardware_release"] is False
    assert d["safety"]["manufacturer_release_gates_closed"] == 0


if __name__ == "__main__":
    verify()
    print("PASS: all 5 TI Rev.C guaranteed setpoint rows checked; no interpolation inferred")
    print("PASS: TI source discrepancy reproduced; current 2.21kΩ guaranteed minimum remains unknown")
