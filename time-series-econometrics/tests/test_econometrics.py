import sys,unittest,tempfile
from pathlib import Path
import pandas as pd
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyse import load_data,choose_spec,forecast,evaluate,metrics,ROOT

class EconometricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs=load_data(ROOT/'data/us_macro.csv')[['realgdp','realcons']];cls.train=cls.logs.loc[:'1989Q4'];cls.order,cls.lag,cls.rank,*_=choose_spec(cls.train)
    def test_data_quarters(self):
        self.assertEqual(len(self.logs),203);self.assertEqual(str(self.logs.index[-1]),'2009Q3')
    def test_reject_missing_quarter(self):
        df=pd.read_csv(ROOT/'data/us_macro.csv').drop(index=5)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';df.to_csv(p,index=False)
            with self.assertRaises(ValueError):load_data(p)
    def test_future_perturbation(self):
        a=self.logs.iloc[:len(self.train)+1].copy();b=a.copy();b.iloc[-1,0]+=.1
        ra=evaluate(a,self.order,self.lag,self.rank);rb=evaluate(b,self.order,self.lag,self.rank)
        np.testing.assert_allclose(ra.forecast,rb.forecast,rtol=0,atol=1e-10)
        np.testing.assert_allclose(rb.actual-ra.actual,40.,atol=1e-10)
    def test_baseline_and_intervals(self):
        rows=forecast(self.train,self.order,self.lag,self.rank)
        rw=next(x for x in rows if x['model']=='Random walk');self.assertEqual(rw['forecast'],0)
        mean=next(x for x in rows if x['model']=='Historical mean')
        expected=400*(self.train.realgdp.iloc[-1]-self.train.realgdp.iloc[0])/(len(self.train)-1)
        self.assertAlmostEqual(mean['forecast'],expected)
        for row in rows[:3]:self.assertLess(row['lower'],row['forecast']);self.assertLess(row['forecast'],row['upper'])
    def test_metrics_known_values(self):
        d=pd.DataFrame(dict(split=['test']*2,model=['x']*2,forecast=[1,5],actual=[0,2],lower=[None]*2,upper=[None]*2))
        m=metrics(d)[0];self.assertAlmostEqual(m['rmse'],np.sqrt(5));self.assertEqual(m['mae'],2);self.assertIsNone(m['interval_coverage'])
if __name__=='__main__':unittest.main()
