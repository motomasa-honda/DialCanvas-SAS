#!/usr/bin/env python3
"""Validate full coverage of 48 scoped workflows and intentional full-suite trigger.

This validates CI route wiring, not application safety or manufacturing release.
"""
from pathlib import Path
import re

BASE=Path(__file__).resolve().parents[2]
DIR=BASE/".github"/"workflows"
BRANCH="review/forest-guardian-phase66-idf"
MARKER="execution/ci/full-regression.marker"
SELF="ci-scope-gate.yml"
DESK="desk-redesign.yml"

def header(path):
    data=path.read_text(encoding="utf-8")
    m=re.search(r"(?m)^permissions:\s*$",data)
    assert m is not None, f"{path.name}: permissions block absent"
    return data[:m.start()]

def main():
    workflows=sorted(DIR.glob("*.yml"))
    assert (BASE/MARKER).is_file()
    assert len(workflows)>=49, f"original 48 workflows plus CI gate expected, got {len(workflows)}"
    # The approved desk redesign has its own main-targeted CI. Keep it out of
    # the legacy review-branch router below, which serves the historical
    # phase66 workflows only.
    scoped=[p for p in workflows if p.name not in {SELF,DESK}]
    assert len(scoped)>=48
    for p in scoped:
        h=header(p)
        assert re.search(r"(?m)^on:\s*$",h),p
        assert re.search(r"(?m)^  push:\s*$",h),p
        assert re.search(r"(?m)^    branches:\s*$",h),p
        assert "      - '"+BRANCH+"'\n" in h,p
        assert "    paths:\n" in h,p
        assert "      - '"+MARKER+"'\n" in h,p
        assert ("      - '"+p.as_posix().split(str(BASE)+"/")[-1]+"'\n") in h,p
        assert re.search(r"(?m)^  workflow_dispatch:\s*$",h),p
        # Feature PRs MUST target the long-lived review branch; only
        # their THREE-DOT change set (not accumulated main PR) is considered.
        assert re.search(r"(?m)^  pull_request:\s*$",h),p
        assert h.count("      - '"+BRANCH+"'\n")==2,p
        assert h.count("      - '"+MARKER+"'\n")==2,p
        assert not re.search(r"(?m)^    paths-ignore:\s*$",h),p
    gate=header(DIR/SELF)
    assert re.search(r"(?m)^  pull_request:\s*$",gate)
    assert re.search(r"(?m)^  push:\s*$",gate)
    desk=header(DIR/DESK)
    assert re.search(r"(?m)^  pull_request:\s*$",desk)
    assert re.search(r"(?m)^    branches: \[main\]\s*$",desk)
    assert re.search(r"(?m)^  push:\s*$",desk)
    assert re.search(r"(?m)^    branches: \[main\]\s*$",desk)
    assert re.search(r"(?m)^  workflow_dispatch:\s*$",desk)
    assert '      - "firmware/cots_clock_core/**"\n' in desk
    assert '      - "firmware/cots_clock_app/**"\n' in desk
    assert '      - "docs/**"\n' in desk
    assert (BASE/"execution"/"preflight.py").is_file()
    assert (BASE/"tests"/"check_design.py").is_file()
    print(f"PASS CI routing: {len(scoped)} scoped feature-PR+native-push checks; marker triggers ALL in a feature PR; lightweight main/feature PR gate")
    print("HOLD: branch protection rules not available for inspection; no manufacturing/power release; explicit full marker when finishing task")

if __name__=="__main__":
    main()
