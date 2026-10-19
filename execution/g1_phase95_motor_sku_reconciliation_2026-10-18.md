# G1-95 — Motor/driver SKU identity disposition

Date: 2026-10-18
Status: PARTIAL CORRECTION — driver-board identity distinguished from motor; actual motor selection remains blocked. Not a hardware acceptance.

## Established evidence
- `MTR-09-024` and `MTR-09-004` are ElectroPeak seller SKUs for distinct ULN2003 stepper-driver boards, not motor identifiers. The source M1-02 SKU/link mismatch is a board variant conflict. The actual motor SKU/model remains unconfirmed.
- PRs #9–#11 provide evidence-driven acceptance logic but do not supply actual measured motor current or a qualified 5V shared supply.
- Do **not** infer that either board variant is mechanically/electrically suitable from its SKU or seller listing, and do not treat the boards as interchangeable.

## Closure decision
1. Keep both driver boards as *different unverified variants*, not interchangeable approved parts. The M1 named candidate remains MTR-09-024 only as a seller listing; neither board is released.
2. Find the originating manufacturer drawing/datasheet, actual motor label or supplier procurement reference. Record manufacturer, exact motor ordering code, rated voltage, winding configuration, rated/peak/stall current, motor envelope and shaft/gear interface.
3. Cross-check each against the seven-axis driver phase map, power rail and existing mechanical envelope. Reject incompatible candidates explicitly.
4. The board listing mismatch is corrected, but actual motor manufacturer/model and ratings are still a **hard blocking dependency**. No BOM release, current acceptance or electrical re-enable.
5. Once a single part is verified, update the BOM, current-envelope inputs, power/eFuse checks, seven-axis interface, and test evidence **in one scoped change**. Run only the affected motor/current/ledger checks.

## Evidence acceptance checklist
- [ ] Primary source uniquely identifies the chosen motor SKU.
- [ ] Electrical winding/phase topology matches the actual driver interface.
- [ ] Voltage, continuous/starting/stall-current data are traceable, with uncertainty documented.
- [ ] Shaft, mounting and gear geometry are compatible with source CAD.
- [ ] Seven-axis aggregate worst-case power is recomputed from verified inputs.
- [ ] All M1 source SKU/link references are classified as motor vs driver board and reconciled.
- [ ] Review branch tests pass; existing safety HOLD remains until separate physical acceptance.

No checklist item is marked complete by this document. No manufacturing gate or 48-item ledger state is changed.

## External identification search and correction — 2026-10-19

ElectroPeak's two product listings establish only seller catalog identity and nominal board dimensions: MTR-09-024 is a 35×31mm ULN2003 DIP board; MTR-09-004 is a 40×20mm different UL2003 driver board. The MTR-09 codes are therefore not motors. The seller page for its separate MTR-05-008 28BYJ-48 motor mixes 5V/12V variants and conflicting winding resistance/current entries; those values are rejected as a usable electrical specification. The 28BYJ-48 model is only a compatibility candidate mentioned by board listings, not the selected motor.

**Disposition:** driver board listing identities are distinguished, but samples, exact pins, headers and fitted dimensions are unverified. The actual motor manufacturer/model and verified electrical rating remain UNKNOWN. Do not assign motor current from the inconsistent reseller catalog. This is a correction to the identity record, not part qualification or a ledger closure.
