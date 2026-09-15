from pathlib import Path
import sys, unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import futures_engine as e
import futures_signals as s

class FuturesTests(unittest.TestCase):
    def fixture(self,side=1,n=8):
        index=pd.date_range('2024-01-01',periods=n,freq='5min',tz='UTC')
        frame=pd.DataFrame({'open':100.,'high':100.5,'low':99.5,'close':100.},index=index)
        funding=pd.DataFrame({'rate':[]},index=pd.DatetimeIndex([],tz='UTC'))
        frames={'trade':frame,'mark':frame.copy(),'funding':funding}
        sides={}
        for sign in (1,-1):
            sides[sign]={'signal':np.zeros(n,bool),'structure':np.full(n,98. if sign==1 else 102.),
                'atr':np.ones(n),'regime':np.full(n,'uptrend' if sign==1 else 'downtrend',dtype=object),
                'completed_favorable':np.full(n,np.nan),'mean_exit':np.zeros(n,bool),'trend_exit':np.zeros(n,bool)}
        sides[side]['signal'][1]=True
        f={'config':{'name':'fixture','tf':'1h','atr_multiple':1.5,'rr':2,'holding_days':5,'exit_policy':'2R'},'sides':sides}
        return frames,f,index
    def run_fixture(self,frames,f,index,**kwargs):return e.simulate(e.Market(frames),f,index[0],index[-1]+pd.Timedelta(minutes=5),**kwargs)
    def test_long_and_short_signed_profit_and_cash_identity(self):
        for side in (1,-1):
            frames,f,idx=self.fixture(side)
            for k in ('trade','mark'):frames[k].iloc[-1]=[100+side,101.5,98.5,100+side]
            metrics,t,_=self.run_fixture(frames,f,idx,cost=0)
            self.assertGreater(t[0]['net_pnl'],0);self.assertAlmostEqual(metrics['accounting_error'],0)
            self.assertAlmostEqual(t[0]['net_pnl'],t[0]['initial_quantity'])
    def test_both_barriers_stop_first_each_direction(self):
        self.assertEqual(e.protective_fill([100,110,90,100],98,104,1),(98,'stop'))
        self.assertEqual(e.protective_fill([100,110,90,100],102,96,-1),(102,'stop'))
    def test_adverse_gaps_fill_at_open(self):
        self.assertEqual(e.protective_fill([95,101,94,100],98,104,1),(95,'gap_stop'))
        self.assertEqual(e.protective_fill([105,106,99,100],102,96,-1),(105,'gap_stop'))
    def test_short_fees_and_slippage_are_costs(self):
        frames,f,idx=self.fixture(-1)
        _,zero,_=self.run_fixture(frames,f,idx,cost=0)
        _,paid,_=self.run_fixture(frames,f,idx,cost=1)
        self.assertAlmostEqual(zero[0]['net_pnl'],0)
        self.assertLess(paid[0]['net_pnl'],0);self.assertGreater(paid[0]['costs'],0)
    def test_quantity_respects_cost_adjusted_risk_and_ceiling(self):
        for side in (1,-1):
            for ceiling in (1,2,3,5):
                q,unit=e.quantity(10000,100,100-side*.01,side,ceiling,.0005,.0002)
                self.assertLessEqual(q*unit,50+1e-9)
                self.assertLessEqual(q*100/(10000-q*100*.0005),ceiling+1e-9)
        with self.assertRaises(ValueError):e.quantity(10000,100,99,1,6,.0005,.0002)
    def test_funding_direction_and_exact_event_cash(self):
        self.assertEqual(e.funding_cash(1,2,100,.001),-.2)
        self.assertEqual(e.funding_cash(-1,2,100,.001),.2)
        for side in (1,-1):
            frames,f,idx=self.fixture(side)
            frames['funding']=pd.DataFrame({'rate':[.001]},index=idx[2:3])
            metrics,t,_=self.run_fixture(frames,f,idx,cost=0)
            self.assertAlmostEqual(t[0]['net_pnl'],-side*t[0]['initial_quantity']*100*.001)
            self.assertEqual(t[0]['funding_events'],1);self.assertAlmostEqual(metrics['accounting_error'],0)
    def test_new_entry_not_charged_past_exact_funding(self):
        frames,f,idx=self.fixture()
        frames['funding']=pd.DataFrame({'rate':[.001]},index=idx[1:2])
        _,t,_=self.run_fixture(frames,f,idx,cost=0)
        self.assertEqual(t[0]['funding_cash'],0)
    def test_intrabar_funding_blocks_new_entry(self):
        frames,f,idx=self.fixture()
        frames['funding']=pd.DataFrame({'rate':[.001]},index=idx[1:2]+pd.Timedelta(milliseconds=1))
        _,t,_=self.run_fixture(frames,f,idx,cost=0)
        self.assertEqual(len(t),0)
    def test_intrabar_credit_not_awarded_to_exiting_position(self):
        frames,f,idx=self.fixture(-1)
        frames['funding']=pd.DataFrame({'rate':[.001]},index=idx[2:3]+pd.Timedelta(milliseconds=1))
        f['sides'][-1]['trend_exit'][2]=True
        _,t,_=self.run_fixture(frames,f,idx,cost=0)
        self.assertEqual(t[0]['funding_cash'],0)
    def test_completed_bar_breakeven_is_cost_adjusted_both_sides(self):
        for side in (1,-1):
            p={'side':side,'entry':100.,'distance':2.,'best':side*100,'stop':100-side*2}
            e.ratchet(p,100+side*2.1,1,.0005,.0002)
            fill=p['stop']*(1-side*.0002)
            self.assertAlmostEqual(side*(fill-100)-.0005*(100+fill),0)
            old=p['stop'];e.ratchet(p,100+side*1,5,.0005,.0002)
            self.assertEqual(p['stop'],old)
    def test_future_high_cannot_tighten_current_stop(self):
        frames,f,idx=self.fixture()
        f['config']['exit_policy']='adaptive'
        frames['trade'].iloc[1]=[100,103,99,100]
        _,t,_=self.run_fixture(frames,f,idx,cost=0)
        self.assertEqual(t[0]['fills'][0]['reason'],'boundary')
    def test_missing_mark_flags_position(self):
        frames,f,idx=self.fixture();frames['mark'].iloc[3]=np.nan
        metrics,t,_=self.run_fixture(frames,f,idx,cost=0)
        self.assertTrue(t[0]['gap_affected']);self.assertEqual(metrics['gap_affected_positions'],1)
    def test_mark_price_can_trigger_liquidation_without_trade_stop(self):
        frames,f,idx=self.fixture();f['sides'][1]['atr'][:]=.02;f['sides'][1]['structure'][:]=99.9
        frames['trade'].iloc[:]=[100,100.01,99.99,100]
        frames['mark'].iloc[2]=[100,101,70,100]
        metrics,t,_=self.run_fixture(frames,f,idx,cost=0,initial=1000)
        self.assertEqual(t[0]['fills'][0]['reason'],'liquidation');self.assertEqual(metrics['liquidations'],1)
    def test_reflected_prices_preserve_ohlc_geometry(self):
        frames,_,_=self.fixture();raw=frames['trade'];ref=s.signed_prices(raw,-1)
        self.assertTrue((ref.high>=ref.low).all());np.testing.assert_allclose(s.signed_prices(ref,-1),raw)
    def test_future_changes_do_not_change_past_signals(self):
        idx=pd.date_range('2020-01-01',periods=75000,freq='5min',tz='UTC')
        rng=np.random.default_rng(919);price=100+np.cumsum(rng.normal(.001,.03,len(idx)))
        base=pd.DataFrame({'open':price,'high':price+.1,'low':price-.1,'close':price},index=idx)
        daily=base.resample('1d').agg({'open':'first','high':'max','low':'min','close':'last'})
        a,_=s.prepare(base,daily)
        cutoff=70000;base.iloc[cutoff:]*=2
        daily.loc[daily.index>=idx[cutoff].floor('1d')+pd.Timedelta(days=1)]*=2
        b,_=s.prepare(base,daily)
        for name in a:
            for side in (1,-1):np.testing.assert_array_equal(a[name]['sides'][side]['signal'][:cutoff],b[name]['sides'][side]['signal'][:cutoff])

if __name__=='__main__':unittest.main()
