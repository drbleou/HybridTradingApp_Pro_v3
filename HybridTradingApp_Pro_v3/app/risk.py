import pandas as pd
import numpy as np

def position_size(capital: float, risk_per_trade: float, stop_distance: float) -> float:
    if stop_distance <= 0:
        return 0.0
    return (capital * risk_per_trade) / stop_distance

def stop_loss_take_profit(entry: float, atr: float, direction: int):
    sl_distance = max(entry * 0.02, 4 * atr)
    if direction == 1:
        sl = entry - sl_distance
        tp1 = entry * 1.2
        tp2 = entry * 1.6
    else:
        sl = entry + sl_distance
        tp1 = entry * 0.8
        tp2 = entry * 0.4
    return sl, tp1, tp2

def correlation_sizing(returns: pd.DataFrame, base_risk: float = 1.0):
    corr = returns.corr().fillna(0)
    vol = returns.std().replace(0, np.nan)
    inv_vol = 1 / vol
    w = inv_vol / inv_vol.sum()
    avg_corr = corr.mean().clip(lower=0)
    damp = 1 - avg_corr
    w = (w * damp).fillna(0)
    w = w / w.sum() if w.sum() > 0 else w
    return w
