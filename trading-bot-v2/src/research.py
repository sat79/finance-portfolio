"""Reproducible spot research. Historical screening is not prospective validation."""
from __future__ import annotations
import concurrent.futures as cf
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import urllib.request
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "generated"
CACHE = ROOT / "data" / "cache"
MINUTE = 60_000_000_000
STEP = 5 * MINUTE
START = "2018-01-01"
END = "2026-09-01"
EVAL_START = "2020-01-01"
# Research assumptions, not historical exchange-rule claims.
FEE = .001
SLIP = .0002
RISK = .005
CAP = .25
EPS = 1e-9
CONFIGS = [
    {"name": f"A-{tf}-{r}R", "family": f"A-{tf}", "kind": "A", "tf": tf, "rr": r}
    for tf in ("5min", "15min", "1h") for r in (2, 3)
] + [
    {"name": f"B-4h-{r}R", "family": "B-4h", "kind": "B", "tf": "4h", "rr": r}
    for r in (2, 3)
] + [
    {"name": "C-1d-partial", "family": "C-1d", "kind": "C", "tf": "1d", "rr": 3}
] + [
    {"name": f"D-{tf}-{r}R", "family": f"D-{tf}", "kind": "D", "tf": tf, "rr": r}
    for tf in ("4h", "1d") for r in (2, 3)
]

def stamp(value):
    return pd.Timestamp(value, tz="UTC").value

def fetch_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "SatvikFinanceResearch/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()

def read_month(symbol, month):
    name = f"{symbol}-5m-{month}"
    url = f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/5m/{name}.zip"
    path = CACHE / (name + ".zip")
    checksum_path = CACHE / (name + ".zip.CHECKSUM")
    if not checksum_path.exists():
        checksum_path.write_bytes(fetch_bytes(url + ".CHECKSUM"))
    expected = checksum_path.read_text().split()[0]
    if not path.exists():
        payload = fetch_bytes(url)
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError(f"Checksum failure: {name}")
        path.write_bytes(payload)
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"Cached checksum failure: {name}")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        with z.open(name + ".csv") as f:
            frame = pd.read_csv(f, header=None, usecols=[0, 1, 2, 3, 4])
    frame.columns = ["time", "open", "high", "low", "close"]
    # Archive switched spot timestamps from milliseconds to microseconds in 2025.
    unit = "us" if frame.time.iloc[0] > 100_000_000_000_000 else "ms"
    frame.index = pd.to_datetime(frame.pop("time"), unit=unit, utc=True)
    record = {"url": url, "sha256": expected, "rows": len(frame), "timestamp_unit": unit}
    return frame, record

def download(symbol):
    CACHE.mkdir(parents=True, exist_ok=True)
    months = pd.date_range(START, END, freq="MS", inclusive="left").strftime("%Y-%m")
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        parts = list(pool.map(lambda m: read_month(symbol, m), months))
    frame = pd.concat([p[0] for p in parts]).sort_index()
    if frame.index.has_duplicates:
        raise ValueError("Duplicate candles")
    if not ((frame.high >= frame[["open", "close", "low"]].max(axis=1)) &
            (frame.low <= frame[["open", "close", "high"]].min(axis=1)) &
            (frame.low > 0)).all():
        raise ValueError("Malformed OHLC")
    frame, audit = validate_grid(frame, START, END)
    manifest = {"symbol": symbol, "retrieved_at": pd.Timestamp.now(tz="UTC").isoformat(),
                **audit, "archives": [p[1] for p in parts]}
    return frame, manifest

def validate_grid(frame, start, end):
    grid = pd.date_range(start, end, freq="5min", inclusive="left", tz="UTC")
    if frame.index.has_duplicates:
        raise ValueError("Duplicate candles")
    if ((frame.index < grid[0]) | (frame.index >= pd.Timestamp(end, tz="UTC"))).any():
        raise ValueError("Archive contains dates outside the requested range")
    offgrid = frame.index[~frame.index.isin(grid)]
    # Preserve archive hashes and rejected timestamps. Never round shifted candles:
    # their underlying OHLC spans a different time window.
    blocked = offgrid.floor("5min").union(offgrid.floor("5min")+pd.Timedelta(minutes=5))
    frame = frame.loc[frame.index.isin(grid)].reindex(grid)
    frame.loc[frame.index.isin(blocked), :] = np.nan
    missing = frame.index[frame.close.isna()]
    audit = {"off_grid_bars": len(offgrid), "off_grid_times": offgrid.astype(str).tolist(),
             "missing_bars": len(missing), "missing_times": missing.astype(str).tolist(),
             "handling": "Reject shifted candles and block overlapping grid intervals; no price imputation"}
    return frame, audit

def indicators(base, tf):
    count = int(pd.Timedelta(tf).value // STEP)
    grouped = base.resample(tf, label="left", closed="left")
    f = grouped.agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    valid = grouped.close.count().eq(count)
    f.loc[~valid, :] = np.nan
    previous = f.close.shift()
    tr = pd.concat([f.high - f.low, (f.high - previous).abs(),
                    (f.low - previous).abs()], axis=1).max(axis=1)
    tr[previous.isna() | f.close.isna()] = np.nan
    f["atr"] = tr.rolling(14).mean()
    f["ma21"] = f.close.rolling(21).mean()
    f["ma200"] = f.close.rolling(200).mean()
    f["rising"] = f.ma200.gt(f.ma200.shift(20))
    f["structure"] = f.low.rolling(10).min() - .25 * f.atr
    f["end"] = f.index.asi8 + pd.Timedelta(tf).value
    return f

def rsi_wilder(close):
    a = close.to_numpy(dtype=float)
    out = np.full(len(a), np.nan)
    gain = loss = None
    changes = []
    for i in range(1, len(a)):
        if not np.isfinite(a[i]) or not np.isfinite(a[i-1]):
            gain = loss = None
            changes = []
            continue
        d = a[i] - a[i-1]
        if gain is None:
            changes.append(d)
            if len(changes) < 14:
                continue
            gain = np.mean([max(x, 0) for x in changes])
            loss = np.mean([max(-x, 0) for x in changes])
        else:
            gain = (13 * gain + max(d, 0)) / 14
            loss = (13 * loss + max(-d, 0)) / 14
        out[i] = 50 if gain == loss == 0 else (100 if loss == 0 else 100-100/(1+gain/loss))
    return out

def earlier_gate(f, higher, rising=True):
    h = (higher.close > higher.ma200)
    if rising:
        h &= higher.rising
    right = pd.DataFrame({"end": higher.end.to_numpy(), "gate": h.to_numpy()})
    left = pd.DataFrame({"end": f.end.to_numpy()})
    joined = pd.merge_asof(left, right, on="end", direction="backward", allow_exact_matches=False)
    return pd.Series(joined.gate.eq(True).to_numpy(dtype=bool), index=f.index)

def divergence_signal(f, gate):
    low, high, close = (f[c].to_numpy() for c in ("low", "high", "close"))
    rsi = rsi_wilder(f.close)
    signal = np.zeros(len(f), dtype=bool)
    structure = np.full(len(f), np.nan)
    previous = None
    pending = []
    for t in range(4, len(f)):
        p = t - 2
        window = low[p-2:p+3]
        if np.isfinite(window).all() and all(low[p] < low[j] for j in (p-2, p-1, p+1, p+2)):
            if previous is not None and 3 <= p-previous <= 28:
                if low[p] > low[previous] and rsi[p] < rsi[previous]:
                    pending.append(p)
            previous = p
        keep = []
        for pivot in pending:
            if t > pivot+6 or not np.isfinite(low[pivot:t+1]).all() or np.min(low[pivot:t+1]) < low[pivot]:
                continue
            if close[t] > high[pivot]:
                if bool(gate.iloc[t]):
                    signal[t] = True
                    structure[t] = low[pivot] - .25*f.atr.iloc[t]
                # First reclaim consumes the pair, even if gate fails.
            else:
                keep.append(pivot)
        pending = keep
    return signal, structure

def prepare(base, configs=CONFIGS):
    frames = {tf: indicators(base, tf) for tf in ("5min", "15min", "1h", "4h", "1d")}
    result = {}
    for config in configs:
        f = frames[config["tf"]].copy()
        kind = config["kind"]
        if kind == "A":
            gate = earlier_gate(f, frames["4h"])
        elif kind == "B":
            gate = earlier_gate(f, frames["1d"])
        else:
            gate = f.close > f.ma200
        if kind in ("A", "B"):
            touched = (f.low <= f.ma21) & (f.close >= f.ma200)
            signal = ((f.ma21 > f.ma200) & (f.ma21.shift() > f.ma200.shift()) &
                      (f.ma21 > f.ma21.shift(3)) &
                      touched.shift().rolling(3).max().eq(1) &
                      (f.close > f.ma21) & (f.close > f.high.shift()) & gate)
            exit_rule = (~gate) | (f.ma21 <= f.ma200)
        elif kind == "C":
            near = (f.low-f.ma200).abs() <= .5*f.atr
            safe = f.close >= f.ma200-f.atr
            signal = (near.rolling(5).max().eq(1) & safe.rolling(5).min().eq(1) &
                      f.rising & (f.close > f.ma200) & (f.close > f.high.shift()))
            exit_rule = f.close < f.ma200
        else:
            gate = (f.close > f.ma21) & (f.ma21 > f.ma200) & f.rising
            if config["tf"] == "4h":
                gate &= earlier_gate(f, frames["1d"], rising=False)
            signal, structure = divergence_signal(f, gate)
            f["structure"] = structure
            exit_rule = f.close < f.ma200
        f["signal"] = np.asarray(signal, dtype=bool) & np.isfinite(f.atr) & np.isfinite(f.structure)
        f["exit"] = np.asarray(exit_rule, dtype=bool)
        events = f[["end", "signal", "exit", "atr", "structure", "high"]].copy()
        events.index = pd.to_datetime(events.pop("end"), utc=True)
        # End timestamps map to the next 5-minute bar open; events are not forward-filled.
        aligned = events.reindex(base.index)
        result[config["name"]] = {
            "signal": aligned.signal.eq(True).to_numpy(dtype=bool),
            "exit": aligned.exit.eq(True).to_numpy(dtype=bool),
            "atr": aligned.atr.to_numpy(), "structure": aligned.structure.to_numpy(),
            "daily_high": aligned.high.to_numpy(), "config": config}
    return result

def exit_fill(bar, stop, target):
    o, h, l, c = bar
    if o <= stop:
        return o, "gap_stop"
    if l <= stop:
        return stop, "stop"
    if h >= target:
        return target, "target"
    return None, None

def wilson(wins, n):
    if not n:
        return [None, None]
    z = 1.959963984540054
    p = wins/n
    den = 1+z*z/n
    center = (p+z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [100*(center-half), 100*(center+half)]

def stats(trades, daily_equity, initial, exposure_sum, steps, gap_positions, rejected, candidates):
    p = np.array([x["net_pnl"] for x in trades], dtype=float)
    wins, losses = p[p > EPS], p[p < -EPS]
    equity = np.array([initial] + list(daily_equity.values()), dtype=float)
    # Intraday maximum drawdown is supplied by the engine separately.
    return {
        "trades": len(p), "win_rate_pct": 100*len(wins)/len(p) if len(p) else None,
        "win_rate_wilson_95_pct": wilson(len(wins), len(p)),
        "payoff": float(wins.mean()/-losses.mean()) if len(wins) and len(losses) else None,
        "profit_factor": float(wins.sum()/-losses.sum()) if len(losses) else None,
        "expectancy_cash": float(p.mean()) if len(p) else None,
        "total_return_pct": 100*(equity[-1]/initial-1),
        "average_exposure_pct": 100*exposure_sum/max(1, steps),
        "gap_affected_positions": gap_positions, "candidate_signals": candidates,
        "rejected_signals": rejected,
        "costs": sum(x["costs"] for x in trades),
        "accounting_error": float(equity[-1]-initial-p.sum()),
    }

def adaptive_stop(position, high, atr, fee, slip):
    """Use only a completed signal-timeframe high, applied at next execution open."""
    position["highest"] = max(position["highest"], high)
    initial_r = position["entry"] - position["initial_stop"]
    if position["highest"] >= position["entry"] + initial_r:
        breakeven = position["entry"] * (1 + fee) / ((1 - slip) * (1 - fee))
        position["stop"] = max(position["stop"], breakeven)
    if position["highest"] >= position["entry"] + 2 * initial_r:
        position["stop"] = max(position["stop"], position["highest"] - 2 * atr)

def simulate(markets, strategies, start, end, multiplier=1, initial=10000):
    """One shared cash account. strategies is an ordered list of (symbol, prepared_signal)."""
    index = next(iter(markets.values())).index
    first = int(index.searchsorted(pd.Timestamp(start)))
    last = int(index.searchsorted(pd.Timestamp(end)))
    bars = {s: f[["open", "high", "low", "close"]].to_numpy() for s, f in markets.items()}
    fee, slip = FEE*multiplier, SLIP*multiplier
    cash = initial
    positions, prices, trades, daily = {}, {}, [], {}
    max_equity, max_dd, exposure_sum = initial, 0., 0.
    candidates = rejected = gap_positions = 0
    previous_valid = {}
    units = {"BTCUSDT": .00001, "ETHUSDT": .0001}
    min_notional = 10.  # Fixed conservative research assumption.
    def equity():
        return cash + sum(p["qty"]*prices[s] for s,p in positions.items())
    def sell(symbol, raw, fraction, when, reason):
        nonlocal cash, gap_positions
        p = positions[symbol]
        qty = p["qty"] if fraction == 1 else p["qty"]*fraction
        fill = raw*(1-slip)
        fee_cash = qty*fill*fee
        proceeds = qty*fill-fee_cash
        cash += proceeds
        p["proceeds"] += proceeds
        p["costs"] += qty*(raw-fill)+fee_cash
        p["qty"] -= qty
        p["fills"].append({"time": str(when), "price": fill, "quantity": qty, "reason": reason})
        if p["qty"] <= 1e-12:
            pnl = p["proceeds"]-p["entry_cash"]
            gap_positions += int(p["gap"])
            trades.append({"symbol": symbol, "strategy": p["name"], "entry_time": p["entry_time"],
                           "exit_time": str(when), "entry_price": p["entry"],
                           "initial_stop": p["initial_stop"], "initial_quantity": p["initial_qty"],
                           "net_pnl": pnl, "net_r": pnl/p["planned_risk"],
                           "costs": p["costs"], "gap_affected": p["gap"], "fills": p["fills"],
                           "entry_regime": p["entry_regime"]})
            del positions[symbol]
    candidate_mask = np.zeros(len(index), dtype=bool)
    for _, f in strategies:
        candidate_mask |= f["signal"]
    event_indices = np.flatnonzero(candidate_mask)
    i = first
    while i < last:
        if not positions:
            next_event = np.searchsorted(event_indices, i)
            if next_event == len(event_indices) or event_indices[next_event] >= last:
                break
            i = int(event_indices[next_event])
        when = index[i]
        exited = set()
        # Mark all available opens before processing any asset.
        for symbol in bars:
            bar = bars[symbol][i]
            if np.isfinite(bar).all():
                prices[symbol] = bar[0]
        for symbol in list(positions):
            p = positions[symbol]
            bar = bars[symbol][i]
            if not np.isfinite(bar).all():
                p["gap"] = True
                continue
            f = p["feature"]
            if p["adaptive"] and np.isfinite(f["daily_high"][i]) and np.isfinite(f["atr"][i]):
                adaptive_stop(p, f["daily_high"][i], f["atr"][i], fee, slip)
            regime_exit = ("regime" in f and f["regime"][i] != "" and
                           f["regime"][i] != p["entry_regime"])
            mean_exit = (p["adaptive"] and p["entry_regime"] == "sideways" and
                         "mean_exit" in f and f["mean_exit"][i])
            if p["kind"] == "C" and np.isfinite(f["daily_high"][i]):
                p["highest"] = max(p["highest"], f["daily_high"][i])
                if p["partial"]:
                    p["stop"] = max(p["stop"], p["highest"]-3*f["atr"][i])
            # A protective gap stop precedes discretionary next-open exits.
            if bar[0] <= p["stop"]:
                sell(symbol, bar[0], 1, when, "gap_stop")
            elif f["exit"][i] or regime_exit or mean_exit or when.value-p["entry_ns"] >= p["max_hold"]:
                sell(symbol, bar[0], 1, when, "rule_or_time")
            else:
                raw, reason = exit_fill(bar, p["stop"], p["target"])
                if raw is not None:
                    if reason == "target" and p["kind"] == "C" and not p["partial"]:
                        sell(symbol, raw, .5, when, "partial_target")
                        positions[symbol]["partial"] = True
                        positions[symbol]["target"] = math.inf
                    else:
                        sell(symbol, raw, 1, when, reason)
            if symbol not in positions:
                exited.add(symbol)
        for symbol, f in strategies:
            if not f["signal"][i]:
                continue
            candidates += 1
            bar = bars[symbol][i]
            config = f["config"]
            if symbol in positions or symbol in exited or not np.isfinite(bar).all():
                rejected += 1
                continue
            # Never execute a signal across a missing immediate execution predecessor.
            if i == 0 or not np.isfinite(bars[symbol][i-1]).all():
                rejected += 1
                continue
            entry = bar[0]*(1+slip)
            atr = f["atr"][i]
            structure = f["structure"][i]
            if not np.isfinite(atr+structure) or bar[0] <= structure:
                rejected += 1
                continue
            stop = min(entry-config.get("atr_multiple", 1.5 if config["kind"] == "A" else 2)*atr, structure)
            if stop <= 0:
                rejected += 1
                continue
            r = entry-stop
            target = entry+config["rr"]*r
            # Include estimated entry and exit fee/slippage costs.
            roundtrip = entry*(2*fee+2*slip)
            if config["rr"]*r < 3*roundtrip:
                rejected += 1
                continue
            eq = equity()
            unit_risk = entry*(1+fee)-stop*(1-slip)*(1-fee)
            risk_used = sum(p["planned_risk"] for p in positions.values())
            notional_used = sum(p["qty"]*prices[s] for s,p in positions.items())
            qty = min(eq*RISK/unit_risk, max(0, eq*.01-risk_used)/unit_risk,
                      eq*CAP/entry, max(0, eq*.5-notional_used)/entry,
                      cash/(entry*(1+fee)))
            step = units[symbol]
            qty = math.floor(qty/step)*step
            if qty*entry < min_notional:
                rejected += 1
                continue
            entry_cash = qty*entry*(1+fee)
            cash -= entry_cash
            holding_days = config.get("holding_days", 2 if config["kind"] == "A" else (365 if config["tf"] == "1d" else 30))
            positions[symbol] = {
                "name": config["name"], "kind": config["kind"], "feature": f,
                "entry_time": str(when), "entry_ns": when.value, "entry": entry,
                "initial_stop": stop, "stop": stop, "target": target,
                "qty": qty, "initial_qty": qty, "entry_cash": entry_cash,
                "planned_risk": qty*unit_risk, "proceeds": 0.,
                "costs": qty*(entry-bar[0])+qty*entry*fee, "fills": [],
                "max_hold": holding_days*24*60*MINUTE,
                "partial": False, "highest": entry, "gap": False,
                "adaptive": config.get("adaptive", False),
                "entry_regime": str(f["regime"][i]) if "regime" in f else "unspecified"}
            # Entry candle is tradable after its opening fill.
            raw, reason = exit_fill(bar, stop, target)
            if raw is not None:
                if reason == "target" and config["kind"] == "C":
                    sell(symbol, raw, .5, when, "partial_target")
                    positions[symbol]["partial"] = True
                    positions[symbol]["target"] = math.inf
                else:
                    sell(symbol, raw, 1, when, reason)
                    exited.add(symbol)
        for symbol in bars:
            if np.isfinite(bars[symbol][i]).all():
                prices[symbol] = bars[symbol][i][3]
                previous_valid[symbol] = i
        eq = equity()
        max_equity = max(max_equity, eq)
        max_dd = min(max_dd, eq/max_equity-1)
        exposure_sum += sum(p["qty"]*prices[s] for s,p in positions.items())/max(eq, EPS)
        daily[str(when.date())] = eq
        i += 1
    for symbol in list(positions):
        # Reject stale final prices rather than invent a liquidation.
        if previous_valid.get(symbol) != last-1:
            raise ValueError("Cannot liquidate at an unavailable final candle")
        sell(symbol, prices[symbol], 1, index[last-1]+pd.Timedelta(minutes=5), "boundary")
    if last > first:
        daily[str(index[last-1].date())] = cash
    day_grid = pd.date_range(pd.Timestamp(start).normalize(), pd.Timestamp(end)-pd.Timedelta(nanoseconds=1), freq="1d")
    daily = pd.Series(daily, dtype=float).reindex(day_grid.strftime("%Y-%m-%d")).ffill().fillna(initial).to_dict()
    max_dd = min(max_dd, cash/max_equity-1)
    result = stats(trades, daily, initial, exposure_sum, last-first, gap_positions, rejected, candidates)
    result["max_drawdown_pct"] = max_dd*100
    years = (pd.Timestamp(end)-pd.Timestamp(start)).total_seconds()/(365.25*86400)
    result["cagr_pct"] = 100*((cash/initial)**(1/years)-1) if years >= 1 else None
    assert abs(result["accounting_error"]) < 1e-5, result
    return result, trades, daily

def benchmark(frame, start, end, exposure, multiplier=1):
    f = frame.loc[(frame.index >= pd.Timestamp(start)) & (frame.index < pd.Timestamp(end))]
    entry, exit_ = f.open.iloc[0], f.close.iloc[-1]
    net = exit_*(1-SLIP*multiplier)*(1-FEE*multiplier)/(entry*(1+SLIP*multiplier)*(1+FEE*multiplier))-1
    return {"buy_hold_return_pct": net*100,
            "exposure_scaled_buy_hold_return_pct": net*exposure}
    # Second benchmark: invest average strategy exposure at inception, leave remainder in cash.

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    manifests, markets, features = {}, {}, {}
    for symbol in ("BTCUSDT", "ETHUSDT"):
        print("Downloading", symbol, flush=True)
        markets[symbol], manifests[symbol] = download(symbol)
        print("Preparing", symbol, "missing bars", manifests[symbol]["missing_bars"], flush=True)
        features[symbol] = prepare(markets[symbol])
    (OUT/"data-manifest.json").write_text(json.dumps(manifests, indent=2))
    settings = {"start": START, "end_exclusive": END, "evaluation_start": EVAL_START,
                "configs": CONFIGS, "fee": FEE, "slippage": SLIP, "risk": RISK, "cap": CAP,
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
                "classification": "Retrospective research; no prospective validation",
                "lot_rules": "Fixed research assumptions, not historical exchange metadata"}
    (OUT/"settings.json").write_text(json.dumps(settings, indent=2))
    rows, ledger, curves = [], [], {}
    start, end = pd.Timestamp(EVAL_START, tz="UTC"), pd.Timestamp(END, tz="UTC")
    # All predeclared variants; no winner is hidden.
    for symbol in markets:
        for config in CONFIGS:
            for multiplier in (1, 2):
                label = f"{symbol}/{config['name']}/cost{multiplier}"
                metrics, trades, daily = simulate(
                    {symbol: markets[symbol]}, [(symbol, features[symbol][config["name"]])],
                    start, end, multiplier)
                metrics.update(benchmark(markets[symbol], start, end, metrics["average_exposure_pct"], multiplier))
                metrics.update({"label": label, "symbol": symbol, "config": config["name"], "cost_multiplier": multiplier})
                metrics["meets_point_targets"] = bool(
                    metrics["trades"] >= 200 and (metrics["win_rate_pct"] or 0) >= 60 and
                    (metrics["payoff"] or 0) >= 1.5 and metrics["max_drawdown_pct"] >= -10 and
                    metrics["total_return_pct"] > 0 and metrics["gap_affected_positions"] == 0)
                rows.append(metrics)
                ledger.extend(dict(t, run=label) for t in trades)
                curves[label] = daily
                print("SCREEN", json.dumps(metrics), flush=True)
    # Exit selection is per asset and family using only the preceding 24 months.
    # Training score is net account return; skip families with no positive training variant.
    folds = []
    fold_ledgers = []
    capital = {1: 10000., 2: 10000.}
    combined_daily = {1: {}, 2: {}}
    families = sorted(set(c["family"] for c in CONFIGS))
    fold_start = start
    while fold_start < end:
        fold_end = min(fold_start+pd.DateOffset(months=6), end)
        train_start = fold_start-pd.DateOffset(months=24)
        chosen, training = [], []
        for symbol in markets:
            for family in families:
                trials = []
                for config in [c for c in CONFIGS if c["family"] == family]:
                    metrics, _, _ = simulate(
                        {symbol: markets[symbol]}, [(symbol, features[symbol][config["name"]])],
                        train_start, fold_start, 1)
                    trials.append((metrics["total_return_pct"], config["name"], metrics["gap_affected_positions"]))
                    training.append({"symbol": symbol, "config": config["name"], **metrics})
                best = sorted(trials, key=lambda x: (-x[0], x[1]))[0]
                if best[0] > 0 and best[2] == 0:
                    chosen.append((symbol, features[symbol][best[1]]))
        # Timeframe priority; deterministic name order then symbol breaks ties.
        chosen.sort(key=lambda x: (-pd.Timedelta(x[1]["config"]["tf"]).value, x[1]["config"]["name"], x[0]))
        for multiplier in (1, 2):
            metrics, trades, daily = simulate(markets, chosen, fold_start, fold_end, multiplier, capital[multiplier])
            capital[multiplier] *= 1+metrics["total_return_pct"]/100
            combined_daily[multiplier].update(daily)
            row = {"start": str(fold_start), "end": str(fold_end), "cost_multiplier": multiplier,
                   "chosen": [s+"/"+f["config"]["name"] for s,f in chosen], **metrics}
            folds.append(row)
            fold_ledgers.extend(dict(t, fold=str(fold_start), cost_multiplier=multiplier) for t in trades)
            print("FOLD", json.dumps(row), flush=True)
        (OUT/("training-"+fold_start.strftime("%Y-%m")+".json")).write_text(json.dumps(training, indent=2))
        fold_start = fold_end
    (OUT/"screen-results.json").write_text(json.dumps(rows, indent=2))
    pd.DataFrame(rows).to_csv(OUT/"screen-results.csv", index=False)
    (OUT/"trade-ledger.json").write_text(json.dumps(ledger))
    (OUT/"daily-equity.json").write_text(json.dumps(curves))
    (OUT/"rolling-folds.json").write_text(json.dumps(folds, indent=2))
    (OUT/"rolling-trades.json").write_text(json.dumps(fold_ledgers))
    (OUT/"rolling-daily-equity.json").write_text(json.dumps(combined_daily))
    summaries = []
    for multiplier in (1, 2):
        tt = [t for t in fold_ledgers if t["cost_multiplier"] == multiplier]
        dd = combined_daily[multiplier]
        a = np.array([10000.] + list(dd.values()))
        summary = stats(tt, dd, 10000, 0, 1, sum(t["gap_affected"] for t in tt), 0, 0)
        summary.pop("average_exposure_pct")
        summary["daily_max_drawdown_pct"] = 100*float(np.min(a/np.maximum.accumulate(a)-1))
        summary["cost_multiplier"] = multiplier
        summaries.append(summary)
        print("COMBINED", json.dumps(summary), flush=True)
    (OUT/"combined-summary.json").write_text(json.dumps(summaries, indent=2))
    note = """# Historical research output
All results are retrospective and sensitive to data and execution assumptions.
The screen covers every fixed configuration. Rolling evaluation selects exits using
only preceding 24-month returns, liquidates at six-month boundaries, and uses a shared
cash account with one position per asset. A positive training result is required.
Missing candles block entries and incomplete indicators. Positions crossing a missing
candle are flagged: their intragap execution is unknown, and those results are provisional.
Reported drawdown is sampled at execution-bar closes; unobserved intrabar drawdown can be larger.
Fixed lot sizes/minimum notional are research assumptions. Historical exchange rules,
time-block bootstrap confidence intervals and live order execution are not implemented.
The research target is not certified by an isolated passing point estimate.
"""
    (OUT/"README.md").write_text(note)
    print("COMPLETE", flush=True)

if __name__ == "__main__":
    run()
