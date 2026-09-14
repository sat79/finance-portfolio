"""Historical US macro forecasting: chronological validation and untouched test.
Data are a revised 2009 vintage, so this is pseudo-out-of-sample, not real-time.
"""
from pathlib import Path
import argparse,json,hashlib,warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.vecm import VECM,select_coint_rank
from statsmodels.tsa.stattools import adfuller,kpss
from statsmodels.stats.diagnostic import acorr_ljungbox
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]


def load_data(path):
    df=pd.read_csv(path)
    required=['year','quarter','realgdp','realcons','realinv']
    if not set(required).issubset(df): raise ValueError('Missing required macro columns')
    v=df[required].apply(pd.to_numeric,errors='raise')
    if not np.isfinite(v).all().all() or not v.year.eq(v.year.astype(int)).all() or not v.quarter.isin([1,2,3,4]).all():
        raise ValueError('Invalid year, quarter or numeric value')
    ix=pd.PeriodIndex.from_fields(year=v.year.astype(int),quarter=v.quarter.astype(int),freq='Q')
    if ix.has_duplicates or not ix.is_monotonic_increasing or not ix.equals(pd.period_range(ix[0],ix[-1],freq='Q')):
        raise ValueError('Expected unique, contiguous, increasing quarters')
    levels=v[['realgdp','realcons','realinv']].set_axis(ix)
    if len(levels)<100 or (levels<=0).any().any(): raise ValueError('Need at least 100 positive quarterly levels')
    return np.log(levels)


def fit_arima(history,order):
    # Percentage log levels improve numerical scaling; forecasts are divided by 100.
    fit=ARIMA(100*history,order=order,trend='t').fit(method_kwargs={'maxiter':1000})
    if not fit.mle_retvals.get('converged',False): raise RuntimeError(f'ARIMA {order} did not converge')
    return fit


def diagnostics(train):
    rows=[]
    for name in train:
        for transform,x,reg in [('log level',train[name],'ct'),('log difference',train[name].diff().dropna(),'c')]:
            adf=adfuller(x,regression=reg,autolag='AIC',maxlag=8,result_object=False)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always'); kp=kpss(x,regression=reg,nlags='auto',result_object=False)
            rows.append(dict(series=name,transform=transform,deterministic=reg,adf_stat=float(adf[0]),adf_p=float(adf[1]),adf_lags=int(adf[2]),
                             kpss_stat=float(kp[0]),kpss_p=float(kp[1]),kpss_lags=int(kp[2]),kpss_warning='; '.join(str(w.message) for w in caught)))
    return rows


def choose_spec(train):
    aics=[]
    # Small declared candidate set; no search over the final test period.
    for order in [(0,1,0),(1,1,0),(0,1,1),(1,1,1),(2,1,0)]:
        try:
            f=fit_arima(train.realgdp,order);aics.append(dict(order=list(order),aic=float(f.aic),status='converged'))
        except RuntimeError as e: aics.append(dict(order=list(order),aic=None,status=str(e)))
    eligible=[a for a in aics if a['aic'] is not None]
    if not eligible: raise RuntimeError('No converged ARIMA candidate')
    order=tuple(min(eligible,key=lambda a:a['aic'])['order'])
    # VAR on first differences; VECM adds level error correction with same difference lag.
    lag=max(1,int(VAR(train.diff().dropna()).select_order(maxlags=4,trend='c').selected_orders['bic']))
    rank_test=select_coint_rank(train,det_order=0,k_ar_diff=lag,method='trace',signif=.05)
    rank=int(rank_test.rank)
    if rank==train.shape[1]:
        raise RuntimeError('Full rank conflicts with the I(1) VECM design; review specification')
    return order,lag,rank,aics,rank_test


def forecast(history,order,lag,rank):
    previous=float(history.realgdp.iloc[-1])
    af=fit_arima(history.realgdp,order);pred=af.get_forecast(1);ci=pred.conf_int().iloc[0]
    vf=VAR(history.diff().dropna()).fit(lag,trend='c')
    point,lo,hi=vf.forecast_interval(history.diff().dropna().to_numpy()[-lag:],steps=1,alpha=.05)
    ef=VECM(history,k_ar_diff=lag,coint_rank=rank,deterministic='co').fit()
    ep,el,eu=ef.predict(steps=1,alpha=.05)
    return [dict(model='ARIMA',forecast=400*(float(pred.predicted_mean.iloc[0])/100-previous),lower=400*(float(ci.iloc[0])/100-previous),upper=400*(float(ci.iloc[1])/100-previous)),
            dict(model='VAR',forecast=400*float(point[0,0]),lower=400*float(lo[0,0]),upper=400*float(hi[0,0])),
            dict(model='VECM',forecast=400*(float(ep[0,0])-previous),lower=400*(float(el[0,0])-previous),upper=400*(float(eu[0,0])-previous)),
            dict(model='Historical mean',forecast=400*float(history.realgdp.diff().dropna().mean()),lower=None,upper=None),
            dict(model='Random walk',forecast=0.,lower=None,upper=None)]


def evaluate(logs,order,lag,rank,validation_start='1990Q1',test_start='2000Q1'):
    rows=[]
    for i in range(len(logs)):
        if logs.index[i]<pd.Period(validation_start): continue
        history=logs.iloc[:i]
        actual=400*float(logs.realgdp.iloc[i]-history.realgdp.iloc[-1])
        for f in forecast(history,order,lag,rank):
            f.update(quarter=str(logs.index[i]),history_end=str(history.index[-1]),actual=actual,
                     split='validation' if logs.index[i]<pd.Period(test_start) else 'test')
            rows.append(f)
    return pd.DataFrame(rows)


def metrics(df):
    rows=[]
    for (split,model),g in df.groupby(['split','model']):
        err=g.forecast-g.actual;available=g.lower.notna()
        rows.append(dict(split=split,model=model,n=len(g),rmse=float(np.sqrt(np.mean(err**2))),mae=float(np.abs(err).mean()),bias=float(err.mean()),
            interval_coverage=float(((g.actual>=g.lower)&(g.actual<=g.upper))[available].mean()) if available.any() else None))
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',type=Path,default=ROOT/'data/us_macro.csv');ap.add_argument('--output',type=Path,default=ROOT/'reports')
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    logs=load_data(args.data);train=logs.loc[:'1989Q4']
    if len(train)<100 or logs.index[-1]<pd.Period('2001Q1'): raise ValueError('Dataset must span the fixed train and test periods')
    # Investment rejects a trend unit root in training; exclude it from the I(1) system.
    stationarity=diagnostics(train)
    system=logs[['realgdp','realcons']]
    train=system.loc[:'1989Q4']
    order,lag,rank,aics,rank_test=choose_spec(train)
    results=evaluate(system,order,lag,rank);scores=metrics(results)
    valid=[s for s in scores if s['split']=='validation']
    best=min(s['rmse'] for s in valid)
    priority=['Historical mean','Random walk','ARIMA','VAR','VECM']
    champion=min([s for s in valid if np.isclose(s['rmse'],best,rtol=0,atol=1e-8)],key=lambda s:priority.index(s['model']))['model']
    results.to_csv(args.output/'forecasts.csv',index=False,float_format='%.10g')
    pd.DataFrame(scores).to_csv(args.output/'model_comparison.csv',index=False,float_format='%.10g')
    af=fit_arima(train.realgdp,order)
    # Omit initial diffuse/integrated residual before residual diagnostics.
    lb=float(acorr_ljungbox(af.resid.iloc[10:],lags=[8],model_df=order[0]+order[2],return_df=True).lb_pvalue.iloc[0])
    summary=dict(data_sha256=hashlib.sha256(args.data.read_bytes()).hexdigest(),quarters=len(logs),train_end='1989Q4',validation='1990Q1–1999Q4',test='2000Q1–2009Q3',
      target='US real GDP annualised log growth: 400*log(GDP_t/GDP_t-1), percent',arima_order=list(order),arima_candidates=aics,var_difference_lags=lag,
      vecm_difference_lags=lag,cointegration_rank=rank,johansen_trace=rank_test.test_stats.tolist(),johansen_critical=rank_test.crit_vals.tolist(),
      rank_note='Fixed from training sample; unrestricted constant, no deterministic time trend in VECM',stationarity=stationarity,system_variables=['realgdp','realcons'],excluded_variable='realinv: training diagnostics support trend stationarity, so excluded from I(1) system',
      train_arima_ljung_box_p=lb,validation_selected_model=champion,scores=scores)
    (args.output/'results.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    fig,ax=plt.subplots(figsize=(10,4.8)); actual=results[(results.model=='ARIMA')&(results.split=='test')]
    dates=pd.PeriodIndex(actual.quarter,freq='Q').to_timestamp();ax.plot(dates,actual.actual,color='#142c45',lw=2,label='Observed GDP growth')
    for name,color in [(champion,'#b47733'),('ARIMA','#7a939b')]:
        if name=='ARIMA' and champion=='ARIMA': continue
        g=results[(results.model==name)&(results.split=='test')];ax.plot(dates,g.forecast,color=color,lw=1.4,label=name)
    ax.axhline(0,color='#d3d9df',lw=.8);ax.set(ylabel='Annualised log growth (%)',title='GDP forecasts • final historical test, 2000–2009');ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(args.output/'forecast-comparison.png',dpi=180);plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
