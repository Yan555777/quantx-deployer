"""Quick test: place 1 limit buy order on LongPort for 700.HK"""
import sqlite3
from api.database import get_db, decrypt

# Get credentials from DB
conn = get_db()
student = conn.execute("SELECT * FROM students WHERE email LIKE '%sean%'").fetchone()
conn.close()

app_key = decrypt(student["app_key_enc"])
app_secret = decrypt(student["app_secret_enc"])
access_token = decrypt(student["access_token_enc"])

print(f"Student: {student['email']}")

from longport.openapi import Config, QuoteContext, TradeContext, OrderSide, OrderType, TimeInForceType
import decimal

cfg = Config(app_key=app_key, app_secret=app_secret, access_token=access_token)
quote_ctx = QuoteContext(cfg)
trade_ctx = TradeContext(cfg)

# Get current price
quotes = quote_ctx.quote(["700.HK"])
price = float(quotes[0].last_done)
print(f"700.HK current price: {price}")

# Place limit buy 100 shares (1 lot) at 2% below market
limit_price = round(price * 0.98, 2)
print(f"Placing limit buy: 100 shares @ {limit_price}")

resp = trade_ctx.submit_order(
    symbol="700.HK",
    order_type=OrderType.LO,
    side=OrderSide.Buy,
    submitted_quantity=100,
    time_in_force=TimeInForceType.Day,
    submitted_price=decimal.Decimal(str(limit_price)),
    remark="QuantX test order"
)
print(f"Order submitted! ID: {resp.order_id}")
print("Check LongPort app for the order.")

# Cancel it immediately
import time
time.sleep(2)
trade_ctx.cancel_order(resp.order_id)
print(f"Order cancelled: {resp.order_id}")