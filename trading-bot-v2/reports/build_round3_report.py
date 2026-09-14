"""Create the round-3 research report and figure from executed result files."""
from pathlib import Path
import json, hashlib, shutil, sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'reports/generated/btc-round-3'
REPORTS=ROOT/'reports'

def run():
    rows=json.loads((OUT/'screen.json').read_text())
    combined=json.loads((OUT/'combined.json').read_text())
    folds=json.loads((OUT/'folds.json').read_text())
    normal=sorted([r for r in rows if r['cost_multiplier']==1 and r['config'].startswith('H-')],key=lambda r:-r['total_return_pct'])
    best=normal[0];name=best['config']
    by={(r['config'],r['cost_multiplier']):r for r in rows}
    settings=json.loads((OUT/'settings.json').read_text())
    snapshot={'screen':rows,'rolling':combined,'folds':folds,'settings':settings,
              'data_reconciliation':json.loads((OUT/'data-reconciliation.json').read_text())}
    (REPORTS/'btc-round-3-results.json').write_text(json.dumps(snapshot,indent=2))
    flat=[{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in rows]
    pd.DataFrame(flat).to_csv(REPORTS/'btc-round-3-comparison.csv',index=False)
    preliminary=OUT.with_name('btc-round-3-preliminary')
    if preliminary.exists():
        audit={'status':'Superseded: missing intraday bars repeatedly reset aggregated daily SMA200.',
               'source_commit':'c921695cf2cf876f1d62241f4f863c1455be0b55',
               'screen':json.loads((preliminary/'screen.json').read_text()),
               'rolling':json.loads((preliminary/'combined.json').read_text())}
        (REPORTS/'btc-round-3-preliminary-audit.json').write_text(json.dumps(audit,indent=2))
    equity=json.loads((OUT/'daily-equity.json').read_text())
    rolling=json.loads((OUT/'rolling-equity.json').read_text())
    from market_data import load_daily
    daily,_=load_daily()
    regimes=pd.read_csv(OUT/'daily-regimes.csv',index_col=0)
    regimes.index=pd.to_datetime(regimes.index,utc=True)+pd.Timedelta(days=1)
    start=pd.Timestamp('2020-01-01',tz='UTC');end=pd.Timestamp('2026-09-01',tz='UTC')
    regimes=regimes.loc[(regimes.index>=start)&(regimes.index<end)]
    colors={'uptrend':'#c5e8cf','sideways':'#cbd9f3','downtrend':'#f2c7c9','transition':'#e8e8e8','unknown':'#ffffff'}
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
    fig,axes=plt.subplots(3,1,figsize=(12,10),sharex=True,gridspec_kw={'height_ratios':[1.1,1,1]},layout='constrained')
    fig.suptitle('BTCUSDT | regime-aware strategy evaluation',fontsize=18,fontweight='bold')
    dd=daily.loc[(daily.index>=start)&(daily.index<end)]
    axes[0].plot(dd.index,dd.close,color='#1b304b',linewidth=.8)
    for date,row in regimes.iterrows():axes[0].axvspan(date,date+pd.Timedelta(days=1),color=colors[row.regime],lw=0)
    axes[0].set_yscale('log');axes[0].set_ylabel('BTC / USDT (log)')
    axes[0].set_title('Regime known at each day’s opening; official daily candles',loc='left',fontsize=11)
    axes[0].legend(handles=[Patch(facecolor=colors[k],label=k.capitalize()) for k in ('uptrend','sideways','downtrend','transition')],ncol=4,loc='upper left',fontsize=9)
    for cost,color in ((1,'#2563a6'),(2,'#d46723')):
        s=pd.Series(equity[name+f'/cost{cost}']);s.index=pd.to_datetime(s.index,utc=True)
        axes[1].plot(s.index,s,label='Normal costs' if cost==1 else 'Double costs',color=color,linewidth=1.3)
        s=pd.Series(rolling[str(cost)]);s.index=pd.to_datetime(s.index,utc=True)
        axes[2].plot(s.index,s,label='Normal costs' if cost==1 else 'Double costs',color=color,linewidth=1.3)
    axes[1].set_title(f'Highest-return full-period screen: {name} — selected with hindsight',loc='left',fontsize=11)
    axes[2].set_title('Rolling 24-month selection / 6-month execution; cash if no eligible configuration',loc='left',fontsize=11)
    for ax in axes[1:]:
        ax.axhline(10000,color='#777777',ls='--',lw=.7);ax.set_ylabel('Account / USDT');ax.legend(loc='best');ax.grid(alpha=.15)
    axes[2].set_xlabel('2020–August 2026 • retrospective research • initial account 10,000 USDT')
    fig.savefig(REPORTS/'btc-round-3-regimes.png',dpi=145)
    plt.close(fig)
    def pct(v):return f'{v:+.2f}%'
    def f(v):return '—' if v is None else f'{v:.2f}'
    def table(rr):
        lines=['| Configuration | Trades | Hit rate | Payoff | Profit factor | Net return | Double-cost return |','|---|---:|---:|---:|---:|---:|---:|']
        for r in rr:
            double=by[(r['config'],2)]
            lines.append(f"| {r['config']} | {r['trades']} | {r['win_rate_pct']:.1f}% | {f(r['payoff'])} | {f(r['profit_factor'])} | {pct(r['total_return_pct'])} | {pct(double['total_return_pct'])} |")
        return '\n'.join(lines)
    c=combined[0];c2=combined[1]
    text=f'''# BTCUSDT round 3: Fibonacci, regimes, divergence and adaptive exits

Evaluation: 1 January 2020–31 August 2026, with history from January 2018. BTCUSDT spot, long only. All periods are research-exposed.

## Decision
The requested 60% hit rate with strong average-win/average-loss profitability is **not established**. The highest-return new configuration in the full-period screen is **{name}**, returning {pct(best['total_return_pct'])} at normal costs and {pct(by[(name,2)]['total_return_pct'])} at doubled costs. Its hit rate is {best['win_rate_pct']:.1f}% across {best['trades']} positions, with payoff {best['payoff']:.2f} and profit factor {best['profit_factor']:.2f}. This is a hindsight-selected screen, not an independently validated winner.

The predeclared rolling selection returns **{pct(c['total_return_pct'])}**, falling to **{pct(c2['total_return_pct'])}** with doubled costs; {c['trades']} positions, {c['win_rate_pct']:.1f}% hit rate, profit factor {f(c['profit_factor'])}. Do not deploy this strategy on this evidence.

## What changed
Daily SMA200, its 20-day slope and ADX classify trend/range/transition conditions. Uptrend entries use confirmed 38.2%–61.8% Fibonacci retracements with rising RSI14; a second variant additionally requires confirmed hidden bullish divergence. Sideways entries use lower-Bollinger-band rejection with rising RSI. Downtrend and transition conditions allow no new position; existing positions exit at the next eligible event.

Two entry timeframes (1h and 4h), two confirmations, and three exit policies produce twelve configurations. Fixed targets are 1.5R or 2R. Adaptive exits use a 3R cap, cost-adjusted breakeven after 1R, then a completed-bar 2-ATR trailing stop after 2R. Every version has an initial protective stop and maximum holding time. See [the recorded specification](../BTC-ROUND-3-SPEC.md) for exact rules.

## All new configurations
Returns are total account returns over the entire period, not annual returns. Payoff is average net winning position divided by average absolute net losing position; profit factor is gross net-position profits divided by absolute net-position losses. Cost scenarios are separate replays, including their entry-cost filter, so trade counts can differ.

{table(normal)}

## Frozen breakout comparison
The legacy run keeps the original aggregated daily data; the corrected run uses authoritative daily candles with identical breakout rules. Any change between these baselines is a data-coverage effect.

{table([r for r in rows if r['cost_multiplier']==1 and r['config'].startswith('BASELINE')])}

## Market regimes
For the highest-return new full-period configuration, positions grouped by the regime at entry:

| Entry regime | Positions | Hit rate | Payoff | Profit factor | Net position P&L / USDT |
|---|---:|---:|---:|---:|---:|
'''
    for reg,rr in best['entry_regime_metrics'].items():text+=f"| {reg} | {rr['trades']} | {f(rr['win_rate_pct'])}{'%' if rr['trades'] else ''} | {f(rr['payoff'])} | {f(rr['profit_factor'])} | {rr['net_pnl']:+.2f} |\n"
    text+='''
Daily account returns grouped by the regime known at the day's opening. These are non-contiguous return slices, not separately investable portfolios; multiplying their growth factors reconstructs the account total. They are not the same grouping as entry-regime P&L. BTC comparison uses exact observed daily open/close endpoints and no fees.

| Daily regime | Days | Screen account | Rolling account | BTC same-day slice |
|---|---:|---:|---:|---:|
'''
    for reg,rr in best['daily_regime_metrics'].items():text+=f"| {reg} | {rr['days']} | {pct(rr['account_compounded_return_pct'])} | {pct(c['daily_regime_metrics'][reg]['account_compounded_return_pct'])} | {pct(rr['btc_intraday_compounded_return_pct'])} |\n"
    text+='''
Downtrend performance measures the cash/exit policy, not a profitable short-selling strategy. Small nonzero returns can arise while exiting a position entered under the preceding regime. Sideways is an ADX-based causal label and can include days with substantial cumulative BTC gains; it is not a hindsight claim that prices stayed within one range.

![BTC price, regime coverage and account equity](btc-round-3-regimes.png)

## Rolling selection and uncertainty
Each fold uses the previous 24 months to choose one configuration with at least 20 positions, positive mean net R, positive return and no gap-affected positions. It holds that configuration for six months; no eligible candidate means cash. Doubled-cost replay uses the same choices. Forced liquidation at fold boundaries is included.

| Fold start | Selected configuration | Normal net return | Double-cost net return |
|---|---|---:|---:|
'''
    for row in folds:
        if row['cost_multiplier']!=1:continue
        double=next(x for x in folds if x['start']==row['start'] and x['cost_multiplier']==2)
        text+=f"| {row['start'][:10]} | {row['chosen'] or 'Cash'} | {pct(row['total_return_pct'])} | {pct(double['total_return_pct'])} |\n"
    text+=f'''
The screen winner's Wilson 95% hit-rate interval is {best['win_rate_wilson_95_pct'][0]:.1f}%–{best['win_rate_wilson_95_pct'][1]:.1f}%. Its three-month circular-block bootstrap interval for mean net R is {best['mean_net_r_block_95'][0]:+.3f} to {best['mean_net_r_block_95'][1]:+.3f}; this does not correct for choosing a winner among many tests.

Screen maximum drawdown: {best['max_drawdown_pct']:.2f}%; worst month: {best['worst_month_pct']:.2f}%; worst year: {best['worst_year_pct']:.2f}%; average exposure: {best['average_exposure_pct']:.2f}%. Rolling daily-close maximum drawdown: {c['daily_max_drawdown_pct']:.2f}%; worst month: {c['worst_month_pct']:.2f}%; worst year: {c['worst_year_pct']:.2f}%. Five-minute gaps affected {best['gap_affected_positions']} screen-winner positions and {c['gap_affected_positions']} rolling positions. Affected executions remain provisional.

## Data correction and reproducibility
The preliminary run classified 1,078 of 2,435 evaluation days as unknown because missing intraday bars invalidated aggregated daily candles and repeatedly reset SMA200. The amended run uses separately checksum-verified Binance daily archives for daily indicators, while retaining all 1,847 missing/blocked five-minute bars, including exclusion of 241 off-grid timestamps. The daily archive contains 3,165 complete candles. All 3,134 complete intraday days exactly match native daily OHLC; 31 days contain intraday gaps. No execution prices were filled. Daily regime coverage now has zero unknown evaluation days.

Rules were frozen in commit `c921695cf2cf876f1d62241f4f863c1455be0b55`; the data-method amendment and 38 passing tests were committed as `ade55f92b8d4adb35a06187603390ad5e2f62810` before the corrected run. The amendment changed data coverage, not trading thresholds. [Preliminary audit](btc-round-3-preliminary-audit.json) preserves superseded comparisons.

Start capital 10,000 USDT; 0.5% planned trade risk, 25% initial allocation cap, no leverage. Normal costs assume 0.10% fee and 0.02% slippage each side. Entries use next opens; stop/target ambiguity within five-minute candles resolves stop first. Fixed quantity/minimum-notional assumptions, gaps, approximate fills, sparse samples and multiple testing limit conclusions. Native daily data are from [Binance public archives](https://github.com/binance/binance-public-data).

[Machine-readable snapshot](btc-round-3-results.json) · [Comparison CSV](btc-round-3-comparison.csv) · [Pinned Colab notebook](../notebooks/BTCUSDT-Round-3.ipynb) · [Independent workflow run](https://github.com/sat79/finance-portfolio/actions/runs/34910758348)

Full ledgers, daily equity, training candidates, checksum manifests and settings are in the run artifact and the [permanent result archive](btc-round-3-full-results.zip). No live orders or exchange credentials are involved. Next research should test distinct hypotheses with a fresh forward period; repeated tuning of this history cannot establish the requested future hit rate.
'''
    (REPORTS/'BTC-ROUND-3-RESULTS.md').write_text(text)
    print('REPORT_READY',name,'normal',best['total_return_pct'],'rolling',c['total_return_pct'])

if __name__=='__main__':run()
