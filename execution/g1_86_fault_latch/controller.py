"""Ideal gate-settled NOR latch, NOT a transistor timing/eFuse simulation."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Latch:
    fault: bool=True
def step(state, qual_clr_n, clear_request):
    s=not qual_clr_n
    r=bool(clear_request and qual_clr_n)
    assert not(s and r)
    q=True if s else (False if r else state.fault)
    qb=not q
    assert q== (not(r or qb)) and qb==(not(s or q))
    return Latch(q)
