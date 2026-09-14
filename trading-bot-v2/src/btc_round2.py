"""BTCUSDT-only second research round. See BTC-ROUND-2-SPEC.md."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import research as m

OUT = m.ROOT / "reports" / "generated" / "btc-round-2"
CONFIGS = []
for family, tf, days, atr in [
    ("E","1h",2,1.5), ("E","4h",30,2),
    ("F","15min",2,1.5), ("F","1h",2,1.5),
    ("G","4h",10,2), ("G","1d",20,2)]:
    for rr in (2,3):
        CONFIGS.append({"name":f"{family}-{tf}-{rr}R","family":family,"tf":tf,
                        "kind":"B", "rr":rr,"holding_days":days,"atr_multiple":atr})

def rsi(close, period):
    values = close.to_numpy(dtype=float)
    result = np.full(len(values), np.nan)
    gain = loss = None
    initial = []
    for i in range(1,len(values)):
        if not np.isfinite(values[i:i+1]).all() or not np.isfinite(values[i-1]):
            gain = loss = None
            initial = []
            continue
        d = values[i]-values[i-1]
        if gain is None:
            initial.append(d)
            if len(initial) < period:
                continue
            gain = np.mean([max(x,0) for x in initial])
            loss = np.mean([max(-x,0) for x in initial])
        else:
            gain = ((period-1)*gain+max(d,0))/period
            loss = ((period-1)*loss+max(-d,0))/period
        result[i] = 50 if gain == loss == 0 else (100 if loss == 0 else 100-100/(1+gain/loss))
    return pd.Series(result,index=close.index)

def raw_rule(f, family, gate):
    if family == "E":
        width = (f.high.rolling(20).max()-f.low.rolling(20).min())/f.ma21
        compressed = width < width.shift().rolling(120).quantile(.2)
        level = f.high.shift().rolling(20).max()
        signal = (compressed.shift().rolling(12).max().eq(1) &
                  (f.close > level) & (f.close.shift() <= level.shift()) & gate)
        structure = level-.25*f.atr
        exit_rule = (~gate) | (f.close < f.ma21)
    elif family == "F":
        level = f.low.shift().rolling(20).min()
        strength = (f.close-f.low)/(f.high-f.low).replace(0,np.nan)
        signal = ((f.low < level) & (f.close > level) & (f.close > f.open) &
                  (strength >= .65) & (rsi(f.close,14) < 45) & gate)
        structure = f.low-.25*f.atr
        exit_rule = ~gate
    else:
        fast = rsi(f.close,2)
        signal = (fast.shift().le(10) & fast.gt(10) & (f.close > f.close.shift()) & gate)
        structure = f.low.rolling(3).min()-.25*f.atr
        exit_rule = ~gate
    signal &= np.isfinite(structure) & np.isfinite(f.atr)
    return signal,structure,exit_rule

def prepare(base):
    frames = {tf:m.indicators(base,tf) for tf in ("15min","1h","4h","1d")}
    output = {}
    for config in CONFIGS:
        f = frames[config["tf"]]
        if config["tf"] == "1d":
            gate = (f.close > f.ma200) & f.rising
        else:
            higher = frames["1d"] if config["tf"] == "4h" else frames["4h"]
            gate = m.earlier_gate(f,higher,rising=False)
        signal,structure,exit_rule = raw_rule(f,config["family"],gate)
        event = pd.DataFrame({"signal":signal,"structure":structure,"exit":exit_rule,
                              "atr":f.atr,"daily_high":f.high})
        event.index = pd.to_datetime(f.end.to_numpy(),utc=True)
        event = event.reindex(base.index)
        output[config["name"]] = {
            "signal":event.signal.eq(True).to_numpy(dtype=bool),
            "exit":event.exit.eq(True).to_numpy(dtype=bool),
            "structure":event.structure.to_numpy(),"atr":event.atr.to_numpy(),
            "daily_high":event.daily_high.to_numpy(),"config":config}
    return output

def extra_metrics(trades, daily, initial=10000):
    s = pd.Series(daily,dtype=float)
    s.index = pd.to_datetime(s.index)
    anchor = pd.Series([initial],index=[s.index[0]-pd.Timedelta(days=1)])
    equity = pd.concat([anchor,s])
    monthly = equity.resample("ME").last().pct_change().dropna()
    yearly = equity.resample("YE").last().pct_change().dropna()
    peak = equity.cummax()
    max_underwater = current = 0
    for down in equity.lt(peak-1e-8):
        current = current+1 if down else 0
        max_underwater = max(max_underwater,current)
    loss_streak = current = 0
    for t in trades:
        current = current+1 if t["net_pnl"] < -m.EPS else 0
        loss_streak = max(loss_streak,current)
    turnover = sum(t["initial_quantity"]*t["entry_price"]+
                   sum(f["quantity"]*f["price"] for f in t["fills"]) for t in trades)
    return {
        "worst_month_pct":float(monthly.min()*100) if len(monthly) else None,
        "worst_year_pct":float(yearly.min()*100) if len(yearly) else None,
        "monthly_returns_pct":{str(k.date()):float(v*100) for k,v in monthly.items()},
        "yearly_returns_pct":{str(k.date()):float(v*100) for k,v in yearly.items()},
        "longest_losing_streak":loss_streak,"daily_time_underwater_max_days":max_underwater,
        "turnover_over_mean_equity":turnover/equity.mean(),
        "daily_max_drawdown_pct":float((equity/peak-1).min()*100)}

def bootstrap(trades,start,end,draws=2000):
    months = pd.date_range(pd.Timestamp(start).tz_localize(None),
                          pd.Timestamp(end).tz_localize(None),freq="MS",inclusive="left").to_period("M")
    counts = np.zeros(len(months))
    netr = np.zeros(len(months))
    wins = np.zeros(len(months))
    losses = np.zeros(len(months))
    for t in trades:
        # Boundary liquidations at the fold end belong to the preceding period.
        ts = pd.Timestamp(t["exit_time"])
        if t["fills"][-1]["reason"] == "boundary":
            ts -= pd.Timedelta(nanoseconds=1)
        k = months.get_indexer([ts.tz_localize(None).to_period("M")])[0]
        if k < 0:
            continue
        counts[k] += 1
        netr[k] += t["net_r"]
        wins[k] += max(t["net_pnl"],0)
        losses[k] += max(-t["net_pnl"],0)
    rng = np.random.default_rng(20260914)
    starts = rng.integers(0,len(months),size=(draws,math.ceil(len(months)/3)))
    indices = ((starts[:,:,None]+np.arange(3))%len(months)).reshape(draws,-1)[:,:len(months)]
    n = counts[indices].sum(axis=1)
    rr = netr[indices].sum(axis=1)
    w,l = wins[indices].sum(axis=1),losses[indices].sum(axis=1)
    def interval(values):
        return np.quantile(values,[.025,.975]).tolist() if len(values) else [None,None]
    return {"mean_net_r":sum(t["net_r"] for t in trades)/len(trades) if trades else None,
            "mean_net_r_block_95":interval(rr[n>0]/n[n>0]),
            "profit_factor_block_95":interval(w[l>0]/l[l>0]),
            "bootstrap_draws":draws,"bootstrap_pf_undefined_draws":int((l==0).sum()),
            "bootstrap_block_months":3}

def compact(row):
    return {k:v for k,v in row.items() if k not in ("monthly_returns_pct","yearly_returns_pct")}

def select(training, features):
    selected = []
    for family in ("E","F","G"):
        eligible = [r for r in training if r["family"]==family and r["trades"]>=30 and
                    r["total_return_pct"]>0 and (r["profit_factor"] or 0)>1 and r["gap_affected_positions"]==0]
        if eligible:
            best = sorted(eligible,key=lambda r:(-r["total_return_pct"],r["config"]))[0]
            selected.append(("BTCUSDT",features[best["config"]]))
    selected.sort(key=lambda x:(-pd.Timedelta(x[1]["config"]["tf"]).value,x[1]["config"]["name"]))
    return selected

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    print("BTC2 DOWNLOAD",flush=True)
    base,manifest=m.download("BTCUSDT")
    (OUT/"data-manifest.json").write_text(json.dumps(manifest,indent=2))
    print("BTC2 DATA",json.dumps({"missing_bars":manifest["missing_bars"],"off_grid_bars":manifest["off_grid_bars"]}),flush=True)
    features=prepare(base)
    markets={"BTCUSDT":base}
    start=pd.Timestamp("2020-01-01",tz="UTC")
    end=pd.Timestamp("2026-09-01",tz="UTC")
    settings={"configs":CONFIGS,"start":str(start),"end_exclusive":str(end),
              "classification":"Research-exposed retrospective evaluation",
              "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "engine_sha256":hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
              "fee":m.FEE,"slippage":m.SLIP,"planned_risk":m.RISK,
              "bootstrap":"2000 draws, circular three-month blocks, seed 20260914"}
    (OUT/"settings.json").write_text(json.dumps(settings,indent=2))
    rows=[]
    ledger=[]
    curves={}
    for config in CONFIGS:
        for cost in (0,1,2):
            metrics,trades,daily=m.simulate(markets,[("BTCUSDT",features[config["name"]])],start,end,cost)
            metrics.update({"config":config["name"],"family":config["family"],"cost_multiplier":cost})
            metrics.update(extra_metrics(trades,daily))
            metrics.update(bootstrap(trades,start,end))
            metrics.update(m.benchmark(base,start,end,metrics["average_exposure_pct"],cost))
            metrics["point_target_status"]="MEETS_POINT_TARGETS" if (
                metrics["trades"]>=200 and (metrics["win_rate_pct"] or 0)>=60 and
                (metrics["payoff"] or 0)>=1.5 and metrics["total_return_pct"]>0 and
                metrics["max_drawdown_pct"]>=-10 and metrics["gap_affected_positions"]==0
            ) else "FAIL_OR_INSUFFICIENT"
            rows.append(metrics)
            label=config["name"]+f"/cost{cost}"
            ledger.extend(dict(t,run=label) for t in trades)
            curves[label]=daily
            print("BTC2 SCREEN",json.dumps(compact(metrics)),flush=True)
    (OUT/"screen.json").write_text(json.dumps(rows,indent=2))
    pd.DataFrame([compact(r) for r in rows]).to_csv(OUT/"screen.csv",index=False)
    (OUT/"trade-ledger.json").write_text(json.dumps(ledger))
    (OUT/"daily-equity.json").write_text(json.dumps(curves))
    capital={1:10000.,2:10000.}
    combined_daily={1:{},2:{}}
    combined_trades={1:[],2:[]}
    fold_rows=[]
    begin=start
    while begin<end:
        finish=min(begin+pd.DateOffset(months=6),end)
        train_start=begin-pd.DateOffset(months=24)
        training=[]
        for config in CONFIGS:
            metrics,_,_=m.simulate(markets,[("BTCUSDT",features[config["name"]])],train_start,begin,1)
            training.append(dict(metrics,config=config["name"],family=config["family"]))
        chosen=select(training,features)
        (OUT/("training-"+begin.strftime("%Y-%m")+".json")).write_text(json.dumps(training,indent=2))
        for cost in (1,2):
            metrics,trades,daily=m.simulate(markets,chosen,begin,finish,cost,capital[cost])
            capital[cost]*=1+metrics["total_return_pct"]/100
            combined_daily[cost].update(daily)
            combined_trades[cost].extend(trades)
            row=dict(metrics,start=str(begin),end=str(finish),cost_multiplier=cost,
                     chosen=[f["config"]["name"] for _,f in chosen])
            fold_rows.append(row)
            print("BTC2 FOLD",json.dumps(row),flush=True)
        begin=finish
    summaries=[]
    for cost in (1,2):
        fs=[f for f in fold_rows if f["cost_multiplier"]==cost]
        weighted=0.
        total=0.
        for f in fs:
            days=(pd.Timestamp(f["end"])-pd.Timestamp(f["start"])).total_seconds()
            weighted+=days*f["average_exposure_pct"]
            total+=days
        trades,daily=combined_trades[cost],combined_daily[cost]
        metrics=m.stats(trades,daily,10000,0,1,sum(t["gap_affected"] for t in trades),
                        sum(f["rejected_signals"] for f in fs),sum(f["candidate_signals"] for f in fs))
        metrics["average_exposure_pct"]=weighted/total
        metrics["cost_multiplier"]=cost
        metrics["cagr_pct"]=100*((capital[cost]/10000)**(365.25*86400/total)-1)
        metrics.update(extra_metrics(trades,daily))
        metrics.update(bootstrap(trades,start,end))
        metrics.update(m.benchmark(base,start,end,metrics["average_exposure_pct"],cost))
        summaries.append(metrics)
        print("BTC2 COMBINED",json.dumps(compact(metrics)),flush=True)
    (OUT/"combined.json").write_text(json.dumps(summaries,indent=2))
    (OUT/"folds.json").write_text(json.dumps(fold_rows,indent=2))
    (OUT/"rolling-trades.json").write_text(json.dumps(combined_trades))
    (OUT/"rolling-equity.json").write_text(json.dumps(combined_daily))
    chart = ["date,normal_cost_equity,double_cost_equity"]
    chart += [f"{d},{v},{combined_daily[2].get(d,'')}" for d,v in combined_daily[1].items()]
    (OUT/"rolling-equity.csv").write_text("\n".join(chart)+"\n")
    print("BTC2 COMPLETE",flush=True)

if __name__=="__main__":
    run()
