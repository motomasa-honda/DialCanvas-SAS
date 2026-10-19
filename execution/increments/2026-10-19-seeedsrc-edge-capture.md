# Seeed driver PCB edge-window screen

- Work IDs: G4-04 / FG-026. Evidence increment only; status remains OPEN.
- Completion condition: inspect source-derived component/copper geometry and identify possible edge-lip contact regions without claiming a completed retainer.
- Implementation files: `execution/g4_04_seeed_105990072/check_board_edge_capture.py`, `test_board_edge_capture.py`, `BOARD_EDGE_CAPTURE_REVIEW.scad`, generated `board_edge_capture_screen.json`, README, and mandatory `execution/preflight.py` checks.
- Result: two candidate windows on the nominal 35.0 × 19.3 mm board clear EAGLE tPlace line/circle proxies and pad/SMD copper bounds by 0.30 mm in plan. A regression injects an overlap and verifies rejection, then verifies a clear case. Source package outlines are only body proxies, not 3D courtyards.
- Verification: edge screen PASS; collision regression PASS; vendor EAGLE source parser PASS; motor plate screen PASS; OpenSCAD CGAL overlay PASS (40 vertices, 24 facets); mandatory preflight 42/42 PASS; `tests/check_design.py` PASS; stable task-ID checks and `git diff --check` PASS.
- Implementation commit: `a74e73da45362330bae54dd244d3cf11182bcf91`.
- Remaining: PCB thickness and revision, solder and full 3D heights, retaining material/spring force, tolerance/process, insertion/removal path, cable exit, tool access, motor/driver Z-stack and D7 55 mm extraction sweep are not verified. No clip is dimensioned or released.
- Downstream effect: this narrows possible contact regions for a later reversible holder design. It does not close G4-04 or FG-026, does not advance scoped count (22/48), and does not close a manufacturing gate (0/6). G3-08 remains HARDWARE_WAIT. No purchase, machining, power-up, or release.
