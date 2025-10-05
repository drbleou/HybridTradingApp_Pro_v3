import pandas as pd
import numpy as np
from .risk import position_size, stop_loss_take_profit

def run_backtest(df: pd.DataFrame, capital=10000.0, risk_per_trade=0.01):
    df = df.copy()
    df["equity"] = capital
    df["trade"] = 0
    position = 0
    entry_price = 0.0
    for i in range(1, len(df)):
        price = df["close"].iloc[i]
        atr = df["atr"].iloc[i]
        sig = df["signal"].iloc[i]
        exit_long = df["exit_long"].iloc[i] if "exit_long" in df else False
        exit_short = df["exit_short"].iloc[i] if "exit_short" in df else False

        if position == 0:
            if sig == 1:
                sl, tp1, tp2 = stop_loss_take_profit(price, atr, 1)
                df.at[df.index[i], "trade"] = 1
                position = 1
                entry_price = price
            elif sig == -1:
                sl, tp1, tp2 = stop_loss_take_profit(price, atr, -1)
                df.at[df.index[i], "trade"] = -1
                position = -1
                entry_price = price
        else:
            if position == 1 and (exit_long or price <= entry_price*0.98 or price >= entry_price*1.6):
                pnl = (price - entry_price) / entry_price
                df.at[df.index[i], "equity"] = df["equity"].iloc[i-1] * (1 + pnl * 0.5)
                position = 0
            elif position == -1 and (exit_short or price >= entry_price*1.02 or price <= entry_price*0.4):
                pnl = (entry_price - price) / entry_price
                df.at[df.index[i], "equity"] = df["equity"].iloc[i-1] * (1 + pnl * 0.5)
                position = 0
            else:
                df.at[df.index[i], "equity"] = df["equity"].iloc[i-1]

        if df["equity"].iloc[i] == 0:
            df.at[df.index[i], "equity"] = df["equity"].iloc[i-1]

    equity = df["equity"].fillna(method="ffill")
    returns = equity.pct_change().fillna(0)
    sharpe = (returns.mean() / (returns.std() + 1e-9)) * (365 ** 0.5)
    downside = returns[returns < 0].std()
    sortino = (returns.mean() / (downside + 1e-9)) * (365 ** 0.5)
    max_dd = ((equity / equity.cummax()) - 1).min()

    summary = {
        "final_equity": float(equity.iloc[-1]),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_drawdown": float(max_dd),
        "trades": int((df["trade"] != 0).sum())
    }
    return df, summary
