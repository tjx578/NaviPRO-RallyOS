import unittest
from tools.bali_routing.guard import classify_osm_segment,release_decision
class TestBaliGuard(unittest.TestCase):
 def test_no_footway(self):self.assertEqual(classify_osm_segment("footway",{}),"BLOCK_HIGHWAY")
 def test_no_private(self):self.assertEqual(classify_osm_segment("residential",{"access":"private"}),"BLOCK_ACCESS")
 def test_oneway_not_verified_by_filter(self):self.assertEqual(classify_osm_segment("residential",{"oneway":"yes"}),"CANDIDATE_ONLY")
 def test_no_unvalidated_release(self):self.assertEqual(release_decision(["PASS"]*16,True,True),"HOLD")
if __name__=="__main__":unittest.main()
