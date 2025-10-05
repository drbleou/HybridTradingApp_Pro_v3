import os, time, base64, hashlib
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import requests

def get_db() -> Engine:
    db_url = os.environ.get("DATABASE_URL", "sqlite:///trading.db")
    return create_engine(db_url, future=True)

def derive_key(password: str) -> bytes:
    h = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(h)

def get_fernet(password: str) -> Fernet:
    return Fernet(derive_key(password))

def encrypt(s: str, password: str) -> str:
    return get_fernet(password).encrypt(s.encode()).decode()

def decrypt(s: str, password: str) -> str:
    return get_fernet(password).decrypt(s.encode()).decode()

def now_s() -> int:
    return int(time.time())

def tg_send(message: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage",
                     params={"chat_id": chat_id, "text": message[:4000], "parse_mode": "Markdown"})
    except Exception:
        pass
