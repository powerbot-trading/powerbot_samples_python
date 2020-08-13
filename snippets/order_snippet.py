"""
This snippet is a collection of commands used to work with orders in PowerBot
"""

from swagger_client import OrderModify, OrderEntry, OrdersApi, ContractApi
# Importing generated client from configuration
from configuration import client

"""
Getting the Orderbook
"""
order_book = ContractApi(client).get_order_books(delivery_area="DELIVERY_AREA", portfolio_id="PORTFOLIO")


"""
Placing an Order
"""
# Creating the order object
order = OrderEntry(contract_id="CONTRACT_ID",
                   portfolio_id="PORTFOLIO",
                   delivery_area="DELIVERY_AREA",
                   side='BUY',
                   type= "O",
                   quantity=5,
                   price=35,
                   txt='order_example',
                   clearing_acct_type="P")

# Sending the order object to the market and saving the response
response = OrdersApi(client).add_order(order)


"""
Modifying an Order
"""
result = OrdersApi(client).modify_order(order_id="ORDER_ID",
                                       revision_no="REVISION_NO",
                                       modifications=OrderModify(
                                         action="MODI",
                                         quantity=8,
                                         price=40))


"""
Deleting an Order
"""
result = OrdersApi(client).modify_order(order_id="ORDER_ID",
                                       revision_no="REVISION_NO",
                                       modifications=OrderModify(action="DELE"))


"""
Activating/ Deactivating an Order
"""
# Activating
result = OrdersApi(client).modify_order(order_id="ORDER_ID",
                                       revision_no="REVISION_NO",
                                       modifications=OrderModify(action="ACTI"))

# Deactivating
result = OrdersApi(client).modify_order(order_id="ORDER_ID",
                                       revision_no="REVISION_NO",
                                       modifications=OrderModify(action="DEAC"))