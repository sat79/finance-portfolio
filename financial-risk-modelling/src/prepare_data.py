"""Extract the documented dataset already shipped in the installed arch package.
No network request is made. Does not overwrite an existing file unless --force.
"""
from pathlib import Path
import argparse,json,hashlib
import arch.data.sp500
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--force',action='store_true');args=ap.parse_args()
    path=ROOT/'data/sp500.csv';expected=json.loads((ROOT/'data/manifest.json').read_text())[0]['sha256']
    if path.exists() and not args.force:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise SystemExit('Existing CSV differs; preserve it or explicitly use --force.')
        print('Existing CSV matches the documented dataset.');return
    df=arch.data.sp500.load()[['Adj Close']].rename(columns={'Adj Close':'adjusted_close'})
    text=df.to_csv(index_label='date',float_format='%.10g',lineterminator='\n')
    if hashlib.sha256(text.encode()).hexdigest()!=expected:raise SystemExit('Installed package data differ from the reviewed snapshot; no file written.')
    path.write_bytes(text.encode());print('Prepared historical dataset; SHA-256 matches the reviewed input.')
if __name__=='__main__':main()
