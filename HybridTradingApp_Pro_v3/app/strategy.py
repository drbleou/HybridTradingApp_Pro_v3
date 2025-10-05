import pandas as pd
import numpy as np
from .indicators import find_divergences

def session_filter(ts: pd.Series, start_h=9, end_h=15):
    hours = ts.dt.hour
    return (hours >= start_h) & (hours < end_h)

def hybrid_pro(df: pd.DataFrame, use_ema200=True, use_adx=True, adx_min=15,
               use_wavetrend=True, wt_bound=0, use_divergence=True,
               session_start=9, session_end=15):
    df = df.copy()
    cond_ema_long = df["ema50"] > df["ema100"]
    cond_ema_short = df["ema50"] < df["ema100"]
    if use_ema200:
        cond_ema_long &= df["close"] > df["ema200"]
        cond_ema_short &= df["close"] < df["ema200"]
    cond_rsi_long = (df["rsi"].shift(1) < 30) & (df["rsi"] >= 30)
    cond_rsi_short = (df["rsi"].shift(1) > 70) & (df["rsi"] <= 70)
    cond_macd_long = (df["macd"].shift(1) <= df["macd_signal"].shift(1)) & (df["macd"] > df["macd_signal"])
    cond_macd_short = (df["macd"].shift(1) >= df["macd_signal"].shift(1)) & (df["macd"] < df["macd_signal"])
    cond_boll_long = (df["close"] <= df["bb_lower"]) & (df["bb_width"] > df["bb_width"].rolling(20).median())
    cond_boll_short = (df["close"] >= df["bb_upper"])
    cond_vol_long = df["obv_slope"] > 0
    cond_vol_short = df["obv_slope"] < 0
    if use_adx:
        cond_adx = df["adx"] >= adx_min
        cond_ema_long &= cond_adx
        cond_ema_short &= cond_adx
    if use_wavetrend:
        cond_wt_long = df["wt1"] < -abs(wt_bound)
        cond_wt_short = df["wt1"] > abs(wt_bound)
    else:
        cond_wt_long = cond_wt_short = True
    if use_divergence:
        bull_rsi, bear_rsi = find_divergences(df["close"], df["rsi"], lookback=30)
        bull_macd, bear_macd = find_divergences(df["close"], df["macd"], lookback=30)
        cond_div_long = bull_rsi | bull_macd
        cond_div_short = bear_rsi | bear_macd
    else:
        cond_div_long = cond_div_short = True
    long_entry = cond_ema_long & cond_rsi_long & cond_macd_long & cond_boll_long & cond_vol_long & cond_wt_long & cond_div_long
    short_entry = cond_ema_short & cond_rsi_short & cond_macd_short & cond_boll_short & cond_vol_short & cond_wt_short & cond_div_short
    if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        sess = session_filter(df["timestamp"], session_start, session_end)
        long_entry &= sess
        short_entry &= sess
    sig = pd.Series(0, index=df.index)
    sig[long_entry] = 1
    sig[short_entry] = -1
    return sig

def momentum_breakout(df: pd.DataFrame, ema_fast=20, ema_slow=50, adx_min=20, bb_dev=2.0):
    d = df.copy()
    ema_f = d["close"].ewm(span=ema_fast, adjust=False).mean()
    ema_s = d["close"].ewm(span=ema_slow, adjust=False).mean()
    trend_up = ema_f > ema_s
    trend_dn = ema_f < ema_s
    # Breakout: close > upper band or strong MACD momentum
    bb_width = d["bb_width"]
    breakout_up = (d["close"] > d["bb_upper"]) & (d["macd_hist"] > 0) & (bb_width > bb_width.rolling(50).median())
    breakout_dn = (d["close"] < d["bb_lower"]) & (d["macd_hist"] < 0) & (bb_width > bb_width.rolling(50).median())
    strong = d["adx"] >= adx_min
    sig = pd.Series(0, index=d.index)
    sig[trend_up & breakout_up & strong] = 1
    sig[trend_dn & breakout_dn & strong] = -1
    return sig

def mean_revert(df: pd.DataFrame, rsi_low=28, rsi_high=72, wt_band=25):
    d = df.copy()
    # buy near lower band with oversold + negative WT, sell near upper band with overbought + positive WT
    long_cond = (d["close"] <= d["bb_lower"]) & (d["rsi"] < rsi_low) & (d["wt1"] < -abs(wt_band))
    short_cond = (d["close"] >= d["bb_upper"]) & (d["rsi"] > rsi_high) & (d["wt1"] > abs(wt_band))
    sig = pd.Series(0, index=d.index)
    sig[long_cond] = 1
    sig[short_cond] = -1
    return sig

def combine_signals(signals: dict, weights: dict=None):
    idx = next(iter(signals.values())).index
    total = pd.Series(0.0, index=idx)
    if weights is None:
        weights = {k:1.0 for k in signals}
    for k, s in signals.items():
        total += s.fillna(0) * float(weights.get(k, 1.0))
    out = pd.Series(0, index=idx)
    out[total > 0] = 1
    out[total < 0] = -1
    return out
