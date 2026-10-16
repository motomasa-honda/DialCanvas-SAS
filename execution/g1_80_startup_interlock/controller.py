"""G1-80 virtual independent motor rail/phase safety FSM SPECIFICATION ONLY.

No actuator, relay, eFuse, GPIO, KiCad, or attached hardware is controlled.
All power/driver requests are analysis-only signals.
"""
from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    WAIT_RELEASE = "WAIT_RELEASE"
    READY = "READY"
    STARTING = "STARTING"
    RUN = "RUN"
    FAULT = "FAULT"


@dataclass(frozen=True)
class Inputs:
    aon_ok: bool
    raw_motor_supply_ok: bool
    stop_channels_ok: bool  # ASSUMPTION: independent tested NC STOP paths; not wired
    watchdog_ok: bool       # ASSUMPTION: truly active external watchdog; not wired
    rearm_pressed: bool
    efuse_pg_high: bool     # open drain+pullup alone is NOT trustworthy
    motor_rail_valid: bool  # MUST be independent physical threshold monitor, unbuilt

    @property
    def startup_permitted(self):
        return (self.aon_ok and self.raw_motor_supply_ok and
                self.stop_channels_ok and self.watchdog_ok)


@dataclass(frozen=True)
class State:
    mode: Mode = Mode.WAIT_RELEASE
    startup_age_ms: int = 0
    stable_rail_ms: int = 0
    fault_reason: str = ""


@dataclass(frozen=True)
class Requests:
    rail_enable: bool
    phases_enable: bool


def requests(state: State, inputs: Inputs) -> Requests:
    """Virtual requests; existing physical U7.EN and /OE remain DISABLED."""
    health = inputs.startup_permitted
    rail = health and state.mode in (Mode.STARTING, Mode.RUN)
    phases = (health and state.mode == Mode.RUN and
              inputs.efuse_pg_high and inputs.motor_rail_valid)
    return Requests(bool(rail), bool(phases))


def advance(state: State, inputs: Inputs, elapsed_ms: int = 1,
            startup_deadline_ms: int = 500, rail_stable_ms: int = 20) -> State:
    """Synchronous sampled functional requirements, NOT an analog circuit simulation.

    A power-good can be false while eFuse is deliberately off. Therefore
    PG/rail sense are NOT prerequisites for entering STARTING. During STARTING
    phase outputs remain blocked until BOTH independent senses remain good for
    rail_stable_ms. A RUN sense failure latches FAULT immediately per sample.
    """
    if (not isinstance(elapsed_ms, int) or elapsed_ms < 0 or
        not isinstance(startup_deadline_ms, int) or
        not isinstance(rail_stable_ms, int) or
        rail_stable_ms <= 0 or startup_deadline_ms < rail_stable_ms):
        raise ValueError("invalid duration parameters")

    if not inputs.aon_ok:
        # Power-up must NEVER inherit RUN. Full AON outage is NOT persistent
        # memory: it MUST be followed by a new release -> press sequence.
        return State()

    if state.mode == Mode.FAULT:
        # A latched fault survives every recovered signal and held REARM.
        # The release first returns to WAIT_RELEASE, not directly to RUN.
        if not inputs.startup_permitted or inputs.rearm_pressed:
            return state
        return State()

    if not inputs.startup_permitted:
        if state.mode in (Mode.STARTING, Mode.RUN):
            failures = [name for name, healthy in (
                ("RAW_SUPPLY", inputs.raw_motor_supply_ok),
                ("STOP", inputs.stop_channels_ok),
                ("WATCHDOG", inputs.watchdog_ok),
            ) if not healthy]
            return State(mode=Mode.FAULT, fault_reason="|".join(failures))
        return State()  # no automatic arming on stop/watchdog recovery

    if state.mode == Mode.WAIT_RELEASE:
        return State(mode=Mode.READY) if not inputs.rearm_pressed else state

    if state.mode == Mode.READY:
        return State(mode=Mode.STARTING) if inputs.rearm_pressed else state

    if state.mode == Mode.STARTING:
        age = state.startup_age_ms + elapsed_ms
        stable = (state.stable_rail_ms + elapsed_ms
                  if inputs.efuse_pg_high and inputs.motor_rail_valid else 0)
        if stable >= rail_stable_ms and age <= startup_deadline_ms:
            return State(mode=Mode.RUN)
        if age >= startup_deadline_ms:
            return State(mode=Mode.FAULT, fault_reason="STARTUP_TIMEOUT")
        return State(mode=Mode.STARTING, startup_age_ms=age,
                     stable_rail_ms=stable)

    if state.mode == Mode.RUN:
        if not inputs.efuse_pg_high:
            return State(mode=Mode.FAULT, fault_reason="PG_LOST")
        if not inputs.motor_rail_valid:
            return State(mode=Mode.FAULT, fault_reason="RAIL_SENSE_LOST")
        return state

    raise ValueError(f"unexpected state: {state.mode}")
