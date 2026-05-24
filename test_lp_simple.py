import sys, math, decimal, time
sys.path.insert(0, ".")
from api.database import get_db, decrypt

conn = get_db()
student = conn.execute("SELECT * FROM students WHERE email LIKE '%sean%'").fetchone()
conn.close()

app_key = decrypt(student["app_key_enc"])
app_secret = decrypt(student["app_secret_enc"])
access_token = decrypt(student["access_token_enc"])
print(f"Student: {student['email']}")

from longport.openapi import Config, QuoteContext, TradeContext, OrderSide, OrderType, TimeInForceType
cfg = Config(app_key=app_key, app_secret=app_secret, access_token=access_token)
quote_ctx = QuoteContext(cfg)
trade_ctx = TradeContext(cfg)

quotes = quote_ctx.quote(["700.HK"])
price = float(quotes[0].last_done)
print(f"700.HK price: {price}")

tick = 0.20
limit_price = math.floor(price * 0.98 / tick) * tick
limit_price = round(limit_price, 2)
print(f"Limit price (tick-rounded): {limit_price}")

resp = trade_ctx.submit_order(
    symbol="700.HK",
    order_type=OrderType.LO,
    side=OrderSide.Buy,
    submitted_quantity=100,
    time_in_force=TimeInForceType.Day,
    submitted_price=decimal.Decimal(str(limit_price)),
    remark="QuantX test"
)
print(f"Order placed! ID: {resp.order_id}")
print("Check LongPort app now...")
time.sleep(3)
trade_ctx.cancel_order(resp.order_id)
print(f"Order cancelled.")
