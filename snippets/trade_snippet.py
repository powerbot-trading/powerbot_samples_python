"""
This snippet is a collection of commands used to work with trades in PowerBot
"""
from swagger_client import TradesApi, NewInternalTrade
# Importing generated client from configuration
from configuration import client

"""
Getting Trades
"""
trades = TradesApi(client).get_trades(portfolio_id=["PORTFOLIO_ID"])


"""
Getting Internal Trades
"""
internal_trades = TradesApi(client).get_internal_trades(portfolio_id=["PORTFOLIO_ID"])

"""
Creating Internal Trade
"""
new_internal_trade = NewInternalTrade(
    exchange="epex",
    deliverystart="YYYY-MM-DDTHH:MM:SS.FFFZ",
    deliveryend="YYYY-MM-DDTHH:MM:SS.FFFZ",
    exectime="YYYY-MM-DDTHH:MM:SS.FFFZ",
    buydeliveryarea="DELIVERY_AREA",
    buytxt="TEST",
    buyportfolioid="PORTFOLIO_ID",
    buyaggressorindicator="N",
    selldeliveryarea="DELIVERY_AREA",
    selltxt="TEST",
    sellportfolioid="PORTFOLIO_ID",
    sellaggressorindicator="Y",
    contractid="CONTRACT_ID",
    price=50,
    quantity=10
)

trade = TradesApi(client).add_internal_trade(new_internal_trade)

"""
Recalling a Trade
"""
TradesApi(client).recall_trade("TRADE_ID")


