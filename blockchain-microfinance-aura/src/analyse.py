"""New audit extension, not recovery of the dissertation's original simulation."""
from pathlib import Path
import argparse,json,itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DIMS=['accessibility','usability','reliability','affordability']


def weighted_scores(scores,weights):
    s=np.asarray(scores,dtype=float);w=np.asarray(weights,dtype=float)
    if s.ndim!=2 or s.shape[1]!=4 or w.shape!=(4,) or not np.isfinite(s).all() or not np.isfinite(w).all() or (s<0).any() or (s>25).any() or (w<0).any() or not np.isclose(w.sum(),1):
        raise ValueError('Scores must be 0–25; four nonnegative weights must sum to one')
    return s@w*4


def bass(time,p,q,m):
    if not np.isfinite([p,q,m]).all() or p<=0 or q<0 or not 0<m<=1 or (np.asarray(time)<0).any(): raise ValueError('Invalid Bass parameters')
    e=np.exp(-(p+q)*np.asarray(time))
    return m*(1-e)/(1+(q/p)*e)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',type=Path,default=ROOT/'data');ap.add_argument('--output',type=Path,default=ROOT/'reports');args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    scores=pd.read_csv(args.data/'aura_scores.csv');s=scores[DIMS].to_numpy()
    equal=weighted_scores(s,np.ones(4)/4)
    scenarios={'equal':[.25]*4,'accessibility emphasis':[.55,.15,.15,.15],'usability emphasis':[.15,.55,.15,.15],'reliability emphasis':[.15,.15,.55,.15],'affordability emphasis':[.15,.15,.15,.55]}
    rows=[]
    for name,w in scenarios.items():
        for case,value in zip(scores['case'],weighted_scores(s,w)):rows.append(dict(scenario=name,case=case,score=value))
    pd.DataFrame(rows).to_csv(args.output/'weight_scenarios.csv',index=False)
    rng=np.random.default_rng(79);weights=rng.dirichlet(np.ones(4),10000);sim=s@weights.T*4
    top=np.argmax(sim,axis=0)
    sensitivity=[dict(case=case,equal_weight_score=float(equal[i]),reported_rounded_score=int(scores.reported_total.iloc[i]),rounding_consistent=bool(round(equal[i])==scores.reported_total.iloc[i]),share_of_sampled_weights_ranked_first=float(np.mean(top==i))) for i,case in enumerate(scores['case'])]
    pars=pd.read_csv(args.data/'bass_parameters.csv');curves=[];bounds=[]
    for _,r in pars.iterrows():
        combos=list(itertools.product([r.p_low,r.p_high],[r.q_low,r.q_high],[r.m_low,r.m_high]))
        mid=[(r.p_low+r.p_high)/2,(r.q_low+r.q_high)/2,(r.m_low+r.m_high)/2]
        v=[float(bass(10,*c)) for c in combos]
        bounds.append(dict(region=r.region,year10_low=min(v),year10_mid=float(bass(10,*mid)),year10_high=max(v)))
        for year in range(21): curves.append(dict(region=r.region,year=year,cumulative_market_share=float(bass(year,*mid))))
    pd.DataFrame(curves).to_csv(args.output/'bass_curves.csv',index=False)
    # Pure arithmetic check of the final dissertation's reported cost range.
    fees=dict(baseline=12.3,blockchain_low=4.2,blockchain_high=8.7,
        actual_reduction_low=1-8.7/12.3,actual_reduction_high=1-4.2/12.3,
        stated_reduction_low=.35,stated_reduction_high=.65)
    out=dict(status='Uncalibrated dissertation assumptions; audit illustration, not empirical validation',seed=79,preference_draws=10000,aura=sensitivity,bass_year10=bounds,
        bass_time_unit='Years assumed for this audit; original table does not specify parameter frequency',fee_arithmetic=fees)
    (args.output/'results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    fig,ax=plt.subplots(figsize=(9,4.5))
    for (region,g),color in zip(pd.DataFrame(curves).groupby('region'),['#142c45','#b47733','#769098']): ax.plot(g.year,100*g.cumulative_market_share,label=region,color=color)
    ax.set(xlabel='Years (audit assumption)',ylabel='Share of total market (%)',title='Adoption under dissertation parameter midpoints')
    ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(args.output/'adoption-audit.png',dpi=180);plt.close(fig)
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
