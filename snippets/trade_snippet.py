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
    delivery_start="YYYY-MM-DDTHH:MM:SS.FFFZ",
    delivery_end="YYYY-MM-DDTHH:MM:SS.FFFZ",
    exec_time="YYYY-MM-DDTHH:MM:SS.FFFZ",
    buy_delivery_area="DELIVERY_AREA",
    buy_txt="TEST",
    buy_portfolio_id="PORTFOLIO_ID",
    buy_aggressor_indicator="N",
    sell_delivery_area="DELIVERY_AREA",
    sell_txt="TEST",
    sell_portfolio_id="PORTFOLIO_ID",
    sell_aggressor_indicator="Y",
    contract_id="CONTRACT_ID",
    price=50,
    quantity=10
)

trade = TradesApi(client).add_internal_trade(new_internal_trade)

"""
Recalling a Trade
"""
TradesApi(client).recall_trade("TRADE_ID")


