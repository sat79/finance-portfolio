from pathlib import Path
import sys, unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import research as m
import market_data as d
import btc_round3 as r

class DailyDataTests(unittest.TestCase):
    def fixture(self,days):
        index=pd.date_range('2020-01-01',periods=days*288,freq='5min',tz='UTC')
        c=100+np.arange(len(index))*.001
        base=pd.DataFrame({'open':c,'high':c+.1,'low':c-.1,'close':c},index=index)
        daily=base.resample('1d').agg({'open':'first','high':'max','low':'min','close':'last'})
        return base,daily
    def test_native_daily_survives_intraday_gap_and_remains_causal(self):
        base,daily=self.fixture(250)
        base.iloc[230*288+12]=np.nan
        self.assertTrue(np.isnan(m.indicators(base,'1d').ma200.iloc[-1]))
        native=d.daily_indicators(daily)
        self.assertTrue(np.isfinite(native.ma200.iloc[-1]))
        first,reg=r.prepare(base,daily)
        changed=daily.copy();changed.iloc[240:]*=2
        second,newreg=r.prepare(base,changed)
        cutoff=daily.index[240].value
        mask=reg.end<=cutoff
        np.testing.assert_array_equal(reg.regime[mask],newreg.regime[mask])
        for name in first:
            np.testing.assert_array_equal(first[name]['signal'][:240*288],second[name]['signal'][:240*288])
        self.assertTrue(base.iloc[230*288+12].isna().all())
    def test_reconcile_detects_complete_day_mismatch(self):
        base,daily=self.fixture(3)
        self.assertEqual(d.reconcile(base,daily)['mismatched_complete_days'],0)
        daily.iloc[1,3]+=1
        with self.assertRaises(ValueError):d.reconcile(base,daily)
    def test_reconcile_excludes_partial_day_without_filling(self):
        base,daily=self.fixture(3)
        base.iloc[300]=np.nan
        daily.iloc[1,3]+=1
        record=d.reconcile(base,daily)
        self.assertEqual(record['complete_intraday_days_compared'],2)
        self.assertEqual(record['days_with_intraday_gaps'],1)
        self.assertTrue(base.iloc[300].isna().all())

if __name__=='__main__':unittest.main()
