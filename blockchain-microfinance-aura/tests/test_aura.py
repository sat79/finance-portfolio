import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyse import weighted_scores,bass
class AuraTests(unittest.TestCase):
    def test_equal_weights_equal_sum(self):
        self.assertAlmostEqual(weighted_scores([[19.8,17.8,20.5,21.3]],[.25]*4)[0],79.4)
    def test_corner_weight(self):
        self.assertEqual(weighted_scores([[10,20,15,5]],[1,0,0,0])[0],40)
    def test_invalid_score_and_weight(self):
        for s,w in [([[26,0,0,0]],[.25]*4),([[1,2,3,4]],[1]*4)]:
            with self.assertRaises(ValueError):weighted_scores(s,w)
    def test_bass_limits(self):
        self.assertEqual(bass(0,.01,.3,.5),0);self.assertAlmostEqual(bass(1000,.01,.3,.5),.5)
        self.assertTrue((np.diff(bass(np.arange(21),.01,.3,.5))>0).all())
    def test_innovation_only_solution(self):
        self.assertAlmostEqual(bass(5,.02,0,.6),.6*(1-np.exp(-.1)))
if __name__=='__main__':unittest.main()
