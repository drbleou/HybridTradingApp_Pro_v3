import pandas as pd
import numpy as np
import ta

def wavetrend(df, chlen=10, avg=21, smoothed=4):
    hlc3 = (df["high"] + df["low"] + df["close"]) / 3.0
    esa = hlc3.ewm(span=chlen, adjust=False).mean()
    d = (hlc3 - esa).abs().ewm(span=chlen, adjust=False).mean()
    ci = (hlc3 - esa) / (0.015 * d.replace(0, np.nan))
    tci = ci.ewm(span=avg, adjust=False).mean()
    wt1 = tci
    wt2 = wt1.ewm(span=smoothed, adjust=False).mean()
    return wt1, wt2

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50, fillna=True)
    df["ema100"] = ta.trend.ema_indicator(df["close"], window=100, fillna=True)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200, fillna=True)

    rsi = ta.momentum.RSIIndicator(df["close"], window=14, fillna=True)
    df["rsi"] = rsi.rsi()

    macd = ta.trend.MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9, fillna=True)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"] = macd.macd_diff()

    bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2, fillna=True)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"].replace(0, np.nan)

    obv = ta.volume.OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"], fillna=True)
    df["obv"] = obv.on_balance_volume()
    df["obv_slope"] = df["obv"].diff().rolling(5).mean()

    atr = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14, fillna=True)
    df["atr"] = atr.average_true_range()

    adx = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14, fillna=True)
    df["adx"] = adx.adx()

    wt1, wt2 = wavetrend(df)
    df["wt1"] = wt1
    df["wt2"] = wt2

    return df

def find_divergences(series_price: pd.Series, series_osc: pd.Series, lookback=30):
    bull_div = pd.Series(False, index=series_price.index)
    bear_div = pd.Series(False, index=series_price.index)
    for i in range(lookback, len(series_price)):
        p_now = series_price.iloc[i]
        o_now = series_osc.iloc[i]
        p_low = series_price.iloc[i-lookback:i].min()
        p_high = series_price.iloc[i-lookback:i].max()
        o_low = series_osc.iloc[i-lookback:i].min()
        o_high = series_osc.iloc[i-lookback:i].max()
        if p_now <= p_low and o_now >= o_low:
            bull_div.iloc[i] = True
        if p_now >= p_high and o_now <= o_high:
            bear_div.iloc[i] = True
    return bull_div, bear_div
