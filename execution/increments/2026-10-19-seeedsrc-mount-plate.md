# Seeed motor fixing plate: geometry candidate

- Work ID: G4-04 / FG-026; G3-04 motor integration dependency.
- Completion condition for this increment: create a reproducible parametric face-plate candidate and check its hole/slot geometry against the Seeed source drawing and 50 × 41 mm project reservation.
- Artifacts: `execution/g4_04_seeed_105990072/MOTOR_MOUNT_PLATE_CANDIDATE.scad`, `check_mount_candidate.py`, `mount_candidate_screen.json`, and the corresponding README note.
- Candidate dimensions: 48 × 39 mm plate envelope; 35 mm nominal fixing span aligned to 50 mm reservation axis; 4.8 mm slots and 10 mm boss opening. Slot, thickness and material are design-study values only.
- Verification: Python source-dimension contract PASS; full preflight 40/40 PASS; Seeed EAGLE parser PASS; power budget regressions 7/7 PASS; `tests/check_design.py` PASS; OpenSCAD CGAL mesh export PASS (592 vertices, 298 facets, 2 volumes); stable 48-ID check and `git diff --check` PASS. Results establish a geometric candidate only.
- Commit SHA: `584fa5982279fe4ebed00716a89515ed9ca028da`.
- Remaining: inspect exact motor mount flange drawing; select and source-check fastener/washer; receive and measure product; mount the hole-free driver PCB; establish component heights, cable/connector clearance and Z-stack; integrate shaft coupler and gear; rerun the full D7 collision/sweep audit and physical independent-service test.
- Downstream effect: a 48 × 39 mm candidate plate fits inside the already reserved 50 × 41 mm region. It does not solve the motor/driver-board overlapping plan envelopes or prove the 55 mm service path. G4-04 and FG-026 remain OPEN, G3-08 remains HARDWARE_WAIT, task count remains 22/48 and manufacturing gates remain 0/6. No purchase, machining, power, or release authorized.
