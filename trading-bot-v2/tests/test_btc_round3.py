from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import research as m
import btc_round3 as r

class RegimeTests(unittest.TestCase):
    def test_pivot_anchors_need_two_completed_right_bars(self):
        f=pd.DataFrame({"open":100.,"high":101.,"low":99.,"close":100.,"atr":1.},index=range(40))
        f.loc[5,"low"]=90.
        f.loc[12,"high"]=120.
        signal,low,high=r.fib_signals(f)
        self.assertTrue(np.isnan(high[:14]).all())
        self.assertEqual(high[14],120)
        self.assertEqual(low[14],90)
        f.loc[16,["close","high","low"]]=[110,111,100]
        signal,_,_=r.fib_signals(f)
        self.assertTrue(signal[16])
        self.assertFalse(r.fib_signals(f,require_div=True)[0][16])
    def test_uptrend_gate_does_not_consume_blocked_impulse(self):
        f=pd.DataFrame({"open":100.,"high":101.,"low":99.,"close":100.,"atr":1.},index=range(40))
        f.loc[5,"low"]=90;f.loc[12,"high"]=120
        f.loc[16,["close","high","low"]]=[110,111,100]
        allowed=np.ones(40,bool);allowed[16]=False
        self.assertFalse(r.fib_signals(f,allowed=allowed)[0][16])
    def test_breakeven_includes_costs(self):
        p={"entry":100.02,"initial_stop":98.,"stop":98.,"highest":100.02}
        m.adaptive_stop(p,102.1,1.,.001,.0002)
        proceeds=p["stop"]*(1-.0002)*(1-.001)
        self.assertAlmostEqual(proceeds,p["entry"]*(1+.001))
    def test_trail_never_loosens(self):
        p={"entry":100.,"initial_stop":98.,"stop":98.,"highest":100.}
        m.adaptive_stop(p,108.,1.,.001,.0002)
        self.assertEqual(p["stop"],106.)
        m.adaptive_stop(p,107.,4.,.001,.0002)
        self.assertEqual(p["stop"],106.)
    def fixture(self,adaptive=True):
        index=pd.date_range("2024-01-01",periods=5,freq="5min",tz="UTC")
        market=pd.DataFrame({"open":100.,"high":101.,"low":99.,"close":100.},index=index)
        f={"signal":np.array([False,True,False,False,False]),"exit":np.zeros(5,bool),
           "atr":np.ones(5),"structure":np.full(5,98.),"daily_high":np.full(5,np.nan),
           "regime":np.array(["","uptrend","","",""],dtype=object),"mean_exit":np.zeros(5,bool),
           "config":{"name":"test","kind":"B","tf":"1h","rr":3,"adaptive":adaptive}}
        return market,f
    def test_current_unfinished_high_cannot_move_stop(self):
        market,f=self.fixture()
        market.iloc[1]=[100,105,99,104]
        _,trades,_=m.simulate({"BTCUSDT":market},[("BTCUSDT",f)],market.index[0],market.index[-1]+pd.Timedelta(minutes=5))
        self.assertEqual(trades[0]["fills"][-1]["reason"],"boundary")
    def test_regime_change_exits_at_next_event_open(self):
        market,f=self.fixture()
        f["regime"][3]="downtrend"
        _,trades,_=m.simulate({"BTCUSDT":market},[("BTCUSDT",f)],market.index[0],market.index[-1]+pd.Timedelta(minutes=5))
        self.assertEqual(trades[0]["exit_time"],str(market.index[3]))
        self.assertEqual(trades[0]["entry_regime"],"uptrend")
    def test_rising_and_falling_daily_regimes(self):
        index=pd.date_range("2020-01-01",periods=400,freq="1d",tz="UTC")
        def frame(c):
            f=pd.DataFrame({"high":c+.1,"low":c-.1,"close":c,"atr":1.},index=index)
            f["ma200"]=f.close.rolling(200).mean();f["end"]=index.asi8+pd.Timedelta(days=1).value
            return f
        self.assertEqual(r.regimes(frame(np.arange(400)+100.)).regime.iloc[-1],"uptrend")
        self.assertEqual(r.regimes(frame(1000.-np.arange(400))).regime.iloc[-1],"downtrend")
        self.assertEqual(r.regimes(frame(np.full(400,100.))).regime.iloc[-1],"sideways")
    def test_future_prices_do_not_change_past_regimes_or_signals(self):
        index=pd.date_range("2020-01-01",periods=120000,freq="5min",tz="UTC")
        rng=np.random.default_rng(901)
        c=100+np.cumsum(rng.normal(.001,.07,len(index)))
        base=pd.DataFrame({"open":c,"high":c+.1,"low":c-.1,"close":c},index=index)
        first,regime=r.prepare(base)
        base.iloc[90000:]*=2
        second,new_regime=r.prepare(base)
        for name in first:
            np.testing.assert_array_equal(first[name]["signal"][:90000],second[name]["signal"][:90000])
            np.testing.assert_array_equal(first[name]["regime"][:90000],second[name]["regime"][:90000])
            no_entry=np.isin(first[name]["regime"],["downtrend","transition","unknown"])
            self.assertFalse(first[name]["signal"][no_entry].any())
        cutoff=index[90000].value
        mask=regime.end<cutoff
        np.testing.assert_array_equal(regime.regime[mask],new_regime.regime[mask])
    def test_daily_benchmark_does_not_replace_missing_open(self):
        index=pd.date_range("2024-01-01",periods=576,freq="5min",tz="UTC")
        base=pd.DataFrame({"open":100.,"high":101.,"low":99.,"close":100.},index=index)
        base.loc[index[0],"open"]=np.nan
        daily={"2024-01-01":10000.,"2024-01-02":10000.}
        dreg=pd.DataFrame({"end":[index[0].value],"regime":["downtrend"]})
        result=r.daily_groups(daily,base,dreg,index[0],index[-1])
        self.assertEqual(result["downtrend"]["days"],2)
        self.assertEqual(result["downtrend"]["btc_days_with_observed_endpoints"],1)

if __name__=="__main__":
    unittest.main()

