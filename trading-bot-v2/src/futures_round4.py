"""Execute the predeclared BTCUSDT long/short study and preserve every comparison."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
import futures_data as data
import futures_signals as signals
import futures_engine as engine
import btc_round2 as statistics
import btc_round3 as regimes
import research as shared

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/generated/futures-round-4'
START=pd.Timestamp('2022-01-01',tz='UTC');END=pd.Timestamp('2026-09-01',tz='UTC')

def enrich(row,trades,daily,frames,dreg,start,end,initial=10000):
    row.update(statistics.extra_metrics(trades,daily,initial))
    row.update(statistics.bootstrap(trades,start,end))
    row['entry_regime_metrics']=regimes.trade_groups(trades)
    row['daily_regime_metrics']=regimes.daily_groups(daily,frames['trade'],dreg,start,end,initial)
    row['side_metrics']={}
    for side in ('long','short'):
        t=[x for x in trades if x['side']==side];p=np.array([x['net_pnl'] for x in t]);w=p[p>shared.EPS];l=p[p<-shared.EPS]
        row['side_metrics'][side]={'trades':len(t),'net_pnl':float(p.sum()),'win_rate_pct':100*len(w)/len(t) if t else None,
            'profit_factor':float(w.sum()/-l.sum()) if len(l) else None,'payoff':float(w.mean()/-l.mean()) if len(w) and len(l) else None}
    row['cagr_pct']=100*((1+row['total_return_pct']/100)**(365.25/((end-start).total_seconds()/86400))-1) if row['total_return_pct']>-100 else None
    return row

def compact(row):return {k:v for k,v in row.items() if not isinstance(v,(dict,list))}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    print('FUTURES DATA_VALIDATION',flush=True)
    frames,manifest=data.load()
    (OUT/'data-manifest.json').write_text(json.dumps(manifest,indent=2))
    print('FUTURES DATA_OK',json.dumps({k:{a:v for a,v in x.items() if not isinstance(v,list)} for k,x in manifest['audit'].items()}),flush=True)
    market=engine.Market(frames);features,dreg=signals.prepare(frames['trade'],frames['daily'])
    dreg.to_csv(OUT/'daily-regimes.csv',index_label='candle_open')
    settings={'configs':signals.CONFIGS,'start':str(START),'end_exclusive':str(END),'classification':'Research-exposed retrospective evaluation',
       'fee':engine.FEE,'slippage':engine.SLIP,'risk_fraction':engine.RISK,'maintenance':engine.MAINTENANCE,
       'liquidation_fee':engine.LIQUIDATION_FEE,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,
       'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').glob('*.py'))}}
    (OUT/'settings.json').write_text(json.dumps(settings,indent=2))
    rows=[];ledger=[];equities={}
    scenarios=[(1,5,d,.01) for d in ('long','short','both')]+[(c,5,'both',.01) for c in (0,2)]+[(1,l,'both',.01) for l in (1,2,3)]+[(1,5,'both',.02)]
    for c in signals.CONFIGS:
        for cost,lev,direction,maintenance in scenarios:
            label=f"{c['name']}/cost{cost}/cap{lev}/{direction}/mm{maintenance}"
            row,trades,daily=engine.simulate(market,features[c['name']],START,END,cost,lev,direction,maintenance=maintenance)
            row.update({'config':c['name'],'run':label});enrich(row,trades,daily,frames,dreg,START,END)
            rows.append(row);ledger.extend(dict(t,run=label) for t in trades);equities[label]=daily
            print('FUTURES SCREEN',json.dumps(compact(row)),flush=True)
    (OUT/'screen.json').write_text(json.dumps(rows,indent=2));pd.DataFrame([compact(r) for r in rows]).to_csv(OUT/'screen.csv',index=False)
    (OUT/'trade-ledger.json').write_text(json.dumps(ledger));(OUT/'daily-equity.json').write_text(json.dumps(equities))
    capitals={1:10000.,2:10000.};all_trades={1:[],2:[]};all_equity={1:{},2:{}};folds=[]
    begin=START
    while begin<END:
        finish=min(begin+pd.DateOffset(months=6),END);training=[]
        for c in signals.CONFIGS:
            row,_,_=engine.simulate(market,features[c['name']],begin-pd.DateOffset(months=24),begin)
            row['config']=c['name'];training.append(row)
        eligible=[r for r in training if r['trades']>=20 and (r['mean_net_r'] or 0)>0 and r['total_return_pct']>0 and (r['profit_factor'] or 0)>1.1 and r['gap_affected_positions']==0 and r['liquidations']==0]
        chosen=sorted(eligible,key=lambda r:(-r['total_return_pct'],r['config']))[0]['config'] if eligible else None
        (OUT/f'training-{begin:%Y-%m}.json').write_text(json.dumps(training,indent=2))
        for cost in (1,2):
            row,t,d=engine.simulate(market,features[chosen] if chosen else None,begin,finish,cost,initial=capitals[cost])
            row.update({'chosen':chosen,'start':str(begin),'end':str(finish)})
            capitals[cost]*=1+row['total_return_pct']/100;all_trades[cost].extend(t);all_equity[cost].update(d);folds.append(row)
            print('FUTURES FOLD',json.dumps(compact(row)),flush=True)
        begin=finish
    combined=[]
    for cost in (1,2):
        tt=all_trades[cost];dd=all_equity[cost];ff=[x for x in folds if x['cost_multiplier']==cost]
        row=shared.stats(tt,dd,10000,0,1,sum(t['gap_affected'] for t in tt),sum(x['rejected_signals'] for x in ff),sum(x['candidate_signals'] for x in ff))
        durations=[(pd.Timestamp(x['end'])-pd.Timestamp(x['start'])).total_seconds() for x in ff]
        row.update({'cost_multiplier':cost,'leverage_ceiling':5,'direction':'both','maintenance_rate':.01,
          'average_exposure_pct':float(np.average([x['average_exposure_pct'] for x in ff],weights=durations)),
          'max_entry_leverage':max(x['max_entry_leverage'] for x in ff),'max_observed_open_leverage':max(x['max_observed_open_leverage'] for x in ff),
          'funding_cash':sum(x['funding_cash'] for x in ff),'funding_ambiguous_events':sum(x['funding_ambiguous_events'] for x in ff),
          'liquidations':sum(x['liquidations'] for x in ff),'leverage_exits':sum(x['leverage_exits'] for x in ff)})
        enrich(row,tt,dd,frames,dreg,START,END);combined.append(row)
        print('FUTURES COMBINED',json.dumps(compact(row)),flush=True)
    (OUT/'combined.json').write_text(json.dumps(combined,indent=2));(OUT/'folds.json').write_text(json.dumps(folds,indent=2))
    (OUT/'rolling-trades.json').write_text(json.dumps(all_trades));(OUT/'rolling-equity.json').write_text(json.dumps(all_equity))
    print('FUTURES COMPLETE',flush=True)

if __name__=='__main__':run()
