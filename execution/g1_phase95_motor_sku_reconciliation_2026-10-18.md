# G1-95 — Motor SKU discrepancy disposition

Date: 2026-10-18
Status: BLOCKED — source discrepancy unresolved; not a hardware acceptance.

## Established evidence
- PR #12 explicitly reports conflicting motor identifiers `MTR-09-024` and `MTR-09-004`, and a 16-case current-sizing study with assumptions.
- PRs #9–#11 provide evidence-driven acceptance logic but do not supply actual measured motor current or a qualified 5V shared supply.
- Do **not** infer that either SKU is correct from its suffix or silently substitute one for the other.

## Closure decision
1. Keep both identifiers as *unverified alternatives*, not interchangeable approved parts.
2. Find the originating manufacturer drawing/datasheet, motor label or purchasing reference for each. Record manufacturer, exact ordering code, rated voltage, phase/winding configuration, rated/peak/stall current, mechanical envelope, shaft/gear interface, and primary-source URL or artifact hash.
3. Cross-check each against the seven-axis driver phase map, power rail and existing mechanical envelope. Reject incompatible candidates explicitly.
4. If no primary-source confirmation exists, retain the conflict as a **hard blocking dependency**. No BOM release, current acceptance or electrical re-enable.
5. Once a single part is verified, update the BOM, current-envelope inputs, power/eFuse checks, seven-axis interface, and test evidence **in one scoped change**. Run only the affected motor/current/ledger checks.

## Evidence acceptance checklist
- [ ] Primary source uniquely identifies the chosen motor SKU.
- [ ] Electrical winding/phase topology matches the actual driver interface.
- [ ] Voltage, continuous/starting/stall-current data are traceable, with uncertainty documented.
- [ ] Shaft, mounting and gear geometry are compatible with source CAD.
- [ ] Seven-axis aggregate worst-case power is recomputed from verified inputs.
- [ ] All stale references to the rejected SKU are identified and dispositioned.
- [ ] Review branch tests pass; existing safety HOLD remains until separate physical acceptance.

No checklist item is marked complete by this document. No manufacturing gate or 48-item ledger state is changed.
