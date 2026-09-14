"""Reproduce the geographic earnings bridge from the FY2025 Form 20-F.
Uses reported group net income, not net income attributable to ADS holders.
Türkiye has no consolidated 2024 comparison in this extract: no growth is invented.
"""
from pathlib import Path
import argparse,csv,json,math
ROOT=Path(__file__).resolve().parents[1]
def analyse(path=ROOT/'data/geography.csv'):
    with path.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    keys=[(r['year'],r['geography']) for r in rows]
    expected={('2024','Kazakhstan & Other'),('2025','Kazakhstan & Other'),('2025','Turkiye')}
    if len(keys)!=3 or set(keys)!=expected:raise ValueError('Incomplete or duplicate geographic panel')
    values={}
    for r in rows:
        rev=float(r['revenue_kzt_mn']);ni=float(r['net_income_kzt_mn'])
        if not math.isfinite(rev) or not math.isfinite(ni) or rev<=0:raise ValueError('Invalid financial input')
        values[(r['year'],r['geography'])]=(rev,ni)
    controls=json.loads((ROOT/'data/group_income_controls.json').read_text())
    for year in ['2024','2025']:
        actual=sum(v[1] for (y,_),v in values.items() if y==year)
        if not math.isclose(actual,controls[year],rel_tol=0,abs_tol=.001):raise ValueError('Group-income reconciliation failed')
    previous=values[('2024','Kazakhstan & Other')];core=values[('2025','Kazakhstan & Other')];turkey=values[('2025','Turkiye')]
    return dict(units='KZT millions; reported geographic scope',core_scope='Kazakhstan & Other includes Azerbaijan and Ukraine; not Kazakhstan standalone',
        core_revenue_growth=core[0]/previous[0]-1,core_net_income_growth=core[1]/previous[1]-1,
        core_2025_net_income=core[1],turkiye_2025_net_income=turkey[1],group_2025_net_income=core[1]+turkey[1],
        turkiye_loss_as_fraction_of_core_income=-turkey[1]/core[1],group_net_income_growth=controls['2025']/controls['2024']-1,
        source='FY2025 Form 20-F, PDF p189 / printed F-35',limitations='Acquisition-scope and IAS 29 figures; no organic Turkish growth rate or incremental acquisition valuation is inferred.')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'reports/geography-results.json');args=ap.parse_args()
    result=analyse();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
