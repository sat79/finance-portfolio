import importlib.util
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

p = Path(__file__).resolve().parents[1] / "src" / "research.py"
spec = importlib.util.spec_from_file_location("research", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ResearchTests(unittest.TestCase):
    def fixture(self, rows, kind="A", rr=2):
        index = pd.date_range("2024-01-01", periods=len(rows), freq="5min", tz="UTC")
        market = pd.DataFrame(rows, index=index, columns=["open", "high", "low", "close"])
        n = len(rows)
        f = {"signal": np.zeros(n, bool), "exit": np.zeros(n, bool),
             "atr": np.ones(n), "structure": np.full(n, 98.),
             "daily_high": np.full(n, np.nan),
             "config": {"kind": kind, "tf": "1d" if kind == "C" else "5min", "rr": rr, "name": "fixture"}}
        f["signal"][1] = True
        return market, f
    def sim(self, market, f, cost=1):
        return m.simulate({"BTCUSDT": market}, [("BTCUSDT", f)], market.index[0],
                          market.index[-1]+pd.Timedelta(minutes=5), cost)
    def test_ambiguous_stop_first(self):
        self.assertEqual(m.exit_fill((100, 110, 90, 103), 95, 105), (95, "stop"))
    def test_gap_stop_uses_open(self):
        self.assertEqual(m.exit_fill((90, 100, 89, 97), 95, 105), (90, "gap_stop"))
    def test_target_gap_no_improvement(self):
        self.assertEqual(m.exit_fill((110, 112, 108, 111), 95, 105), (105, "target"))
    def test_accounting_and_boundary(self):
        market, f = self.fixture([(100,101,99,100)]*6)
        result, trades, _ = self.sim(market, f)
        self.assertEqual(len(trades), 1)
        self.assertLess(trades[0]["net_pnl"], 0)
        self.assertAlmostEqual(result["accounting_error"], 0)
        self.assertEqual(trades[0]["entry_time"], str(market.index[1]))
        self.assertEqual(trades[0]["fills"][-1]["reason"], "boundary")
    def test_stop_applies_entry_bar(self):
        market, f = self.fixture([(100,101,99,100),(100,106,90,100),(100,101,99,100)])
        result, trades, _ = self.sim(market, f)
        self.assertEqual(trades[0]["fills"][0]["reason"], "stop")
        self.assertEqual(trades[0]["exit_time"], str(market.index[1]))
    def test_higher_cost_reduces_flat_trade(self):
        market, f = self.fixture([(100,101,99,100)]*6)
        a = self.sim(market, f, 1)[0]
        b = self.sim(market, f, 2)[0]
        self.assertLess(b["total_return_pct"], a["total_return_pct"])
    def test_partial_is_one_trade(self):
        market, f = self.fixture([(100,101,99,100),(100,107,99,105),(105,106,104,105)], kind="C", rr=3)
        result, trades, _ = self.sim(market, f)
        self.assertEqual(result["trades"], 1)
        self.assertEqual(len(trades[0]["fills"]), 2)
        self.assertEqual(trades[0]["fills"][0]["reason"], "partial_target")
        self.assertAlmostEqual(sum(x["quantity"] for x in trades[0]["fills"]), trades[0]["initial_quantity"])
    def test_missing_bar_flag(self):
        market, f = self.fixture([(100,101,99,100)]*5)
        market.iloc[2] = np.nan
        result, trades, _ = self.sim(market, f)
        self.assertEqual(result["gap_affected_positions"], 1)
    def test_missing_predecessor_blocks_entry(self):
        market, f = self.fixture([(100,101,99,100)]*5)
        market.iloc[0] = np.nan
        self.assertEqual(self.sim(market, f)[0]["trades"], 0)
    def test_strict_higher_timeframe(self):
        f = pd.DataFrame({"end": [10, 20, 21]})
        h = pd.DataFrame({"end": [10, 20], "close": [2, 2], "ma200": [1, 1], "rising": [True, True]})
        self.assertEqual(m.earlier_gate(f,h).tolist(), [False, True, True])
    def test_future_data_does_not_change_past_signals(self):
        index = pd.date_range("2020-01-01", periods=4000, freq="5min", tz="UTC")
        rng = np.random.default_rng(9)
        close = 100+np.cumsum(rng.normal(0,.05,len(index)))
        base = pd.DataFrame({"open":close,"high":close+.1,"low":close-.1,"close":close},index=index)
        configs = [m.CONFIGS[0], m.CONFIGS[-1]]
        before = m.prepare(base, configs)
        changed = base.copy()
        changed.iloc[3000:] *= 3
        after = m.prepare(changed, configs)
        for c in configs:
            name=c["name"]
            np.testing.assert_array_equal(before[name]["signal"][:3000],after[name]["signal"][:3000])
        # Direct divergence logic is exercised on a history long enough for daily SMA200.
        daily = pd.DataFrame({"close":close[:1000],"high":close[:1000]+.1,"low":close[:1000]-.1,"atr":.2})
        a = m.divergence_signal(daily, pd.Series(True,index=daily.index))[0]
        daily.loc[800:,["close","high","low"]] *= 3
        b = m.divergence_signal(daily, pd.Series(True,index=daily.index))[0]
        np.testing.assert_array_equal(a[:800],b[:800])
    def test_rsi_flat_and_rising(self):
        self.assertEqual(m.rsi_wilder(pd.Series([1.]*20))[-1],50)
        self.assertEqual(m.rsi_wilder(pd.Series(range(20)))[-1],100)
    def test_shared_one_position_per_asset(self):
        market, f = self.fixture([(100,101,99,100)]*5)
        result, trades, _ = m.simulate({"BTCUSDT":market},[("BTCUSDT",f),("BTCUSDT",f)],
                                      market.index[0],market.index[-1]+pd.Timedelta(minutes=5))
        self.assertEqual(result["trades"],1)
        self.assertLessEqual(trades[0]["initial_quantity"]*trades[0]["entry_price"],2500)
    def test_fold_has_no_later_fills(self):
        market, f = self.fixture([(100,101,99,100)]*6)
        cutoff=market.index[4]
        _, trades, _ = m.simulate({"BTCUSDT":market},[("BTCUSDT",f)],market.index[0],cutoff)
        self.assertLessEqual(pd.Timestamp(trades[0]["exit_time"]),cutoff)
    def test_no_signals_stays_cash(self):
        market, f = self.fixture([(100,101,99,100)]*5)
        f["signal"][:]=False
        result, trades, daily = self.sim(market,f)
        self.assertEqual(result["total_return_pct"],0)
        self.assertEqual(trades,[])
    def test_trail_not_updated_from_current_execution_high(self):
        market, f = self.fixture([(100,101,99,100),(100,107,99,105),(105,120,100,110),(110,111,109,110)],kind="C",rr=3)
        _, trades, _ = self.sim(market,f)
        self.assertEqual(trades[0]["fills"][-1]["reason"],"boundary")

if __name__ == "__main__":
    unittest.main()
