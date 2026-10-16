import unittest,random
from controller import Latch,step
class Tests(unittest.TestCase):
 def test_fault_always_wins(self):
  for old in [True,False]:
   for reset in [True,False]:
    self.assertTrue(step(Latch(old),False,reset).fault)
 def test_recovery_does_not_clear(self):
  s=step(Latch(False),False,False)
  for _ in range(100):s=step(s,True,False);self.assertTrue(s.fault)
 def test_explicit_clear(self):
  self.assertFalse(step(Latch(True),True,True).fault)
 def test_single_step_truth_table(self):
  for old in [False,True]:
   for healthy in [False,True]:
    for clear in [False,True]:
     self.assertEqual(step(Latch(old),healthy,clear).fault,not healthy or (not clear and old))
 def test_random_100k(self):
  rnd=random.Random(861);s=Latch()
  for _ in range(100000):
   healthy=bool(rnd.getrandbits(1));clear=bool(rnd.getrandbits(1))
   s=step(s,healthy,clear)
   if not healthy:self.assertTrue(s.fault)
 def test_unsafe_held_reset_at_recovery_demonstrated(self):
  s=step(Latch(False),False,True);self.assertTrue(s.fault)
  self.assertFalse(step(s,True,True).fault)
 def test_common_mode_qual_stuck_high_undetectable(self):
  s=step(Latch(True),True,True)
  self.assertFalse(step(s,True,False).fault)
if __name__=="__main__":unittest.main()
