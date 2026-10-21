#!/usr/bin/env python3
"""Phase 0 design-document consistency checks; Python standard library only."""

from __future__ import annotations

import json
import csv
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "docs/01-requirements/requirements.yaml"
OQ_FILE = ROOT / "docs/01-requirements/open-questions.md"
RTM_FILE = ROOT / "docs/09-verification/traceability.md"
VALID_STATES = {"FIXED", "PROVISIONAL", "OPEN", "REJECTED", "SUPERSEDED"}
ACTIVE_STATES = {"FIXED", "PROVISIONAL", "OPEN"}
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def check_requirements() -> None:
    # JSON syntax is intentionally used as a YAML 1.2 subset.
    data = json.loads(REQ_FILE.read_text(encoding="utf-8"))
    requirements = data["requirements"]
    cases = data["verification_cases"]
    ids = [row["id"] for row in requirements]
    case_ids = [row["id"] for row in cases]
    for duplicate in duplicates(ids):
        fail(f"重複要求 ID: {duplicate}")
    for duplicate in duplicates(case_ids):
        fail(f"重複検証 ID: {duplicate}")
    if not all(re.fullmatch(r"FG-\d{3}", item) for item in ids):
        fail("要求 ID の形式が不正")
    if not all(re.fullmatch(r"V-\d{2}", item) for item in case_ids):
        fail("検証 ID の形式が不正")

    known_ids = set(ids)
    known_cases = set(case_ids)
    expected_questions: dict[str, str] = {}
    expected_pairs: set[tuple[str, str]] = set()
    for row in requirements:
        rid = row["id"]
        state = row["status"]
        if state not in VALID_STATES:
            fail(f"{rid}: 不正な状態 {state}")
        linked = row.get("verification", [])
        if not isinstance(linked, list):
            fail(f"{rid}: verification はリストが必要")
            continue
        if state in ACTIVE_STATES and not linked:
            fail(f"{rid}: 有効要求に検証項目がない")
        if state not in ACTIVE_STATES and linked:
            fail(f"{rid}: 非有効要求に検証項目がある")
        for case_id in linked:
            if case_id not in known_cases:
                fail(f"{rid}: 存在しない検証 ID {case_id}")
            expected_pairs.add((case_id, rid))
        question = row.get("open_question")
        if state == "OPEN":
            if not question:
                fail(f"{rid}: OPEN に未決定事項 ID がない")
            elif question in expected_questions:
                fail(f"未決定事項 ID 重複: {question}")
            else:
                expected_questions[question] = rid
        elif question:
            fail(f"{rid}: OPEN 以外に未決定事項 ID がある")
        if state == "SUPERSEDED" and row.get("superseded_by") not in known_ids:
            fail(f"{rid}: 置換先 ID がない")

    questions_text = OQ_FILE.read_text(encoding="utf-8")
    actual_questions = re.findall(r"^\|\s*(OQ-\d+)\s*\|\s*(FG-\d{3})\s*\|", questions_text, re.M)
    for duplicate in duplicates([qid for qid, _ in actual_questions]):
        fail(f"未決定事項表の ID 重複: {duplicate}")
    if dict(actual_questions) != expected_questions:
        fail("未決定事項表と OPEN 要求の対応が不一致")

    trace_text = RTM_FILE.read_text(encoding="utf-8")
    actual_pairs: set[tuple[str, str]] = set()
    for case_id, cell in re.findall(r"^\|\s*(V-\d{2})\s*\|\s*([^|]+)\|", trace_text, re.M):
        for start, end in re.findall(r"FG-(\d{3})(?:〜FG-(\d{3}))?", cell):
            first = int(start)
            last = int(end) if end else first
            if last < first:
                fail(f"{case_id}: 逆順の要求範囲")
            for number in range(first, last + 1):
                actual_pairs.add((case_id, f"FG-{number:03d}"))
    missing = expected_pairs - actual_pairs
    extra = actual_pairs - expected_pairs
    if missing:
        fail(f"対応表にない要求・検証: {sorted(missing)}")
    if extra:
        fail(f"対応表に余分な要求・検証: {sorted(extra)}")


def check_adr() -> None:
    numbers: list[str] = []
    for path in (ROOT / "adr").glob("[0-9][0-9][0-9][0-9]-*.md"):
        number = path.name[:4]
        numbers.append(number)
        heading = re.search(r"^# ADR-(\d{4}):", path.read_text(encoding="utf-8"), re.M)
        if not heading or heading.group(1) != number:
            fail(f"ADR 番号と見出しが不一致: {path.relative_to(ROOT)}")
    for duplicate in duplicates(numbers):
        fail(f"ADR 番号重複: {duplicate}")


def check_requirement_migration() -> None:
    migration_file = ROOT / "docs/10-desk-redesign/requirements-migration-v0.8-to-v0.20.csv"
    data = json.loads(REQ_FILE.read_text(encoding="utf-8"))
    current = {row["id"]: row for row in data["requirements"]}
    try:
        with migration_file.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        fail(f"要求移行表を読めない: {exc}")
        return

    legacy_ids = [row.get("LegacyID", "") for row in rows if row.get("LegacyID")]
    expected_legacy_ids = [f"FG-{number:03d}" for number in range(1, 44)]
    if sorted(legacy_ids) != expected_legacy_ids:
        fail("旧v0.8要求FG-001〜FG-043の移行表が不足または重複")

    mapped_current_ids: list[str] = []
    allowed_dispositions = {"継承", "具体化", "置換", "履歴維持", "追加"}
    for row in rows:
        current_id = row.get("CurrentID", "")
        mapped_current_ids.append(current_id)
        if current_id not in current:
            fail(f"要求移行表の存在しない現行ID: {current_id}")
            continue
        if row.get("CurrentStatus") != current[current_id]["status"]:
            fail(f"要求移行表の状態不一致: {current_id}")
        if row.get("Disposition") not in allowed_dispositions:
            fail(f"要求移行表の処置が不正: {current_id}")
        if row.get("LegacyID"):
            if row.get("LegacyBaseline") != "v0.8@40db883":
                fail(f"旧要求の基準点が不正: {row.get('LegacyID')}")
            if row.get("Disposition") == "追加":
                fail(f"旧要求の行が追加扱い: {row.get('LegacyID')}")
        elif row.get("Disposition") != "追加":
            fail(f"旧要求のない現行行が追加扱いでない: {current_id}")

    if sorted(mapped_current_ids) != sorted(current):
        fail("要求移行表と現行台帳のID対応が一対一でない")
def check_markdown_links() -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content):
            target = target.strip().split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://|^mailto:", target):
                continue
            linked = (path.parent / unquote(target)).resolve()
            if not linked.is_relative_to(ROOT) or not linked.exists():
                fail(f"リンク切れ: {path.relative_to(ROOT)} -> {target}")


def main() -> int:
    check_requirements()
    check_adr()
    check_requirement_migration()
    check_markdown_links()
    if errors:
        for item in errors:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print("OK: Markdown リンク、要求 ID/状態、ADR、未決定事項、要求移行表、検証対応")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
