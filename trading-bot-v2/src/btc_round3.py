"""Round 3: causal regimes, Fibonacci entries and adaptive protective exits."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import research as m
import btc_round2 as previous
import market_data

OUT=m.ROOT/"reports"/"generated"/"btc-round-3"
CONFIGS=[{"name":f"H-{tf}-{confirm}-{exit_}","tf":tf,"confirmation":confirm,
          "policy":exit_,"kind":"B","rr":{"fixed1.5":1.5,"fixed2":2,"adaptive":3}[exit_],
          "atr_multiple":1.5,"holding_days":5 if tf=="1h" else 20,
          "adaptive":exit_=="adaptive"}
         for tf in ("1h","4h") for confirm in ("rsi","div") for exit_ in ("fixed1.5","fixed2","adaptive")]

def wilder(values,n=14):
    output=np.full(len(values),np.nan)
    buffer=[]; state=None
    for i,v in enumerate(values):
        if not np.isfinite(v):
            buffer=[];state=None;continue
        if state is None:
            buffer.append(v)
            if len(buffer)<n:continue
            state=float(np.mean(buffer))
        else:state=((n-1)*state+v)/n
        output[i]=state
    return output

def regimes(daily):
    d=daily
    up=d.high.diff();down=-d.low.diff()
    plus=np.where((up>down)&(up>0),up,0.).astype(float)
    minus=np.where((down>up)&(down>0),down,0.).astype(float)
    valid=d.close.notna()&d.close.shift().notna()
    plus[~valid]=np.nan;minus[~valid]=np.nan
    tr=pd.concat([d.high-d.low,(d.high-d.close.shift()).abs(),(d.low-d.close.shift()).abs()],axis=1).max(axis=1)
    tr[~valid]=np.nan
    smooth_tr=wilder(tr.to_numpy())
    with np.errstate(divide="ignore",invalid="ignore"):
        p=100*wilder(plus)/smooth_tr
        q=100*wilder(minus)/smooth_tr
        dx=100*np.abs(p-q)/(p+q)
    dx[(p+q)==0]=0.
    adx=wilder(dx)
    slope=(d.ma200-d.ma200.shift(20))/d.atr
    known=np.isfinite(adx)&np.isfinite(slope)&d.ma200.notna()
    label=np.full(len(d),"unknown",dtype=object)
    label[known]="transition"
    label[known&(adx<20)]="sideways"
    label[known&(adx>=20)&(d.close>d.ma200)&(slope>.5)]="uptrend"
    label[known&(adx>=20)&(d.close<d.ma200)&(slope<-.5)]="downtrend"
    return pd.DataFrame({"end":d.end.to_numpy(),"regime":label,"adx":adx,"slope_atr":slope.to_numpy()},index=d.index)

def eligible_regime(frame,daily_regime):
    left=pd.DataFrame({"end":frame.end.to_numpy()})
    right=daily_regime[["end","regime"]].reset_index(drop=True)
    joined=pd.merge_asof(left,right,on="end",direction="backward",allow_exact_matches=False)
    return pd.Series(joined.regime.fillna("unknown").to_numpy(),index=frame.index)

def fib_signals(f,require_div=False,allowed=None):
    lo=f.low.to_numpy();hi=f.high.to_numpy();cl=f.close.to_numpy()
    atr=f.atr.to_numpy();rsi=previous.rsi(f.close,14).to_numpy()
    signal=np.zeros(len(f),bool)
    anchor_low=np.full(len(f),np.nan);anchor_high=np.full(len(f),np.nan)
    last_low=None; low_history=[]; impulse=None; consumed=set()
    for t in range(4,len(f)):
        p=t-2
        lows=lo[p-2:p+3];highs=hi[p-2:p+3]
        if not np.isfinite(lows).all() or not np.isfinite(highs).all():
            last_low=None;low_history=[];impulse=None;continue
        pivot_low=all(lo[p]<lo[k] for k in (p-2,p-1,p+1,p+2))
        pivot_high=all(hi[p]>hi[k] for k in (p-2,p-1,p+1,p+2))
        prior_low=last_low
        if pivot_high and prior_low is not None and prior_low<p:
            if np.isfinite(atr[p]) and hi[p]-lo[prior_low]>=3*atr[p]:
                impulse=(prior_low,p)
        if pivot_low:
            last_low=p
            low_history.append(p)
            low_history=low_history[-2:]
        if impulse is None:continue
        a,h=impulse
        if t-h>20 or impulse in consumed:continue
        if np.any(~np.isfinite(lo[h:t+1])) or np.min(lo[h:t+1])<lo[a]:continue
        anchor_low[t]=lo[a];anchor_high[t]=hi[h]
        span=hi[h]-lo[a]
        level38=hi[h]-.382*span;level50=hi[h]-.5*span;level62=hi[h]-.618*span
        touched=any(lo[j]<=level38 and hi[j]>=level62 for j in range(max(h+1,t-2),t+1))
        confirmed=cl[t]>hi[t-1] and cl[t]>level50 and cl[t]<hi[h] and rsi[t]>40 and rsi[t]>rsi[t-1]
        div=False
        if len(low_history)==2:
            p1,p2=low_history
            div=3<=p2-p1<=28 and p2>h and t-p2<=8 and lo[p2]>lo[p1] and rsi[p2]<rsi[p1]
        if touched and confirmed and (div or not require_div) and (allowed is None or allowed[t]):
            signal[t]=True;consumed.add(impulse)
    return signal,anchor_low,anchor_high

def prepare(base,daily_prices=None):
    frames={tf:m.indicators(base,tf) for tf in ("1h","4h","1d")}
    if daily_prices is not None:
        frames["1d"]=market_data.daily_indicators(daily_prices)
    daily_regime=regimes(frames["1d"])
    output={}
    for tf in ("1h","4h"):
        f=frames[tf]
        reg=eligible_regime(f,daily_regime)
        fast=previous.rsi(f.close,14)
        mean=f.close.rolling(20).mean()
        lower=mean-2*f.close.rolling(20).std(ddof=0)
        range_signal=(f.low<lower)&(f.close>lower)&(f.close>f.open)&(fast<40)&(fast>fast.shift())
        for confirm in ("rsi","div"):
            fib,anchor_low,anchor_high=fib_signals(f,require_div=confirm=="div",allowed=reg.eq("uptrend").to_numpy())
            signal=(np.asarray(fib)&reg.eq("uptrend").to_numpy())|(range_signal&reg.eq("sideways")).to_numpy()
            signal &= f.atr.notna().to_numpy()
            structure=f.low.rolling(5).min()-.25*f.atr
            for policy in ("fixed1.5","fixed2","adaptive"):
                config=next(c for c in CONFIGS if c["tf"]==tf and c["confirmation"]==confirm and c["policy"]==policy)
                event=pd.DataFrame({"signal":signal,"structure":structure,"atr":f.atr,
                                    "exit":False,"daily_high":f.high,"regime":reg,
                                    "mean_exit":(f.close>=mean).to_numpy(),"anchor_low":anchor_low,"anchor_high":anchor_high})
                event.index=pd.to_datetime(f.end.to_numpy(),utc=True)
                event=event.reindex(base.index)
                output[config["name"]]={
                    "signal":event.signal.eq(True).to_numpy(dtype=bool),
                    "exit":event.exit.eq(True).to_numpy(dtype=bool),
                    "structure":event.structure.to_numpy(),"atr":event.atr.to_numpy(),
                    "daily_high":event.daily_high.to_numpy(),
                    "regime":event.regime.fillna("").to_numpy(),
                    "mean_exit":event.mean_exit.eq(True).to_numpy(dtype=bool),
                    "anchor_low":event.anchor_low.to_numpy(),"anchor_high":event.anchor_high.to_numpy(),
                    "config":config}
    return output,daily_regime

def trade_groups(trades):
    result={}
    for regime in ("uptrend","sideways","downtrend","transition","unknown"):
        tt=[t for t in trades if t.get("entry_regime")==regime]
        p=np.array([t["net_pnl"] for t in tt])
        wins=p[p>m.EPS];losses=p[p<-m.EPS]
        result[regime]={"trades":len(tt),"win_rate_pct":100*len(wins)/len(tt) if tt else None,
                        "profit_factor":float(wins.sum()/-losses.sum()) if len(losses) else None,
                        "payoff":float(wins.mean()/-losses.mean()) if len(wins) and len(losses) else None,
                        "net_pnl":float(p.sum())}
    return result

def daily_groups(daily,base,daily_regime,start,end,initial=10000):
    s=pd.Series(daily,dtype=float);s.index=pd.to_datetime(s.index,utc=True)
    account=s.pct_change();account.iloc[0]=s.iloc[0]/initial-1
    day=pd.DataFrame({"end":s.index.asi8})
    labels=pd.merge_asof(day,daily_regime[["end","regime"]].reset_index(drop=True),
                         on="end",direction="backward",allow_exact_matches=True).regime.fillna("unknown")
    # Daily regime is known at the open. Daily market benchmark has no fees.
    day_open=base.open.reindex(s.index).to_numpy()
    day_close=base.close.reindex(s.index+pd.Timedelta(hours=23,minutes=55)).to_numpy()
    market=pd.Series(day_close/day_open-1,index=s.index)
    result={}
    for regime in ("uptrend","sideways","downtrend","transition","unknown"):
        mask=labels.eq(regime).to_numpy()
        r=account.iloc[np.flatnonzero(mask)]
        btc=market.iloc[np.flatnonzero(mask)].dropna()
        result[regime]={"days":int(mask.sum()),"account_compounded_return_pct":float((np.prod(1+r)-1)*100),
                        "btc_intraday_compounded_return_pct":float((np.prod(1+btc)-1)*100),
                        "btc_days_with_observed_endpoints":len(btc),
                        "account_down_days":int((r<-1e-10).sum()),"btc_down_days":int((btc<0).sum())}
    return result

def enrich(metrics,trades,daily,base,dreg,start,end,initial=10000):
    metrics.update(previous.extra_metrics(trades,daily,initial))
    metrics.update(previous.bootstrap(trades,start,end))
    metrics["entry_regime_metrics"]=trade_groups(trades)
    metrics["daily_regime_metrics"]=daily_groups(daily,base,dreg,start,end,initial)
    metrics.update(m.benchmark(base,start,end,metrics["average_exposure_pct"],metrics["cost_multiplier"]))
    return metrics

def compact(row):
    return {k:v for k,v in row.items() if k not in ("monthly_returns_pct","yearly_returns_pct")}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    cache=m.ROOT/"data"/"btc-frame.pkl"
    manifest_path=m.ROOT/"data"/"btc-manifest.json"
    if cache.exists() and manifest_path.exists():
        base=pd.read_pickle(cache);manifest=json.loads(manifest_path.read_text())
    else:
        base,manifest=m.download("BTCUSDT")
    (OUT/"data-manifest.json").write_text(json.dumps(manifest,indent=2))
    print("BTC3 DATA",json.dumps({"missing_bars":manifest["missing_bars"],"off_grid_bars":manifest["off_grid_bars"]}),flush=True)
    daily_prices,daily_manifest=market_data.load_daily()
    reconciliation=market_data.reconcile(base,daily_prices)
    (OUT/"daily-data-manifest.json").write_text(json.dumps(daily_manifest,indent=2))
    (OUT/"data-reconciliation.json").write_text(json.dumps(reconciliation,indent=2))
    print("BTC3 RECONCILIATION",json.dumps(reconciliation),flush=True)
    features,dreg=prepare(base,daily_prices)
    markets={"BTCUSDT":base}
    start=pd.Timestamp("2020-01-01",tz="UTC");end=pd.Timestamp("2026-09-01",tz="UTC")
    (OUT/"settings.json").write_text(json.dumps({"configs":CONFIGS,"start":str(start),"end":str(end),
       "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       "engine_sha256":hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
       "daily_data_source":"Official native daily archives; 5m gaps retained for execution",
       "daily_data_code_sha256":hashlib.sha256(Path(market_data.__file__).read_bytes()).hexdigest(),
       "python_numpy":np.__version__,"pandas":pd.__version__,
       "data_frame_sha256":hashlib.sha256(pd.util.hash_pandas_object(base,index=True).values.tobytes()).hexdigest(),
       "classification":"Research-exposed retrospective evaluation"},indent=2))
    rows=[];ledger=[];curves={}
    for config in CONFIGS:
        for cost in (0,1,2):
            metrics,trades,daily=m.simulate(markets,[("BTCUSDT",features[config["name"]])],start,end,cost)
            metrics.update({"config":config["name"],"cost_multiplier":cost})
            enrich(metrics,trades,daily,base,dreg,start,end)
            rows.append(metrics)
            label=config["name"]+f"/cost{cost}"
            ledger.extend(dict(t,run=label) for t in trades);curves[label]=daily
            print("BTC3 SCREEN",json.dumps(compact(metrics)),flush=True)
    # Separate unchanged legacy and daily-data-corrected baselines.
    for label,prices in (("LEGACY",None),("DAILY",daily_prices)):
        baseline=previous.prepare(base,daily_prices=prices)["E-4h-3R"]
        for cost in (1,2):
            metrics,trades,daily=m.simulate(markets,[("BTCUSDT",baseline)],start,end,cost)
            metrics.update({"config":f"BASELINE-{label}-E-4h-3R","cost_multiplier":cost})
            metrics.update(previous.extra_metrics(trades,daily))
            rows.append(metrics)
            curves[metrics["config"]+f"/cost{cost}"]=daily
            ledger.extend(dict(t,run=metrics["config"]+f"/cost{cost}") for t in trades)
            print("BTC3 BASELINE",json.dumps(compact(metrics)),flush=True)
    (OUT/"screen.json").write_text(json.dumps(rows,indent=2))
    pd.DataFrame([compact(r) for r in rows]).to_csv(OUT/"screen.csv",index=False)
    (OUT/"trade-ledger.json").write_text(json.dumps(ledger))
    (OUT/"daily-equity.json").write_text(json.dumps(curves))
    capital={1:10000.,2:10000.};daily_all={1:{},2:{}};trades_all={1:[],2:[]};folds=[]
    begin=start
    while begin<end:
        finish=min(begin+pd.DateOffset(months=6),end)
        training=[]
        for config in CONFIGS:
            metrics,trades,_=m.simulate(markets,[("BTCUSDT",features[config["name"]])],
                                        begin-pd.DateOffset(months=24),begin,1)
            metrics.update({"config":config["name"],
                            "mean_net_r":np.mean([t["net_r"] for t in trades]) if trades else 0})
            training.append(metrics)
        eligible=[r for r in training if r["trades"]>=20 and r["mean_net_r"]>0 and
                  r["total_return_pct"]>0 and r["gap_affected_positions"]==0]
        chosen=sorted(eligible,key=lambda r:(-r["total_return_pct"],r["config"]))[0]["config"] if eligible else None
        (OUT/("training-"+begin.strftime("%Y-%m")+".json")).write_text(json.dumps(training,indent=2))
        for cost in (1,2):
            metrics,trades,daily=m.simulate(markets,[("BTCUSDT",features[chosen])] if chosen else [],
                                           begin,finish,cost,capital[cost])
            capital[cost]*=1+metrics["total_return_pct"]/100
            trades_all[cost].extend(trades);daily_all[cost].update(daily)
            row=dict(metrics,start=str(begin),end=str(finish),cost_multiplier=cost,chosen=chosen)
            folds.append(row);print("BTC3 FOLD",json.dumps(row),flush=True)
        begin=finish
    summaries=[]
    for cost in (1,2):
        ff=[r for r in folds if r["cost_multiplier"]==cost]
        seconds=np.array([(pd.Timestamp(r["end"])-pd.Timestamp(r["start"])).total_seconds() for r in ff])
        trades,daily=trades_all[cost],daily_all[cost]
        metrics=m.stats(trades,daily,10000,0,1,sum(t["gap_affected"] for t in trades),
                        sum(r["rejected_signals"] for r in ff),sum(r["candidate_signals"] for r in ff))
        metrics["cost_multiplier"]=cost
        metrics["average_exposure_pct"]=float(np.average([r["average_exposure_pct"] for r in ff],weights=seconds))
        metrics["cagr_pct"]=100*((capital[cost]/10000)**(365.25*86400/seconds.sum())-1)
        enrich(metrics,trades,daily,base,dreg,start,end)
        summaries.append(metrics);print("BTC3 COMBINED",json.dumps(compact(metrics)),flush=True)
    (OUT/"combined.json").write_text(json.dumps(summaries,indent=2))
    (OUT/"folds.json").write_text(json.dumps(folds,indent=2))
    (OUT/"rolling-trades.json").write_text(json.dumps(trades_all))
    (OUT/"rolling-equity.json").write_text(json.dumps(daily_all))
    dreg.to_csv(OUT/"daily-regimes.csv",index_label="candle_open")
    print("BTC3 COMPLETE",flush=True)

if __name__=="__main__":
    run()
