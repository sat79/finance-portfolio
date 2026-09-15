"""Checksum-verified BTCUSDT perpetual futures data; preserve gaps and event timestamps."""
import concurrent.futures as cf
import hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import research as shared

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'data/futures-cache'
START='2020-01-01'; END='2026-09-01'

def month(kind,label):
    interval='1d' if kind=='daily' else '5m'
    directory='fundingRate' if kind=='funding' else ('markPriceKlines' if kind=='mark' else 'klines')
    name=f'BTCUSDT-fundingRate-{label}' if kind=='funding' else f'BTCUSDT-{interval}-{label}'
    middle='BTCUSDT/' if kind=='funding' else f'BTCUSDT/{interval}/'
    url=f'https://data.binance.vision/data/futures/um/monthly/{directory}/{middle}{name}.zip'
    folder=CACHE/kind;folder.mkdir(parents=True,exist_ok=True)
    path=folder/(name+'.zip');cp=folder/(name+'.zip.CHECKSUM')
    for attempt in range(3):
        try:
            if not cp.exists():cp.write_bytes(shared.fetch_bytes(url+'.CHECKSUM'))
            if not path.exists():path.write_bytes(shared.fetch_bytes(url))
            break
        except Exception:
            if attempt==2:raise
    data=path.read_bytes();expected=cp.read_text().split()[0]
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Checksum mismatch: '+url)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        raw=z.read(name+'.csv')
    header=not raw.split(b',',1)[0].strip().isdigit()
    f=pd.read_csv(io.BytesIO(raw),header=0 if header else None)
    if kind=='funding':
        f=f.iloc[:,:3];f.columns=['time','interval_hours','rate']
    else:
        f=f.iloc[:,:5];f.columns=['time','open','high','low','close']
    unit='us' if f.time.iloc[0]>100_000_000_000_000 else 'ms'
    f.index=pd.to_datetime(f.pop('time'),unit=unit,utc=True)
    return kind,f,{'kind':kind,'url':url,'sha256':expected,'rows':len(f),'unit':unit,'header':header}

def load():
    months=pd.date_range(START,END,freq='MS',inclusive='left').strftime('%Y-%m')
    tasks=[(kind,label) for kind in ('trade','mark','daily','funding') for label in months]
    with cf.ThreadPoolExecutor(max_workers=16) as pool:parts=list(pool.map(lambda args:month(*args),tasks))
    frames={};manifest={'archives':[x[2] for x in parts],'start':START,'end_exclusive':END,'audit':{}}
    for kind in ('trade','mark','daily','funding'):
        f=pd.concat([x[1] for x in parts if x[0]==kind]).sort_index()
        if f.index.has_duplicates:raise ValueError('Duplicate '+kind+' timestamps')
        if kind!='funding':
            if not ((f.low>0)&(f.high>=f[['open','close','low']].max(axis=1))&(f.low<=f[['open','close','high']].min(axis=1))).all():raise ValueError('Bad OHLC '+kind)
            if kind=='daily':
                grid=pd.date_range(START,END,freq='1d',inclusive='left',tz='UTC')
                if not f.index.equals(grid):raise ValueError('Daily coverage incomplete')
                audit={'rows':len(f),'missing_bars':0}
            else:f,audit=shared.validate_grid(f,START,END)
        else:
            if not np.isfinite(f.to_numpy()).all():raise ValueError('Invalid funding values')
            nominal=f.index.round('8h')
            grid=pd.date_range(START,END,freq='8h',inclusive='left',tz='UTC')
            offsets=np.abs(f.index.asi8-nominal.asi8)/1e6
            # Nominal timestamps are only a coverage check, never settlement timestamps.
            if not nominal.equals(grid) or (offsets>60000).any() or not f.interval_hours.eq(8).all():
                raise ValueError('Funding schedule incomplete or changed; investigate before execution')
            audit={'rows':len(f),'coverage_missing_events':0,'maximum_offset_ms':float(offsets.max()),'raw_timestamps_retained':True}
        frames[kind]=f;manifest['audit'][kind]=audit
        manifest[kind+'_frame_sha256']=hashlib.sha256(pd.util.hash_pandas_object(f,index=True).values.tobytes()).hexdigest()
    agg=frames['trade'].resample('1d').agg({'open':'first','high':'max','low':'min','close':'last'})
    complete=frames['trade'].close.resample('1d').count().eq(288)
    diff=(agg-frames['daily']).abs().loc[complete]
    mismatches=(diff>.011).any(axis=1)
    manifest['daily_reconciliation']={'complete_days':int(complete.sum()),'mismatches':int(mismatches.sum()),'max_error':float(diff.max().max())}
    if mismatches.any():raise ValueError('Futures daily/intraday disagreement: '+str(diff.loc[mismatches]))
    return frames,manifest

if __name__=='__main__':
    frames,manifest=load()
    for kind,f in frames.items():f.to_pickle(ROOT/f'data/futures-{kind}.pkl')
    (ROOT/'data/futures-manifest.json').write_text(json.dumps(manifest,indent=2))
    print('DATA_READY',json.dumps({k:{a:v for a,v in x.items() if not isinstance(v,list)} for k,x in manifest['audit'].items()}),flush=True)
