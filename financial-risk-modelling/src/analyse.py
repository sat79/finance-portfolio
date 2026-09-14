"""Historical market-risk study. All risk numbers use percent log-return loss.
Run from any directory; no network request is made during analysis.
"""
from pathlib import Path
import argparse
import json
import hashlib
import warnings
import numpy as np
import pandas as pd
from scipy.stats import t, norm, chi2, binomtest
from scipy.special import xlogy
from arch import arch_model
from statsmodels.stats.diagnostic import acorr_ljungbox
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]


def load_prices(path):
    df = pd.read_csv(path)
    if set(df.columns) != {'date', 'adjusted_close'}:
        raise ValueError('Expected date and adjusted_close columns only')
    df['date'] = pd.to_datetime(df['date'], errors='raise')
    x = pd.to_numeric(df['adjusted_close'], errors='raise')
    if df.date.isna().any() or df.date.duplicated().any() or not df.date.is_monotonic_increasing:
        raise ValueError('Dates must be valid, unique and increasing')
    if len(x) < 1100 or not np.isfinite(x).all() or (x <= 0).any():
        raise ValueError('Need at least 1100 finite, positive prices')
    return pd.Series(x.to_numpy(), index=df.date, name='adjusted_close')


def empirical_risk(loss, confidence):
    """Integral of empirical quantile over upper tail; fractional boundary mass.
    This definition works when n*(1-confidence) is not an integer.
    """
    x = np.sort(np.asarray(loss, dtype=float))
    if len(x) == 0 or not np.isfinite(x).all() or not 0 < confidence < 1:
        raise ValueError('Finite nonempty losses and confidence in (0,1) required')
    var = x[int(np.ceil(confidence * len(x))) - 1]
    mass = len(x) * (1 - confidence)
    k = int(np.floor(mass))
    fraction = mass - k
    es = (x[len(x)-k:].sum() + fraction*x[len(x)-k-1]) / mass if k < len(x) else x.mean()
    return float(var), float(es)


def student_risk(mu, sigma, nu, confidence):
    if not all(np.isfinite([mu, sigma, nu, confidence])) or sigma <= 0 or nu <= 2 or not 0 < confidence < 1:
        raise ValueError('Invalid Student-t distribution parameters')
    q = t.ppf(confidence, nu)
    scale = np.sqrt((nu-2)/nu)
    return (-mu + sigma*scale*q,
            -mu + sigma*scale*(nu+q*q)/(nu-1)*t.pdf(q, nu)/(1-confidence))


def coverage(loss, var, confidence):
    hit = np.asarray(loss) > np.asarray(var)
    n, k = len(hit), int(hit.sum())
    p, observed = 1-confidence, k/n
    lr = 2*(xlogy(k, observed) + xlogy(n-k, 1-observed) - xlogy(k,p) - xlogy(n-k,1-p))
    counts = np.zeros((2,2), dtype=int)
    for a,b in zip(hit[:-1].astype(int), hit[1:].astype(int)): counts[a,b] += 1
    ll_ind = 0.
    for row in counts:
        total = row.sum()
        if total: ll_ind += xlogy(row[1], row[1]/total)+xlogy(row[0],row[0]/total)
    total = counts.sum(); pooled = counts[:,1].sum()/total
    ll_pool = xlogy(counts[:,1].sum(),pooled)+xlogy(counts[:,0].sum(),1-pooled)
    lr_ind = max(0.,float(2*(ll_ind-ll_pool)))
    ci = binomtest(k,n,p).proportion_ci()
    # An unvisited transition row makes the asymptotic independence test unidentified.
    identified = bool((counts.sum(axis=1)>0).all())
    return dict(n=n,exceptions=k,expected=n*p,exception_rate=observed,
                coverage_ci_low=ci.low,coverage_ci_high=ci.high,kupiec_p=float(chi2.sf(max(0,float(lr)),1)),
                independence_p=float(chi2.sf(lr_ind,1)) if identified else None,
                conditional_coverage_p=float(chi2.sf(max(0,float(lr))+lr_ind,2)) if identified else None,
                transitions=counts.tolist())


def backtest(r, start=1000, window=1000, refit_every=63):
    if start < window or len(r) <= start: raise ValueError('Insufficient estimation history')
    rows, fits = [], []
    for i in range(start,len(r)):
        past = r.iloc[i-window:i]
        if (i-start) % refit_every == 0:
            fit = arch_model(past, mean='Constant', vol='GARCH', p=1,q=1,dist='t',rescale=False).fit(disp='off',show_warning=True)
            if fit.convergence_flag: raise RuntimeError(f'GARCH failed at {r.index[i]}')
            mu,omega,a,b,nu = [float(fit.params[k]) for k in ['mu','omega','alpha[1]','beta[1]','nu']]
            if a+b > 1+1e-6 or omega <= 0: raise RuntimeError('Invalid volatility parameters')
            h = omega+a*float(fit.resid.iloc[-1])**2+b*float(fit.conditional_volatility.iloc[-1])**2
            fits.append(dict(forecast_date=str(r.index[i].date()),estimation_end=str(past.index[-1].date()),mu=mu,omega=omega,alpha=a,beta=b,nu=nu,persistence=a+b))
        else:
            h = omega+a*(float(r.iloc[i-1])-mu)**2+b*h
        sigma=np.sqrt(h)
        for c in [.95,.99]:
            hv,he=empirical_risk(-past.iloc[-250:].to_numpy(),c)
            gv,ge=student_risk(mu,sigma,nu,c)
            nv=-past.mean()+past.std(ddof=1)*norm.ppf(c)
            ne=-past.mean()+past.std(ddof=1)*norm.pdf(norm.ppf(c))/(1-c)
            for name,v,e in [('Historical 250d',hv,he),('Normal 1000d',nv,ne),('GARCH-t 1000d',gv,ge)]:
                rows.append(dict(date=r.index[i],history_end=r.index[i-1],model=name,confidence=c,loss=-float(r.iloc[i]),var=float(v),es=float(e)))
    return pd.DataFrame(rows),pd.DataFrame(fits)


def simulate_garch(mu,omega,a,b,nu,h,horizon=10,paths=100000,seed=79):
    if horizon < 1 or paths < 100 or omega <= 0 or h <= 0 or a < 0 or b < 0 or a+b > 1+1e-6 or nu <= 2:
        raise ValueError('Invalid simulation inputs')
    rng=np.random.default_rng(seed); variance=np.full(paths,h); total=np.zeros(paths)
    for _ in range(horizon):
        eps=np.sqrt(variance)*rng.standard_t(nu,paths)*np.sqrt((nu-2)/nu)
        total += mu+eps
        variance=omega+a*eps**2+b*variance
    return -total


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=ROOT/'data/sp500.csv')
    ap.add_argument('--output',type=Path,default=ROOT/'reports')
    args=ap.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    p=load_prices(args.data); r=(100*np.log(p/p.shift(1))).dropna()
    bt,fits=backtest(r); bt.to_csv(args.output/'daily_backtest.csv',index=False,float_format='%.10g')
    fits.to_csv(args.output/'garch_refits.csv',index=False,float_format='%.10g')
    results=[]
    for (model,c),g in bt.groupby(['model','confidence']):
        stats=coverage(g.loss,g['var'],c)
        hit=g.loss>g['var']
        stats.update(model=model,confidence=float(c),mean_var=float(g['var'].mean()),mean_es=float(g.es.mean()),
                     mean_tail_residual=float((g.loc[hit,'loss']-g.loc[hit,'es']).mean()))
        results.append(stats)
    f=arch_model(r.iloc[-1000:],mean='Constant',p=1,q=1,dist='t',rescale=False).fit(disp='off')
    if f.convergence_flag: raise RuntimeError('Final GARCH fit failed')
    mu,omega,a,b,nu=[float(f.params[k]) for k in ['mu','omega','alpha[1]','beta[1]','nu']]
    h=float(f.forecast(horizon=1,reindex=False).variance.iloc[-1,0])
    losses=simulate_garch(mu,omega,a,b,nu,h)
    mc={str(c):dict(zip(['var','es'],empirical_risk(losses,c))) for c in [.95,.99]}
    std=f.std_resid.dropna(); diag={name:float(acorr_ljungbox(x,lags=[10],return_df=True).lb_pvalue.iloc[0]) for name,x in [('residual_lb_p',std),('squared_residual_lb_p',std**2)]}
    summary=dict(data_sha256=hashlib.sha256(args.data.read_bytes()).hexdigest(),prices=len(p),returns=len(r),
        data_start=str(p.index[0].date()),data_end=str(p.index[-1].date()),test_start=str(bt.date.min().date()),test_end=str(bt.date.max().date()),
        units='percent log-return loss; positive is loss',backtests=results,monte_carlo_10day=mc,monte_carlo_paths=100000,seed=79,
        final_parameters=dict(mu=mu,omega=omega,alpha=a,beta=b,nu=nu),final_fit_diagnostics=diag)
    (args.output/'results.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    fig,ax=plt.subplots(figsize=(11,4.6)); g=bt[(bt.model=='GARCH-t 1000d')&(bt.confidence==.99)]
    ax.plot(g.date,g.loss,color='#a8b1bb',lw=.5,label='Realised loss')
    ax.plot(g.date,g['var'],color='#142c45',lw=.8,label='99% one-day VaR')
    hits=g[g.loss>g['var']];ax.scatter(hits.date,hits.loss,s=10,color='#b47733',label='Exceptions',zorder=3)
    ax.set(ylabel='Loss (% log return)',title='S&P 500 • risk forecasts and realised losses');ax.legend(frameon=False,ncol=3)
    ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(args.output/'risk-backtest.png',dpi=180);plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
