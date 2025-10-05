from typing import Dict, List
import pandas as pd
from .risk import correlation_sizing

def route_orders(signals_by_symbol: Dict[str, pd.Series], prices: Dict[str, float], returns_df: pd.DataFrame, risk_budget_usd: float):
    """
    Convert final signals {-1,0,1} to target notional sizes using correlation-aware weights.
    """
    weights = correlation_sizing(returns_df) if not returns_df.empty else None
    actions = []
    for sym, sig in signals_by_symbol.items():
        side = "buy" if int(sig.iloc[-1]) == 1 else ("sell" if int(sig.iloc[-1]) == -1 else "flat")
        if side == "flat":
            continue
        w = float(weights.get(sym, 1.0)) if weights is not None else 1.0/len(signals_by_symbol)
        notional = risk_budget_usd * w
        price = float(prices.get(sym, 0))
        qty = (notional / price) if price > 0 else 0
        actions.append({"symbol": sym, "side": side, "qty": qty, "notional": notional, "price": price})
    return actions
