"""Authoritative daily candles for higher-timeframe indicators; no price imputation."""
import concurrent.futures as cf
import hashlib
import io
import json
import zipfile
import numpy as np
import pandas as pd
import research as m

def daily_indicators(prices):
    f=prices.copy()
    previous=f.close.shift()
    tr=pd.concat([f.high-f.low,(f.high-previous).abs(),(f.low-previous).abs()],axis=1).max(axis=1)
    tr[previous.isna()|f.close.isna()]=np.nan
    f["atr"]=tr.rolling(14).mean()
    f["ma21"]=f.close.rolling(21).mean()
    f["ma200"]=f.close.rolling(200).mean()
    f["rising"]=f.ma200.gt(f.ma200.shift(20))
    f["structure"]=f.low.rolling(10).min()-.25*f.atr
    f["end"]=f.index.asi8+pd.Timedelta(days=1).value
    return f

def load_daily():
    cache=m.CACHE/"daily";cache.mkdir(parents=True,exist_ok=True)
    def month(label):
        name=f"BTCUSDT-1d-{label}"
        url=f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/{name}.zip"
        path=cache/(name+".zip");cp=cache/(name+".zip.CHECKSUM")
        if not cp.exists():cp.write_bytes(m.fetch_bytes(url+".CHECKSUM"))
        expected=cp.read_text().split()[0]
        if not path.exists():path.write_bytes(m.fetch_bytes(url))
        payload=path.read_bytes()
        if hashlib.sha256(payload).hexdigest()!=expected:raise ValueError("Daily checksum failure")
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            with z.open(name+".csv") as file: f=pd.read_csv(file,header=None,usecols=[0,1,2,3,4])
        f.columns=["time","open","high","low","close"]
        unit="us" if f.time.iloc[0]>100_000_000_000_000 else "ms"
        f.index=pd.to_datetime(f.pop("time"),utc=True,unit=unit)
        return f,{"url":url,"sha256":expected,"rows":len(f),"timestamp_unit":unit}
    months=pd.date_range(m.START,m.END,freq="MS",inclusive="left").strftime("%Y-%m")
    with cf.ThreadPoolExecutor(max_workers=12) as pool: parts=list(pool.map(month,months))
    f=pd.concat([p[0] for p in parts]).sort_index()
    expected=pd.date_range(m.START,m.END,freq="1d",inclusive="left",tz="UTC")
    if f.index.has_duplicates or not f.index.equals(expected):raise ValueError("Daily coverage not complete")
    if not ((f.high>=f[["open","low","close"]].max(axis=1))&
            (f.low<=f[["open","high","close"]].min(axis=1))&(f.low>0)).all():
        raise ValueError("Malformed daily candles")
    return f,{"archives":[p[1] for p in parts],"rows":len(f),"missing_daily_candles":0,
              "frame_sha256":hashlib.sha256(pd.util.hash_pandas_object(f,index=True).values.tobytes()).hexdigest()}

def reconcile(base,daily):
    grouped=base.resample("1d")
    complete=grouped.close.count().eq(288)
    aggregate=grouped.agg({"open":"first","high":"max","low":"min","close":"last"})
    aligned=daily.reindex(aggregate.index)
    error=(aggregate-aligned).abs()
    comparable=complete&aligned.notna().all(axis=1)
    mismatch=(error.loc[comparable]>.011).any(axis=1)
    record={"complete_intraday_days_compared":int(comparable.sum()),
            "days_with_intraday_gaps":int((~complete).sum()),
            "mismatched_complete_days":int(mismatch.sum()),
            "max_absolute_price_difference":float(error.loc[comparable].max().max()),
            "mismatch_dates":mismatch.index[mismatch].astype(str).tolist(),
            "tolerance_usdt":.011}
    if mismatch.any():raise ValueError("Authoritative daily/intraday mismatch: "+json.dumps(record))
    return record

