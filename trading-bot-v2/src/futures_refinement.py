"""Post-round-4 refinement: let prior data choose long-only, short-only or both.

This is another research trial after observing round 4; it is not untouched validation.
The entry/exit rules, risk budget and eligibility thresholds remain unchanged.
"""
import json
import numpy as np
import pandas as pd
import futures_round4 as original
import futures_data as data
import futures_signals as signals
import futures_engine as engine
import research as shared

OUT=original.ROOT/'reports/generated/futures-direction-refinement'

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    frames,manifest=data.load();market=engine.Market(frames)
    features,dreg=signals.prepare(frames['trade'],frames['daily'])
    capital={1:10000.,2:10000.};trades={1:[],2:[]};equity={1:{},2:{}};folds=[]
    begin=original.START
    while begin<original.END:
        finish=min(begin+pd.DateOffset(months=6),original.END);training=[]
        for c in signals.CONFIGS:
            for direction in ('long','short','both'):
                row,_,_=engine.simulate(market,features[c['name']],begin-pd.DateOffset(months=24),begin,direction=direction)
                row['config']=c['name'];training.append(row)
        eligible=[r for r in training if r['trades']>=20 and (r['mean_net_r'] or 0)>0 and r['total_return_pct']>0 and (r['profit_factor'] or 0)>1.1 and r['gap_affected_positions']==0 and r['liquidations']==0]
        chosen=sorted(eligible,key=lambda r:(-r['total_return_pct'],r['config'],r['direction']))[0] if eligible else None
        (OUT/f'training-{begin:%Y-%m}.json').write_text(json.dumps(training,indent=2))
        for cost in (1,2):
            direction=chosen['direction'] if chosen else 'both';name=chosen['config'] if chosen else None
            row,t,d=engine.simulate(market,features[name] if name else None,begin,finish,cost,direction=direction,initial=capital[cost])
            row.update({'chosen':name,'start':str(begin),'end':str(finish)});folds.append(row)
            capital[cost]*=1+row['total_return_pct']/100;trades[cost].extend(t);equity[cost].update(d)
            print('REFINEMENT FOLD',json.dumps(row),flush=True)
        begin=finish
    combined=[]
    for cost in (1,2):
        tt=trades[cost];dd=equity[cost];ff=[r for r in folds if r['cost_multiplier']==cost]
        row=shared.stats(tt,dd,10000,0,1,sum(t['gap_affected'] for t in tt),sum(r['rejected_signals'] for r in ff),sum(r['candidate_signals'] for r in ff))
        seconds=[(pd.Timestamp(r['end'])-pd.Timestamp(r['start'])).total_seconds() for r in ff]
        row.update({'cost_multiplier':cost,'leverage_ceiling':5,'direction':'selected from prior data','maintenance_rate':.01,
          'average_exposure_pct':float(np.average([r['average_exposure_pct'] for r in ff],weights=seconds)),
          'max_entry_leverage':max(r['max_entry_leverage'] for r in ff),'max_observed_open_leverage':max(r['max_observed_open_leverage'] for r in ff),
          'funding_cash':sum(r['funding_cash'] for r in ff),'funding_ambiguous_events':sum(r['funding_ambiguous_events'] for r in ff),
          'liquidations':sum(r['liquidations'] for r in ff),'leverage_exits':sum(r['leverage_exits'] for r in ff)})
        original.enrich(row,tt,dd,frames,dreg,original.START,original.END);combined.append(row)
        print('REFINEMENT COMBINED',json.dumps(original.compact(row)),flush=True)
    (OUT/'combined.json').write_text(json.dumps(combined,indent=2));(OUT/'folds.json').write_text(json.dumps(folds,indent=2))
    (OUT/'rolling-trades.json').write_text(json.dumps(trades));(OUT/'rolling-equity.json').write_text(json.dumps(equity))
    print('REFINEMENT COMPLETE',flush=True)

if __name__=='__main__':run()
