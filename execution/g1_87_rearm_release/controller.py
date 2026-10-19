"""Boolean settled-state circuit for G1-87, not analog propagation/SPICE.
Release latch SET only after observing released input while healthy; TRIP resets it.
Fault latch TRIP overrides reset; qualified clear requires release latch.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class Latches:
    fault:bool=True
    release_seen:bool=False
def step(state:Latches, healthy:bool, switch_pressed:bool)->Latches:
    trip=not healthy
    clear_not=not switch_pressed
    release_set=healthy and clear_not
    # NOR2 cross-coupling, trip wins and erases release_seen
    release_seen=False if trip else (True if release_set else state.release_seen)
    release_qbar=not release_seen
    assert release_seen==(not(trip or release_qbar))
    assert release_qbar==(not(release_set or release_seen))
    clear_qualified=bool(switch_pressed and release_seen)
    reset_effective=bool(clear_qualified and healthy)
    fault=True if trip else (False if reset_effective else state.fault)
    fault_qbar=not fault
    assert fault==(not(reset_effective or fault_qbar))
    assert fault_qbar==(not(trip or fault))
    return Latches(fault,release_seen)
