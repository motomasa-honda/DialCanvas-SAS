import itertools
import random
import unittest
from dataclasses import replace
from controller import Inputs, Mode, State, advance, requests


GOOD = Inputs(True, True, True, True, False, False, False)


def boot_to_start():
    s = advance(State(), GOOD)  # observed release
    assert s.mode is Mode.READY
    s = advance(s, replace(GOOD, rearm_pressed=True))
    assert s.mode is Mode.STARTING
    return s


def boot_to_run():
    s = boot_to_start()
    return advance(s, replace(GOOD, rearm_pressed=True,
                              efuse_pg_high=True, motor_rail_valid=True),
                   elapsed_ms=20)


class G180Tests(unittest.TestCase):
    def test_boot_rearm_held_never_enables(self):
        s = State()
        for _ in range(100):
            i = replace(GOOD, rearm_pressed=True)
            s = advance(s, i, 500)
            self.assertFalse(requests(s, i).rail_enable)

    def test_boot_then_release_press(self):
        self.assertEqual(advance(State(), GOOD).mode, Mode.READY)
        self.assertEqual(boot_to_start().mode, Mode.STARTING)

    def test_rail_can_start_without_pg(self):
        s = boot_to_start()
        r = requests(s, replace(GOOD, rearm_pressed=True))
        self.assertTrue(r.rail_enable)
        self.assertFalse(r.phases_enable)

    def test_startup_pending_waits_for_both_senses_and_stability(self):
        s = boot_to_start()
        for _ in range(4):
            s = advance(s, replace(GOOD, rearm_pressed=True,
                                   efuse_pg_high=True, motor_rail_valid=False), 50)
            self.assertEqual(s.mode, Mode.STARTING)
            self.assertFalse(requests(s, GOOD).phases_enable)
        s = advance(s, replace(GOOD, rearm_pressed=True,
                               efuse_pg_high=True, motor_rail_valid=True), 19)
        self.assertEqual(s.mode, Mode.STARTING)
        s = advance(s, replace(GOOD, rearm_pressed=True,
                               efuse_pg_high=True, motor_rail_valid=True), 1)
        self.assertEqual(s.mode, Mode.RUN)

    def test_startup_timeout_latches_when_pg_is_off(self):
        s = advance(boot_to_start(), GOOD, 500)
        self.assertEqual(s.mode, Mode.FAULT)
        self.assertEqual(s.fault_reason, "STARTUP_TIMEOUT")
        self.assertFalse(requests(s, GOOD).rail_enable)

    def test_startup_timeout_latches_when_pg_falsely_high(self):
        s = advance(boot_to_start(), replace(GOOD, efuse_pg_high=True), 500)
        self.assertEqual(s.mode, Mode.FAULT)

    def test_run_qualified_and_faults_latch(self):
        s = boot_to_run()
        self.assertEqual(s.mode, Mode.RUN)
        good_run = replace(GOOD, efuse_pg_high=True, motor_rail_valid=True)
        self.assertTrue(requests(s, good_run).phases_enable)
        for field in ("raw_motor_supply_ok", "stop_channels_ok", "watchdog_ok",
                      "efuse_pg_high", "motor_rail_valid"):
            bad = replace(good_run, **{field: False})
            tripped = advance(s, bad)
            self.assertEqual(tripped.mode, Mode.FAULT, field)
            self.assertFalse(requests(tripped, good_run).phases_enable, field)
            self.assertFalse(requests(s, bad).phases_enable, field)
            self.assertEqual(advance(tripped, replace(good_run, rearm_pressed=True)).mode,
                             Mode.FAULT, field)

    def test_fault_requires_fresh_release_then_press(self):
        fault = advance(boot_to_run(), replace(GOOD, efuse_pg_high=False))
        good = replace(GOOD, efuse_pg_high=True, motor_rail_valid=True)
        for _ in range(10):
            fault = advance(fault, replace(good, rearm_pressed=True))
            self.assertEqual(fault.mode, Mode.FAULT)
        s = advance(fault, good)
        self.assertEqual(s.mode, Mode.WAIT_RELEASE)
        self.assertEqual(advance(s, good).mode, Mode.READY)
        self.assertEqual(advance(advance(s, good), replace(good, rearm_pressed=True)).mode,
                         Mode.STARTING)

    def test_aon_loss_never_restores_armed_state(self):
        s = boot_to_run()
        s = advance(s, replace(GOOD, aon_ok=False, rearm_pressed=True))
        self.assertEqual(s.mode, Mode.WAIT_RELEASE)
        for _ in range(10):
            s = advance(s, replace(GOOD, rearm_pressed=True))
            self.assertEqual(s.mode, Mode.WAIT_RELEASE)

    def test_hold_stop_works_before_start_and_during_run(self):
        stopped = replace(GOOD, stop_channels_ok=False)
        self.assertEqual(advance(State(), stopped).mode, Mode.WAIT_RELEASE)
        self.assertEqual(advance(boot_to_run(), stopped).mode, Mode.FAULT)

    def test_exhaustive_input_one_step_invariants(self):
        # 5 model modes x all 128 input vectors x 4 representative sample intervals.
        modes = [State(mode=m) for m in Mode]
        for bits in itertools.product((False, True), repeat=7):
            i = Inputs(*bits)
            for state in modes:
                for ms in (0, 1, 20, 500):
                    n = advance(state, i, ms)
                    out = requests(n, i)
                    self.assertFalse(out.phases_enable and not out.rail_enable)
                    if n.mode in (Mode.WAIT_RELEASE, Mode.READY, Mode.FAULT):
                        self.assertFalse(out.rail_enable)
                    if not i.startup_permitted:
                        self.assertFalse(out.rail_enable)
                        self.assertFalse(out.phases_enable)
                    if not i.efuse_pg_high or not i.motor_rail_valid:
                        self.assertFalse(out.phases_enable)

    def test_seeded_50000_transitions_never_break_invariants(self):
        rng = random.Random(80180)
        s = State()
        for _ in range(50000):
            i = Inputs(*(rng.choice([False, True]) for _ in range(7)))
            s = advance(s, i, rng.choice([0, 1, 5, 20, 100, 500]))
            r = requests(s, i)
            self.assertFalse(r.phases_enable and not r.rail_enable)
            if not i.startup_permitted or s.mode in (Mode.WAIT_RELEASE, Mode.READY, Mode.FAULT):
                self.assertFalse(r.rail_enable)

    def test_durations_rejected(self):
        with self.assertRaises(ValueError):
            advance(State(), GOOD, -1)
        with self.assertRaises(ValueError):
            advance(State(), GOOD, 1, startup_deadline_ms=10, rail_stable_ms=20)

    def test_double_sensor_stuck_high_cannot_be_detected_in_ideal_model(self):
        # Demonstrates a still-unqualified common-mode danger.
        both_stuck_high = replace(GOOD, efuse_pg_high=True, motor_rail_valid=True)
        s = advance(boot_to_start(), both_stuck_high, 20)
        self.assertEqual(s.mode, Mode.RUN)  # NOT safety evidence, open HIL blocker


if __name__ == "__main__":
    unittest.main()
