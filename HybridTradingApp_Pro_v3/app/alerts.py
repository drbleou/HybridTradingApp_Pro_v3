import pandas as pd
from typing import Dict, Any

def alert_drawdown(equity: pd.Series, max_dd_threshold: float = -0.15):
    if equity.empty:
        return None
    dd = (equity / equity.cummax()) - 1.0
    cur = float(dd.iloc[-1])
    if cur <= max_dd_threshold:
        return f"⚠️ Drawdown {cur:.2%} ≤ seuil {max_dd_threshold:.0%}"
    return None

def alert_liquidation(position: Dict[str, Any], proximity: float = 0.05):
    # position needs fields: side ('long'/'short'), entryPrice, liqPrice, markPrice
    if not position or "liqPrice" not in position or not position["liqPrice"]:
        return None
    liq = float(position["liqPrice"])
    mark = float(position.get("markPrice", 0))
    if liq <= 0 or mark <= 0:
        return None
    dist = abs(mark - liq) / mark
    if dist <= proximity:
        return f"🚨 Proximité liquidation: distance {dist:.2%}"
    return None

def alert_margin(balance: Dict[str, Any], min_free_ratio: float = 0.2):
    # balance: {'total': float, 'free': float}
    if not balance:
        return None
    total = float(balance.get("total", 0))
    free = float(balance.get("free", 0))
    if total <= 0:
        return None
    ratio = free / total
    if ratio < min_free_ratio:
        return f"⚠️ Marge disponible faible ({ratio:.2%}) < {min_free_ratio:.0%}"
    return None

def alert_high_fees(current_hour_utc: int, high_fee_windows=None):
    # high_fee_windows: list of (start_hour, end_hour) UTC
    if not high_fee_windows:
        return None
    for s, e in high_fee_windows:
        if s <= current_hour_utc < e:
            return f"💸 Fenêtre de frais élevés {s:02d}:00–{e:02d}:00 UTC"
    return None
