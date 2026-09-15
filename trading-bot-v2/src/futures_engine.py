"""One-position linear USDT futures replay with signed cash flows and conservative OHLC fills.

Cross-equity margin is a research approximation, not an exchange liquidation replica.
Contract trade prices execute orders. Mark prices value margin. Funding retains event times.
"""
import math
import numpy as np
import pandas as pd
import research as shared

FEE=.0005; SLIP=.0002; RISK=.005
MAX_LEVERAGE=5.; MAINTENANCE=.01; LIQUIDATION_FEE=.005
STEP=pd.Timedelta(minutes=5).value

def quantity(equity,entry,stop,side,ceiling,fee,slip,step=.001):
    if not (0<ceiling<=MAX_LEVERAGE):raise ValueError('Leverage ceiling must be in (0,5]')
    if equity<=0 or entry<=0 or stop<=0 or side not in (1,-1) or side*(entry-stop)<=0:return 0.,0.
    exit_fill=stop*(1-side*slip)
    unit_risk=side*(entry-exit_fill)+fee*(entry+exit_fill)
    # Entry fees reduce equity. Account must retain enough cash for initial margin plus fees.
    cap=ceiling*equity/(entry*(1+ceiling*fee))
    q=math.floor(min(equity*RISK/unit_risk,cap)/step)*step
    if q*entry<10:return 0.,unit_risk
    return q,unit_risk

def protective_fill(bar,stop,target,side):
    o,h,l,c=bar
    if side==1:
        if o<=stop:return o,'gap_stop'
        if l<=stop:return stop,'stop'
        if h>=target:return target,'target' # No favorable gap improvement assumed.
    else:
        if o>=stop:return o,'gap_stop'
        if h>=stop:return stop,'stop'
        if l<=target:return target,'target'
    return None,None

def ratchet(p,favorable,atr,fee,slip):
    s=p['side'];p['best']=max(p['best'],s*favorable)
    advance=p['best']-s*p['entry']
    stop=s*p['stop']
    if advance>=p['distance']:
        # Solve signed gross P&L minus both commissions = zero, before future funding.
        raw=p['entry']*(s+fee)/((s-fee)*(1-s*slip))
        stop=max(stop,s*raw)
    if advance>=2*p['distance']:stop=max(stop,p['best']-2*atr)
    p['stop']=s*stop

def funding_cash(side,qty,mark,rate):return -side*qty*mark*rate

class Market:
    def __init__(self,frames):
        self.index=frames['trade'].index
        self.trade=frames['trade'][['open','high','low','close']].to_numpy()
        self.mark=frames['mark'][['open','high','low','close']].to_numpy()
        self.funding={}
        for t,row in frames['funding'].iterrows():
            i=self.index.searchsorted(t.floor('5min'))
            if i<len(self.index):self.funding.setdefault(i,[]).append((t,float(row.rate)))
        self.days=pd.date_range(self.index[0].floor('1d'),self.index[-1].floor('1d'),freq='1d')

def simulate(market,feature,start,end,cost=1,ceiling=5,direction='both',initial=10000.,maintenance=MAINTENANCE):
    if not (0<ceiling<=5):raise ValueError('Requested leverage exceeds permitted ceiling')
    if direction not in ('both','long','short'):raise ValueError('Unknown direction')
    idx=market.index;first=idx.searchsorted(pd.Timestamp(start));last=idx.searchsorted(pd.Timestamp(end))
    fee=FEE*cost;slip=SLIP*cost;cash=float(initial);p=None;trades=[];daily={}
    rejected=candidates=0;max_equity=initial;max_dd=0.;max_entry_leverage=0.;max_observed_leverage=0.
    exposure_sum=0.;funding_ambiguous=0;liquidations=0;deleverages=0;halted=False
    allowed=(1,-1) if direction=='both' else ((1,) if direction=='long' else (-1,))
    if feature is None:events=np.array([],dtype=int)
    else:events=np.flatnonzero(np.logical_or.reduce([feature['sides'][s]['signal'] for s in allowed]))
    def close(raw,when,reason):
        nonlocal cash,p,liquidations,deleverages
        s=p['side'];fill=raw*(1-s*slip);commission=p['qty']*fill*fee
        gross=s*p['qty']*(fill-p['entry']);extra=p['qty']*raw*LIQUIDATION_FEE if reason=='liquidation' else 0.
        cash+=gross-commission-extra
        net=gross-p['entry_fee']-commission-extra+p['funding']
        trades.append({'symbol':'BTCUSDT','strategy':p['name'],'side':'long' if s==1 else 'short',
          'entry_regime':p['regime'],'entry_time':p['time'],'exit_time':str(when),
          'entry_price':p['entry'],'exit_price':fill,'initial_stop':p['initial_stop'],
          'initial_quantity':p['qty'],'entry_leverage':p['entry_leverage'],
          'net_pnl':net,'net_r':net/p['planned_risk'],'planned_risk':p['planned_risk'],
          'funding_cash':p['funding'],'funding_events':p['funding_events'],
          'funding_ambiguous_events':p['funding_ambiguous'],'gap_affected':p['gap'],
          'costs':p['entry_fee']+commission+extra+p['slippage_cost']+p['qty']*abs(fill-raw),
          'fills':[{'time':str(when),'price':fill,'quantity':p['qty'],'reason':reason}]})
        liquidations+=reason=='liquidation';deleverages+=reason=='leverage_exit';p=None
    def apply_funding(event,i,ambiguous):
        nonlocal cash,funding_ambiguous
        t,rate=event;s=p['side'];mark=market.mark[i,0]
        if not np.isfinite(mark):p['gap']=True;return
        flow=funding_cash(s,p['qty'],mark,rate)
        # Intrabar settlement price unknown: use adverse mark extreme for debits and
        # smaller absolute mark extreme for credits. Direction/order ambiguity is flagged.
        reference=market.mark[i,1] if flow<0 else market.mark[i,2]
        if ambiguous:flow=funding_cash(s,p['qty'],reference,rate)
        cash+=flow;p['funding']+=flow;p['funding_events']+=1
        p['funding_ambiguous']+=int(ambiguous);funding_ambiguous+=int(ambiguous)
    i=first
    while i<last:
        if p is None:
            k=np.searchsorted(events,i)
            if k==len(events) or events[k]>=last:break
            i=int(events[k])
        when=idx[i];bar=market.trade[i];mark=market.mark[i];exited=False
        valid=np.isfinite(bar).all() and np.isfinite(mark).all()
        if not valid:
            if p:p['gap']=True
            i+=1;continue
        settlements=market.funding.get(i,[])
        exact=[e for e in settlements if e[0]==when]
        intrabar=[e for e in settlements if e[0]!=when]
        if p:
            for e in exact:apply_funding(e,i,False)
            # Conservative intrabar debit even if an exit may precede the event.
            for e in intrabar:
                if funding_cash(p['side'],p['qty'],mark[0],e[1])<0:apply_funding(e,i,True)
            s=p['side'];f=feature['sides'][s]
            equity_open=cash+s*p['qty']*(mark[0]-p['entry'])
            gross=p['qty']*mark[0]
            lev=gross/max(equity_open,1e-9);max_observed_leverage=max(max_observed_leverage,lev)
            worst=mark[2] if s==1 else mark[1]
            equity_worst=cash+s*p['qty']*(worst-p['entry'])
            # Cross-wallet maintenance stress, including a liquidation-fee reserve.
            if equity_open<=(maintenance+LIQUIDATION_FEE)*p['qty']*mark[0]:
                close(bar[0],when,'liquidation');exited=True
            elif lev>MAX_LEVERAGE:
                close(bar[0],when,'leverage_exit');exited=True
            else:
                if feature['config']['exit_policy']=='adaptive' and np.isfinite(f['completed_favorable'][i]) and np.isfinite(f['atr'][i]):
                    ratchet(p,f['completed_favorable'][i],f['atr'][i],fee,slip)
                raw,reason=protective_fill(bar,p['stop'],p['target'],s)
                regime_change=f['regime'][i] and f['regime'][i]!=p['regime']
                mean_exit=(feature['config']['exit_policy']=='adaptive' and p['regime']=='sideways' and f['mean_exit'][i])
                time_exit=(when.value-p['entry_ns'])>=feature['config']['holding_days']*86400*1e9
                # Opening gap protection precedes discretionary next-open exits;
                # otherwise discretionary open exits precede later intrabar barriers.
                if reason=='gap_stop':close(raw,when,reason);exited=True
                elif regime_change or mean_exit or f['trend_exit'][i] or time_exit:
                    close(bar[0],when,'rule_or_time');exited=True
                elif equity_worst<=(maintenance+LIQUIDATION_FEE)*p['qty']*worst:
                    close(bar[2] if s==1 else bar[1],when,'liquidation');exited=True
                elif raw is not None:close(raw,when,reason);exited=True
            if p:
                # Credits only if position survived the entire event candle.
                for e in intrabar:
                    if funding_cash(p['side'],p['qty'],mark[0],e[1])>=0:apply_funding(e,i,True)
        if cash<=0 and p is None:halted=True;daily[str(when.date())]=cash;break
        if feature is not None:
            signaled=[s for s in allowed if feature['sides'][s]['signal'][i]]
            candidates+=len(signaled)
            if signaled and (p is not None or exited or len(signaled)>1 or intrabar):rejected+=len(signaled)
            elif len(signaled)==1:
                s=signaled[0];f=feature['sides'][s];c=feature['config']
                entry=bar[0]*(1+s*slip);atr=f['atr'][i];structure=f['structure'][i]
                distance=max(c['atr_multiple']*atr,s*(entry-structure));stop=entry-s*distance
                if not np.isfinite(distance) or distance<=0 or stop<=0 or distance<3*entry*2*(fee+slip):rejected+=1
                else:
                    q,unit=quantity(cash,entry,stop,s,ceiling,fee,slip)
                    target=entry+s*c['rr']*distance
                    if q<=0 or target<=0:rejected+=1
                    else:
                        paid=q*entry*fee;lev=q*entry/(cash-paid)
                        assert lev<=ceiling+1e-9
                        p={'side':s,'qty':q,'entry':entry,'initial_stop':stop,'stop':stop,'target':target,
                           'distance':distance,'entry_fee':paid,'funding':0.,'funding_events':0,'funding_ambiguous':0,
                           'entry_leverage':lev,'time':str(when),'entry_ns':when.value,'name':c['name'],
                           'regime':f['regime'][i],'best':s*entry,'planned_risk':q*unit,'gap':False,
                           'slippage_cost':q*abs(entry-bar[0])}
                        cash-=paid;max_entry_leverage=max(max_entry_leverage,lev)
                        # Stops/targets can fill during the entry bar; no adaptive lookahead.
                        raw,reason=protective_fill(bar,stop,target,s)
                        worst=mark[2] if s==1 else mark[1]
                        if cash+s*q*(worst-entry)<=(maintenance+LIQUIDATION_FEE)*q*worst:
                            close(bar[2] if s==1 else bar[1],when,'liquidation')
                        elif raw is not None:close(raw,when,reason)
        equity=cash+(p['side']*p['qty']*(mark[3]-p['entry']) if p else 0.)
        if p:exposure_sum+=p['qty']*mark[3]/max(equity,1e-9)
        max_equity=max(max_equity,equity);max_dd=min(max_dd,equity/max_equity-1)
        daily[str(when.date())]=equity
        i+=1
    if p:
        # Do not invent an exit through missing endpoint data.
        if not np.isfinite(market.trade[last-1]).all():raise ValueError('Cannot liquidate at missing final candle')
        close(market.trade[last-1,3],pd.Timestamp(end),'boundary')
        daily[str(idx[last-1].date())]=cash
    calendar=pd.date_range(pd.Timestamp(start).floor('1d'),(pd.Timestamp(end)-pd.Timedelta(nanoseconds=1)).floor('1d'),freq='1d')
    d=pd.Series(daily,dtype=float);d.index=pd.to_datetime(d.index,utc=True)
    d=d.reindex(calendar).ffill().fillna(initial)
    metrics=shared.stats(trades,{str(t.date()):float(v) for t,v in d.items()},initial,exposure_sum,last-first,
                         sum(t['gap_affected'] for t in trades),rejected,candidates)
    metrics.update({'max_drawdown_5m_close_pct':max_dd*100,'max_entry_leverage':max_entry_leverage,
       'max_observed_open_leverage':max_observed_leverage,'funding_cash':sum(t['funding_cash'] for t in trades),
       'funding_ambiguous_events':funding_ambiguous,'liquidations':liquidations,'leverage_exits':deleverages,
       'bankrupt':halted,'cost_multiplier':cost,'leverage_ceiling':ceiling,'direction':direction,
       'maintenance_rate':maintenance,'mean_net_r':np.mean([t['net_r'] for t in trades]) if trades else None})
    assert abs(metrics['accounting_error'])<1e-6,'Cash accounting failed'
    return metrics,trades,{str(t.date()):float(v) for t,v in d.items()}
