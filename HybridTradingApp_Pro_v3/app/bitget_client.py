import os
import ccxt

def get_bitget():
    key = os.environ.get("BITGET_API_KEY")
    secret = os.environ.get("BITGET_API_SECRET")
    pw = os.environ.get("BITGET_API_PASSPHRASE")
    params = {"options": {"defaultType": "swap"}}
    if key and secret and pw:
        return ccxt.bitget({
            "apiKey": key,
            "secret": secret,
            "password": pw,
            **params
        })
    return ccxt.bitget(params)

def fetch_ohlcv(symbol="BTC/USDT:USDT", timeframe="1h", limit=1000):
    ex = get_bitget()
    ex.load_markets()
    return ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

def fetch_positions():
    ex = get_bitget()
    try:
        return ex.fetch_positions()
    except Exception:
        return []

def fetch_balance():
    ex = get_bitget()
    try:
        bal = ex.fetch_balance(params={"type": "swap"})
        total = bal.get("total", {}).get("USDT", 0.0)
        free = bal.get("free", {}).get("USDT", 0.0)
        return {"total": float(total), "free": float(free)}
    except Exception:
        return {"total": 0.0, "free": 0.0}

def place_order(symbol, side, amount, price=None, type_="market", leverage=5, params=None):
    ex = get_bitget()
    ex.load_markets()
    ex.set_leverage(leverage, symbol=symbol)
    params = params or {}
    if type_ == "market":
        return ex.create_order(symbol, "market", side, amount, price=None, params=params)
    else:
        return ex.create_order(symbol, "limit", side, amount, price, params=params)
