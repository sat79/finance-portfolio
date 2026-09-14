from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import btc_round2 as b
import research as m

class BTCRoundTests(unittest.TestCase):
    def frame(self, close):
        c=pd.Series(close,dtype=float)
        return pd.DataFrame({"open":c,"high":c+.2,"low":c-.2,"close":c,
                             "atr":1.,"ma21":c.rolling(21).mean()})
    def test_breakout_from_compressed_range(self):
        f=self.frame([100.]*180)
        f["high"]=105.
        f["low"]=95.
        f.loc[145:,"high"]=101.
        f.loc[145:,"low"]=99.
        f.loc[179,["open","high","low","close"]]=[100.,104.,100.,103.]
        signal,_,_=b.raw_rule(f,"E",pd.Series(True,index=f.index))
        self.assertTrue(signal.iloc[-1])
        f.loc[179,"close"]=100.
        self.assertFalse(b.raw_rule(f,"E",pd.Series(True,index=f.index))[0].iloc[-1])
    def test_support_sweep_requires_reclaim(self):
        f=self.frame([110-i*.1 for i in range(50)])
        f.loc[49,["open","high","low","close"]]=[105.05,105.27,104.5,105.25]
        signal,_,_=b.raw_rule(f,"F",pd.Series(True,index=f.index))
        self.assertTrue(signal.iloc[-1])
        f.loc[49,"close"]=104.6
        self.assertFalse(b.raw_rule(f,"F",pd.Series(True,index=f.index))[0].iloc[-1])
    def test_oversold_rebound_is_a_cross(self):
        f=self.frame([100,99,98,97,96,97,98])
        signal,_,_=b.raw_rule(f,"G",pd.Series(True,index=f.index))
        self.assertTrue(signal.iloc[-2])
        self.assertFalse(signal.iloc[-1])
    def test_rsi_gap_resets_warmup(self):
        result=b.rsi(pd.Series([100,99,98,np.nan,97,96,95]),2)
        self.assertTrue(np.isnan(result.iloc[5]))
        self.assertEqual(result.iloc[6],0)
    def test_future_prices_cannot_change_completed_entries(self):
        index=pd.date_range("2020-01-01",periods=120000,freq="5min",tz="UTC")
        rng=np.random.default_rng(81)
        c=100+np.cumsum(rng.normal(.001,.03,len(index)))
        frame=pd.DataFrame({"open":c,"high":c+.1,"low":c-.1,"close":c},index=index)
        before=b.prepare(frame)
        frame.iloc[90000:]*=2
        after=b.prepare(frame)
        for name in before:
            np.testing.assert_array_equal(before[name]["signal"][:90000],after[name]["signal"][:90000])
            np.testing.assert_allclose(before[name]["structure"][:90000],after[name]["structure"][:90000],equal_nan=True)
    def test_selection_uses_only_eligible_training_rows(self):
        features={c["name"]:{"config":c} for c in b.CONFIGS}
        rows=[{"family":"E","config":"E-1h-2R","trades":29,"total_return_pct":100,
               "profit_factor":4,"gap_affected_positions":0},
              {"family":"E","config":"E-1h-3R","trades":30,"total_return_pct":2,
               "profit_factor":1.2,"gap_affected_positions":0}]
        chosen=b.select(rows,features)
        self.assertEqual(chosen[0][1]["config"]["name"],"E-1h-3R")
        rows[1]["gap_affected_positions"]=1
        self.assertEqual(b.select(rows,features),[])
    def test_explicit_stop_multiple(self):
        index=pd.date_range("2024-01-01",periods=3,freq="5min",tz="UTC")
        market=pd.DataFrame({"open":100.,"high":101.,"low":99.,"close":100.},index=index)
        f={"signal":np.array([False,True,False]),"exit":np.zeros(3,bool),"atr":np.ones(3),
           "structure":np.full(3,99.75),"daily_high":np.full(3,np.nan),
           "config":{"name":"override","kind":"B","tf":"1h","rr":3,"atr_multiple":.5,"holding_days":1}}
        _,trades,_=m.simulate({"BTCUSDT":market},[("BTCUSDT",f)],index[0],index[-1]+pd.Timedelta(minutes=5))
        self.assertAlmostEqual(trades[0]["initial_stop"],trades[0]["entry_price"]-.5)
    def test_explicit_holding_limit(self):
        index=pd.date_range("2024-01-01",periods=300,freq="5min",tz="UTC")
        market=pd.DataFrame({"open":100.,"high":101.,"low":99.,"close":100.},index=index)
        signal=np.zeros(300,bool);signal[1]=True
        f={"signal":signal,"exit":np.zeros(300,bool),"atr":np.ones(300),
           "structure":np.full(300,98.),"daily_high":np.full(300,np.nan),
           "config":{"name":"override","kind":"B","tf":"4h","rr":3,"holding_days":1}}
        _,trades,_=m.simulate({"BTCUSDT":market},[("BTCUSDT",f)],index[0],index[-1]+pd.Timedelta(minutes=5))
        self.assertEqual(trades[0]["fills"][-1]["reason"],"rule_or_time")
        self.assertEqual(pd.Timestamp(trades[0]["exit_time"]),index[1]+pd.Timedelta(days=1))
    def test_empty_bootstrap_is_explicit(self):
        result=b.bootstrap([],pd.Timestamp("2020-01-01",tz="UTC"),pd.Timestamp("2020-04-01",tz="UTC"),20)
        self.assertEqual(result["mean_net_r_block_95"],[None,None])
        self.assertEqual(result["bootstrap_pf_undefined_draws"],20)

if __name__=="__main__":
    unittest.main()
