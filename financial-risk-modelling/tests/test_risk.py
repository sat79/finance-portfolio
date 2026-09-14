import sys,unittest,tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.stats import t
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyse import empirical_risk,student_risk,coverage,simulate_garch,load_prices,backtest,ROOT

class RiskTests(unittest.TestCase):
    def test_fractional_expected_shortfall(self):
        self.assertEqual(empirical_risk([1,2,3,4],.625),(3.,(4+.5*3)/1.5))
    def test_constant_distribution(self):
        self.assertEqual(empirical_risk([2]*10,.99),(2.,2.))
    def test_invalid_inputs(self):
        for x,c in [([], .99),([1,np.nan],.95),([1],1)]:
            with self.assertRaises(ValueError):empirical_risk(x,c)
        with self.assertRaises(ValueError):student_risk(0,1,2,.99)
    def test_student_es_against_integration(self):
        v,e=student_risk(.1,2.,6.,.99);scale=2*np.sqrt(4/6)
        integral=quad(lambda z:(-.1+scale*z)*t.pdf(z,6),t.ppf(.99,6),np.inf)[0]/.01
        self.assertAlmostEqual(e,integral,places=8);self.assertGreater(e,v)
    def test_monte_carlo_one_step(self):
        loss=simulate_garch(.1,.01,.05,.9,6.,4.,horizon=1,paths=300000)
        v,e=empirical_risk(loss,.99);av,ae=student_risk(.1,2.,6.,.99)
        self.assertLess(abs(v-av),.1);self.assertLess(abs(e-ae),.2)
    def test_seed_repeatability(self):
        self.assertTrue(np.array_equal(simulate_garch(0,.1,.1,.8,7,1,paths=100),simulate_garch(0,.1,.1,.8,7,1,paths=100)))
    def test_coverage_edges(self):
        z=coverage(np.zeros(100),np.ones(100),.99)
        self.assertEqual(z['exceptions'],0);self.assertIsNone(z['independence_p']);self.assertTrue(np.isfinite(z['kupiec_p']))
    def test_transition_counts(self):
        z=coverage([0,2,2,0],[1]*4,.95);self.assertEqual(z['transitions'],[[0,1],[1,1]])
    def test_loader_rejects_duplicate_and_negative(self):
        p=load_prices(ROOT/'data/sp500.csv')
        with tempfile.TemporaryDirectory() as d:
            df=p.reset_index();df.columns=['date','adjusted_close'];df.loc[1,'date']=df.loc[0,'date'];path=Path(d)/'bad.csv';df.to_csv(path,index=False)
            with self.assertRaises(ValueError):load_prices(path)
    def test_future_perturbation_does_not_change_forecasts(self):
        p=load_prices(ROOT/'data/sp500.csv');r=(100*np.log(p/p.shift())).dropna().iloc[:1020]
        original,_=backtest(r);changed=r.copy();changed.iloc[-1]+=10;revised,_=backtest(changed)
        pd.testing.assert_frame_equal(original[['date','var','es']],revised[['date','var','es']])
    def test_garch_forecast_matches_library(self):
        from arch import arch_model
        p=load_prices(ROOT/'data/sp500.csv');r=(100*np.log(p/p.shift())).dropna().iloc[:1001]
        bt,_=backtest(r);f=arch_model(r.iloc[:1000],mean='Constant',p=1,q=1,dist='t',rescale=False).fit(disp='off')
        sigma=np.sqrt(f.forecast(horizon=1,reindex=False).variance.iloc[-1,0])
        expected=student_risk(f.params['mu'],sigma,f.params['nu'],.99)[0]
        actual=bt[(bt.model=='GARCH-t 1000d')&(bt.confidence==.99)]['var'].iloc[0]
        self.assertAlmostEqual(actual,expected,places=7)
if __name__=='__main__':unittest.main()
