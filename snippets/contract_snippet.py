"""
This snippet is a collection of commands used to work with orders in PowerBot
"""

from swagger_client import ContractApi
# Importing generated client from configuration
from configuration import client


"""
Finding a Contract
"""
ContractApi(client).find_contracts(delivery_start="TIME_FROM", delivery_end="TIME_TILL")


"""
Getting Contract History
"""
ContractApi(client).get_contract_history(contract_id="CONTRACT_ID", delivery_area="DELIVERY_AREA")


"""
Getting Portfolio Information for a Contract in a Delivery Area
"""
ContractApi(client).get_limits(contract_id="CONTRACT_ID", delivery_area="DELIVERY_AREA")


"""
Getting Contract Signals
"""
ContractApi(client).get_contract_signals(contract_id="CONTRACT_ID", delivery_area="DELIVERY_AREA")


"""
Getting Public Trades (up to 500 at a time)
"""
ContractApi(client).get_public_trades(
    contract_id="CONTRACT_ID",
    delivery_area="DELIVERY_AREA",
    offset=0,
    limit=500
)


"""
Getting Orderbook for single Contract
"""
ContractApi(client).get_orders(contract_id="CONTRACT_ID", delivery_area="DELIVERY_AREA")


"""
Getting all Orderbooks
"""
ContractApi(client).get_order_books()
