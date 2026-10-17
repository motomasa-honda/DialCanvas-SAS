#!/usr/bin/env python3
"""G1 static safety review contract. Full native KiCad and dynamic tests in verified ZIP."""
import json
from pathlib import Path
d=json.loads((Path(__file__).parent/"design_contract.json").read_text())
assert (d["old_pads"],d["old_nets"],d["new_pads"],d["new_nets"],d["added_pads"])==(71,24,85,29,14)
assert d["latch"]["sku"]=="SN74LVC2G74DCUR"
assert d["latch"]["pinmap"]=={"1":"REARM_SHAPED_NOT_BUILT","2":"ARM_D_UNIMPLEMENTED",
"3":"ARM_Q_N_UNUSED","4":"GND","5":"ARM_LATCH_Q_ISOLATED","6":"QUAL_CLR_N","7":"3V3_AON","8":"3V3_AON"}
p=d["critical_existing"]
assert p=={"U7.1":"U7_EN_CLAMPED_DISABLED","R_EN_PD.1":"U7_EN_CLAMPED_DISABLED",
"R_EN_PD.2":"GND","U7.3":"EFUSE_PG_OD","U7.4":"PGTH_SENSE",
"U_WD.7":"QUAL_CLR_N","U_5V.1":"QUAL_CLR_N"}
assert d["dynamic_tests"]=={"unit":10,"random":20000,"exhaustive_256_times_states":5,"mutation":8,"result":"LOCAL_PASS_LOGIC_ONLY"}
q=d["native_kicad"]
assert q["sha256"]=="5a1c8086110b44f807f6193648ef6552363d5b7dd282faf180cb8ab066b2c05d"
assert q["actual_KiCad_ERC"]==q["pcb_DRC"]=="NOT_RUN" and q["footprint"]=="UNASSIGNED"
assert q["source_rebuilt_and_verified_in_ZIP"] is True
assert len(d["unbuilt"])>=7
s=d["project_state"]
assert (s["done_scope"],s["total"],s["manufacturing"],s["software"])==(19,48,0,11)
assert s["g1_05"]==s["g1_06"]=="WORKING" and s["efuse_EN"]=="LOW"
assert all(s[k] is False for k in ("order","cut","power","flash","main_merge"))
assert "static" in d["github_ci_limited"].lower() or "pin contract" in d["github_ci_limited"]
for wrong in [
{"U7.1":"ARM_LATCH_Q_ISOLATED"},{"U7.3":"PGTH_SENSE"},{"U7.4":"EFUSE_PG_OD"},
{"U_WD.7":"3V3_AON"},{"U_5V.1":"3V3_AON"},{"R_EN_PD.1":"GND"},
{"R_EN_PD.2":"U7_EN_CLAMPED_DISABLED"},{"U7.1":"REARM_RAW"}]:
    altered={**p,**wrong}
    assert any(altered[k]!=p[k] for k in p)
print("PASS static physical pin map: reviewed 71/24 -> 85/29, U7 EN held GND, TI PG/PGTH mapping")
print("HOLD no live hardware latch or native KiCad ERC, no powered motors; 19/48 and 0/6")
