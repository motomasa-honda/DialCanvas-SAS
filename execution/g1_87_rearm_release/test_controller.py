import random,unittest
from controller import Latches,step
class Tests(unittest.TestCase):
 def test_held_clear_across_fault_recovery_never_rearms(self):
  s=Latches(False,True)
  for healthy in [False]*20+[True]*100:
   s=step(s,healthy,True)
   self.assertTrue(s.fault)
   self.assertFalse(s.release_seen)
 def test_release_then_new_press_clears(self):
  s=step(Latches(False,True),False,True)
  for _ in range(5):s=step(s,True,True)
  self.assertTrue(s.fault)
  s=step(s,True,False);self.assertTrue(s.fault);self.assertTrue(s.release_seen)
  s=step(s,True,True);self.assertFalse(s.fault)
 def test_trip_interrupts_held_clear_after_reset(self):
  s=step(Latches(True,True),True,True)
  self.assertFalse(s.fault)
  s=step(s,False,True);self.assertTrue(s.fault);self.assertFalse(s.release_seen)
  s=step(s,True,True);self.assertTrue(s.fault)
 def test_fresh_boot_requires_release_and_press(self):
  s=Latches()
  self.assertTrue(step(s,True,True).fault)
  s=step(s,True,False)
  self.assertFalse(step(s,True,True).fault)
 def test_all_16_single_step_truth_cases(self):
  for f in (True,False):
   for r in (True,False):
    for healthy in (True,False):
     for press in (True,False):
      x=step(Latches(f,r),healthy,press)
      expect_rel=False if not healthy else (True if not press else r)
      expect_fault=True if not healthy else (False if press and expect_rel else f)
      self.assertEqual(x,Latches(expect_fault,expect_rel))
 def test_100k_seeded_transitions(self):
  rng=random.Random(871234);s=Latches()
  for _ in range(100000):
   old=s;ok=bool(rng.getrandbits(1));press=bool(rng.getrandbits(1))
   s=step(s,ok,press)
   if not ok:self.assertEqual(s,Latches(True,False))
   if not old.release_seen and press:self.assertFalse(s.release_seen)
 def test_after_trip_no_software_to_disable_motors(self):
  s=Latches();s=step(s,False,True)
  self.assertEqual(s,Latches(True,False))
if __name__=="__main__":unittest.main()
