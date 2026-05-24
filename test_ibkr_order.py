"""Quick test: place 1 market buy order on IBKR for AAPL then cancel"""
import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

from ib_insync import IB, Stock, MarketOrder

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=99)
print(f"Connected: {ib.isConnected()}")
print(f"Account: {ib.managedAccounts()}")

contract = Stock('AAPL', 'SMART', 'USD')
ib.qualifyContracts(contract)

ticker = ib.reqMktData(contract)
ib.sleep(2)
print(f"AAPL price: {ticker.last}")

# Place market buy for 1 share
order = MarketOrder('BUY', 1)
trade = ib.placeOrder(contract, order)
ib.sleep(2)
print(f"Order placed: {trade.order.orderId}")
print(f"Order status: {trade.orderStatus.status}")

# Cancel it
ib.cancelOrder(trade.order)
ib.sleep(1)
print("Order cancelled")
ib.disconnect()
print("Done - check TWS Orders tab")