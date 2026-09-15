"""Eight predeclared futures candidates. Signal calculations only; no account arithmetic."""
import numpy as np
import pandas as pd
import research as spot
import btc_round2 as prior
import btc_round3 as regime_rules
from market_data import daily_indicators

CONFIGS=[{'name':f'{family}-{tf}-{exit_}','family':family,'tf':tf,'exit_policy':exit_,
          'rr':3 if exit_ in ('adaptive','3R') else 2,'atr_multiple':1.5 if family=='FIB' else 2,
          'holding_days':5 if tf=='1h' else 20}
         for family in ('FIB','BREAK') for tf in ('1h','4h')
         for exit_ in (('2R','adaptive') if family=='FIB' else ('2R','3R'))]

def signed_prices(prices,side):
    """Reflect OHLC about zero for short *signal geometry*, never for futures P&L."""
    if side==1:return prices.copy()
    return pd.DataFrame({'open':-prices.open,'high':-prices.low,'low':-prices.high,'close':-prices.close},index=prices.index)

def prepare(base,daily):
    dreg=regime_rules.regimes(daily_indicators(daily))
    output={c['name']:{'config':c,'sides':{}} for c in CONFIGS}
    for tf in ('1h','4h'):
        raw=spot.indicators(base,tf)
        reg=regime_rules.eligible_regime(raw,dreg)
        for side in (1,-1):
            f=raw.copy()
            for col in ('open','high','low','close'):f[col]=signed_prices(raw,side)[col]
            trend='uptrend' if side==1 else 'downtrend'
            trend_gate=reg.eq(trend).to_numpy()
            rsi=prior.rsi(f.close,14)
            mean=f.close.rolling(20).mean()
            lower=mean-2*f.close.rolling(20).std(ddof=0)
            range_signal=((f.low<lower)&(f.close>lower)&(f.close>f.open)&(rsi<40)&(rsi>rsi.shift())&reg.eq('sideways')).to_numpy()
            fib=regime_rules.fib_signals(f,require_div=True,allowed=trend_gate)[0]
            ema21=f.close.ewm(span=21,adjust=False,min_periods=21).mean()
            ema55=f.close.ewm(span=55,adjust=False,min_periods=55).mean()
            level=f.high.shift().rolling(20).max()
            breakout=((f.close>level)&(f.close.shift()<=level.shift())&(f.close>ema21)&(ema21>ema55)).to_numpy()&trend_gate
            structure=(f.low.rolling(5).min()-.25*f.atr)*side
            for c in [x for x in CONFIGS if x['tf']==tf]:
                signal=(fib|range_signal) if c['family']=='FIB' else breakout
                event=pd.DataFrame({'signal':signal&f.atr.notna().to_numpy(),'structure':structure,'atr':f.atr,
                   'regime':reg,'completed_favorable':raw.high if side==1 else raw.low,
                   'mean_exit':(f.close>=mean).to_numpy(),
                   'trend_exit':(f.close<ema21).to_numpy() if c['family']=='BREAK' else False})
                event.index=pd.to_datetime(f.end.to_numpy(),utc=True)
                event=event.reindex(base.index)
                features={k:event[k].to_numpy() for k in ('structure','atr','completed_favorable')}
                features.update({k:event[k].eq(True).to_numpy() for k in ('signal','mean_exit','trend_exit')})
                features['regime']=event.regime.fillna('').to_numpy()
                output[c['name']]['sides'][side]=features
    return output,dreg
