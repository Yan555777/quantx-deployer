from ib_insync import IB, Stock
ib = IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=10)
    print('Connected:', ib.isConnected())
    print('Account:', ib.managedAccounts())
    contract = Stock('AAPL', 'SMART', 'USD')
    ib.qualifyContracts(contract)
    ticker = ib.reqMktData(contract)
    ib.sleep(3)
    print('AAPL last:', ticker.last)
    print('AAPL bid:', ticker.bid)
    ib.disconnect()
    print('SUCCESS')
except Exception as e:
    print('ERROR:', e)
