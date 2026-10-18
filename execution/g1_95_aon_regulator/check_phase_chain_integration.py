#!/usr/bin/env python3
"""Check Phase77/78 source terminals survive in the G1-95 648-pad candidate.

This proves source-net-map integration only. It is not ERC, board validation,
electrical safety acceptance, or proof that any motor module is safe to drive.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAP = HERE / "pin_map_648.json"
SOURCES = {
    "B77": (ROOT / "execution/g1_phase77_140pins/nets_140.json", 140),
    "B78": (ROOT / "execution/g1_28phase_disabled/nets_208.json", 208),
}
GLOBAL_NETS = {"GND", "3V3_AON", "5V_MOTOR"}
INTENTIONAL_NC = {
    "ARM_Q_N_UNUSED", "HB_EDGE1_Q_N_UNUSED", "NC_ARM_INV",
    "NC_RELEASE_INV", "NC_SCH", "POR_CT_NC_FIXED_DELAY",
    "RELEASE_Q_N_UNUSED", "RUN_Q_N_UNUSED", "U_5V_CT_NC",
    "U_HB_INV_MANUFACTURER_NC", "WD_ENOUT_NO_CONNECT_PER_TI",
    "UNUSED_U_BUF4_Y5", "UNUSED_U_BUF4_Y6", "UNUSED_U_BUF4_Y7",
    "UNUSED_U_BUF4_Y8",
}


def verify():
    rows = json.loads(MAP.read_text(encoding="utf-8"))
    indexed = {}
    for row in rows:
        key = (row["group"], row["source_ref"], row["source_pin"])
        assert key not in indexed, f"duplicate candidate endpoint: {key}"
        indexed[key] = row

    total = 0
    nc_seen = set()
    for group, (source_path, expected_count) in SOURCES.items():
        data = json.loads(source_path.read_text(encoding="utf-8"))
        expected_net_count = 39 if group == "B77" else 63
        assert len(data["nets"]) == expected_net_count
        expected = {}
        for net, terminals in data["nets"].items():
            for terminal in terminals:
                ref, pin_text = terminal.rsplit(".", 1)
                key = (ref, int(pin_text))
                assert key not in expected, f"duplicate source endpoint: {group} {key}"
                expected[key] = net
        assert len(expected) == expected_count
        actual = {
            (ref, pin): row
            for (row_group, ref, pin), row in indexed.items()
            if row_group == group
        }
        assert set(actual) == set(expected), (
            f"{group} endpoint drift: missing={set(expected)-set(actual)}, "
            f"extra={set(actual)-set(expected)}"
        )
        for (source_ref, source_pin), source_net in expected.items():
            row = actual[(source_ref, source_pin)]
            review_net = row["review_net"]
            if source_net in INTENTIONAL_NC:
                kicad_ref = row["kicad_ref"]
                expected_nc = f"unconnected-({kicad_ref}-P{source_pin}-Pad{source_pin})"
                assert row["source_net"] == expected_nc
                assert review_net == expected_nc, (group, source_ref, source_pin, review_net)
                nc_seen.add(source_net)
            else:
                assert row["source_net"] == source_net
            if source_net in INTENTIONAL_NC:
                continue
            if source_net in GLOBAL_NETS or (group == "B78" and source_net == "VCC_3V3_AON"):
                assert review_net == ("3V3_AON" if source_net in ("3V3_AON", "VCC_3V3_AON") else source_net), (
                    group, source_ref, source_pin, source_net, review_net
                )
            else:
                assert review_net == f"{group}__{source_net}", (
                    group, source_ref, source_pin, source_net, review_net
                )
        total += expected_count

    assert nc_seen == INTENTIONAL_NC, (nc_seen, INTENTIONAL_NC)
    # Trace the release-qualified arm latch through AND gates and the grant
    # resistor chain to EN. This is a source-map path proof, not logic/HIL.
    arm_q = indexed[("B77", "U_ARM", 5)]["review_net"]
    def net(ref, pin):
        found = [r["review_net"] for r in rows
                 if r["kicad_ref"] == ref and r["source_pin"] == pin]
        assert len(found) == 1, (ref, pin, found)
        return found[0]

    path = [
        net("U2", 5), net("U39", 1), net("U39", 4), net("U41", 1),
        net("U41", 4), net("R66", 1), net("R66", 2), net("R68", 1),
        net("R68", 2), net("U14", 1),
    ]
    assert arm_q == path[0] == path[1] == "B77__ARM_LATCH_Q_ISOLATED"
    assert path[2] == path[3] == "B92__ARM_AND_HEALTH"
    assert path[4] == path[5] == "B92__RAIL_GRANT_LOGIC"
    assert path[6] == path[7] == "B92__GRANT_LIMIT_STAGE"
    assert path[8] == path[9] == "B77__U7_EN_CLAMPED_DISABLED"
    efuse_en = next(r["review_net"] for r in rows if r["kicad_ref"] == "U14" and r["source_pin"] == 1)
    assert efuse_en == "B77__U7_EN_CLAMPED_DISABLED"
    assert net("R4", 2) == net("R67", 2) == "GND"
    # The 28 buffer enables must remain on the fail-closed candidate net.
    oe_rows = [r for r in rows if r["group"] == "B78" and r["source_net"] == "PHASE_OE_N_FIXED_HIGH"]
    assert len(oe_rows) == 12
    assert {r["review_net"] for r in oe_rows} == {"B78__PHASE_OE_N_FIXED_HIGH"}
    return {"phase77_terminals": 140, "phase77_nets": 39,
            "phase78_terminals": 208, "phase78_nets": 63,
            "integrated_candidate_terminals": total, "intentional_nc": len(nc_seen),
            "rearm_to_en_logic_path": path, "en_pulldowns_present": True,
            "phase_oe_fail_closed": True,
            "scope": "source pin/net map only; no electrical behavior or HIL proof"}


if __name__ == "__main__":
    print("PASS source-map integration:", json.dumps(verify(), sort_keys=True))
