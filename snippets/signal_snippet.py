"""
This snippet is a collection of commands used to work with signals in PowerBot
"""

from swagger_client import SignalsApi, BulkSignal, ContractApi
# Importing generated client from configuration
from configuration import client

"""
Getting Signals
"""
SignalsApi(client).get_signals()


"""
Post Signals (Positions)
"""
# Create Signal Object
signal = BulkSignal(
  source="PositionTestSource",
  portfolio_ids=["PORTFOLIO_ID"],
  delivery_areas=["DELIVERY_AREA"],
  delivery_start="DELIVERY_START",
  delivery_end="DELIVERY_END",
  position_long=10,
  position_short=5
)

# Send to Market
signal_response = SignalsApi(client).update_signals([signal])


"""
Post Signals (Custom Values)
"""
# Create Signal Object
signal = BulkSignal(
  source="CustomTestSource",
  portfolio_ids=["PORTFOLIO_ID"],
  delivery_areas=["DELIVERY_AREA"],
  delivery_start="DELIVERY_START",
  delivery_end="DELIVERY_END",
  value={
    "signal_value_1": 10,
    "signal_value_2": 15
  }
)

# Send to Market
signal_response = SignalsApi(client).update_signals([signal])


"""
Get Orderbook with Signals
"""
ContractApi(client).get_order_books(with_signals=True)