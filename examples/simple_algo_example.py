"""
PowerBot simple demo algo script.
(c) 2020 PowerBot GmbH

This example algorithm will try close the open position for the next 6 upcoming hourly contracts.
For this purpose the current order book is fetched. The algorithm then iterates over every contract,
extracts the relevant signal information (which is updated ever 5 minutes) from it and places new orders
accordingly.
"""

import logging
import json
import schedule
import time
import configparser
from pathlib import Path
# PowerBot API generated automatically from the open-api specification using
# https://swagger.io/swagger-codegen/
from swagger_client import Configuration, ApiClient, SignalsApi
from swagger_client.api import MarketApi,  OrdersApi, LogsApi, ContractApi
from swagger_client.models import OrderEntry
from helpers.simple_algo_helper import get_previous_values, get_signal_value, get_position_info, delete_orders, create_signals
# Load Config File
from configuration import config

# Setting up logging for commandline output
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()


def algorithm():
    """
    This method holds the main trading logic.
    """

    # Retrieve the market status of the exchange via PowerBot.
    # We only want to trade if the market status is OK.
    market_status = market_api.get_status()
    if market_status.status == "OK":

        # Get the order book for the next 6 upcoming hourly products (only hourly products are listed in our PRODUCTS variable).
        # Join the list of PRODUCTS to a string, where each product is separated by a comma, as this is the input expected by the API.
        order_book = contract_api.get_order_books(product=",".join(PRODUCTS), limit=6, delivery_area=DELIVERY_AREA, with_signals=True, portfolio_id=[PORTFOLIO_ID])
        hour_counter = 0

        # Now that we have the order book, iterate over each contract and perform the desired calculations.
        for contract in order_book.contracts:
            hour_counter += 1

            # This demo script creates random trade signals, which are incorporated in the logic of our algorithm.
            # These signals were automatically associated with the correct contract depending on their timestamp, i.e. every contract holds an array
            # of signals that we have created.
            # With the function call "get_order_books()" we not only downloaded the market information from the exchange,
            # but also the respective signals stored in PowerBot.
            # With the self-defined helper function "get_signal_value()" we can easily get the signal information and include it in our calculations.
            marginal_price = get_signal_value(contract, "OptSystem", "marginal_price")

            # Position related signals are a special kind of information, but are still submitted and retrieved similar to ordinary signals.
            position_long, position_short = get_position_info(contract)

            # Both "position_long" and "position_short" are submitted as positive numbers.
            # The difference is the quantity we need to close.
            # Place a BUY order if the imbalance is negative; place a SELL order if the imbalance is positive.
            imbalance = position_long - position_short

            # Get the current net position for this contract, i.e. the actual volume that we have already traded at the exchange.
            # The 'abs_pos' element shows the absolute traded quantity (quantity of all BUY and SELL trades for this contract).
            net_position = next(portfolio_info.net_pos for portfolio_info in contract.portfolio_information if portfolio_info.portfolio_id == PORTFOLIO_ID)

            prev_marginal_price = None

            # If imbalance and marginal_price are set, we can perform our simple calculation.
            if imbalance and marginal_price:
                # Create an empty list which we use to keep track of all orders we want to remove from the market.
                to_be_deleted = []

                # Use PowerBot's functionality to retrieve all currently active orders within the portfolio and delivery area that the algorithm is trading in.
                own_orders = orders_api.get_own_orders(contract_id=[contract.contract_id], portfolio_id=[PORTFOLIO_ID], delivery_area=DELIVERY_AREA,
                                                       offset=0, limit=500)

                current_quantity = 0
                for o in own_orders:
                    # EPEX and NordPool provide a text field for submitted orders.
                    # We can use this text field to store further information on each order in JSON format (easier to process).
                    # We save the marginal price which was valid when the order was submitted in this text field.
                    # With the self-defined function "get_previous_values()" we can easily extract this information from an order.
                    # Thus, we can compare the current marginal price that we just submitted with the one that was valid when the order was placed.
                    order_type, prev_hour_counter, prev_marginal_price = get_previous_values(o)

                    # We calculate the impact that all orders for this contract would have on the net position, if they were executed.
                    if order_type == "demo":
                        if o.buy:
                            current_quantity += o.quantity
                        else:
                            current_quantity -= o.quantity
                        to_be_deleted.append(o)

                # Here we check if the marginal price signal has changed since the last iteration.
                # In this example we update the signal values every 5 minutes.
                marginal_price_changed = True if prev_marginal_price and prev_marginal_price != marginal_price else False

                # If the quantity, that needs to be traded, has changed or the marginal price is not the same anymore, then we want to place new orders.
                if (current_quantity + net_position != imbalance) or marginal_price_changed:
                    # Delete previously placed orders with our self defined "delete_orders()" method, since we will replace them with new ones.
                    # If desired, orders can also just be modified instead.
                    delete_orders(orders_api, to_be_deleted, contract.contract_id, PORTFOLIO_ID, DELIVERY_AREA)

                    # Prepare a new order.
                    # Every order needs to be associated with exactly one portfolio.
                    # The fields that need to be set might change depending on the exchange the algorithm is trading at.
                    new_order = OrderEntry(prod=contract.product,
                                           contract_id=contract.contract_id,
                                           portfolio_id=PORTFOLIO_ID,
                                           delivery_area=DELIVERY_AREA,
                                           clearing_acct_type="P",
                                           ordr_exe_restriction="NON",
                                           type="O",
                                           validity_res="GFS",
                                           state="ACTI",
                                           quantity=0,
                                           price=0)

                    # Calculate quantity and price
                    delta_q = imbalance + net_position
                    quantity = 0
                    price_premium = 0
                    if delta_q < 0:
                        new_order.side = "BUY"
                        quantity = abs(delta_q)
                        price_premium = - (hour_counter * 2 - 2)
                    elif delta_q > 0:
                        new_order.side = "SELL"
                        quantity = delta_q
                        price_premium = hour_counter * 2 - 2

                    # Place new order
                    if round(quantity, 1) > 0:
                        # EPEX requires rounding to to 0.1 MW
                        new_order.quantity = round(quantity, 1)
                        # EPEX requires rounding to 0.01 EUR
                        new_order.price = round(marginal_price + price_premium, 2)
                        # Remember current values (for eventual next iteration) and save them in the text field of the order.
                        # The exchange does not disclose this field to any other market participant. Only we can see it.
                        new_order.txt = json.dumps({"type": "demo", "hour_counter": hour_counter, "marginal_price": marginal_price})
                        orders_api.add_orders([new_order])
                        LOGGER.info(f"Created {new_order.side} order for {contract.name} for {new_order.quantity} MW and price { new_order.price}")
                else:
                    LOGGER.info(f"Orders are already placed for contract {contract.name}. No changes since last iteration.")
            else:
                LOGGER.info(f"No signals for contract {contract.name}")

        LOGGER.info("Algo finished.")

    else:
        LOGGER.error(f"Market not ready. {market_status}")


def signals():
    """
    This method can be used to create random signals and submit them to PowerBot.
    """
    # Use the self defined "create_signals()" method to create random signals.
    # We set the position_short parameter to "True" to tell the function to create random position_short values every time we call it.
    random_signals = create_signals(delivery_areas=[DELIVERY_AREA], portfolio_ids=[PORTFOLIO_ID], position_short=True)
    # Use the "update_signals()" method of PowerBot to submit the signals.
    signals_api.update_signals(random_signals)
    LOGGER.info("Created and submitted new signal information.")


if __name__ == '__main__':

    # Get parameters from config file
    API_KEY = config['CLIENT_DATA']['API_KEY']
    URL = config['CLIENT_DATA']['HOST']
    DELIVERY_AREA = config['CONTRACT_DATA']['DELIVERY_AREA']
    PORTFOLIO_ID = config['CONTRACT_DATA']['PORTFOLIO_ID']

    # Define a list of products, which should be included in the order book request.
    # Possible values for EPEX: Intraday_Hour_Power, XBID_Hour_Power, Intraday_Quarter_Hour_Power, XBID_Quarter_Hour_Power
    PRODUCTS = ["Intraday_Hour_Power", "XBID_Hour_Power"]

    # Define the time interval in which the algorithm is executed regularly (in seconds).
    INTERVAL = 30

    # PowerBot api client setup.
    # This utilizes the automatically generated Python library from swagger.
    config = Configuration()
    config.api_key['api_key'] = API_KEY
    config.host = URL

    client = ApiClient(config)
    # Create a new object for every endpoint of the API that you want to use.
    # Available endpoints are listed on swagger.
    market_api = MarketApi(client)
    orders_api = OrdersApi(client)
    contract_api = ContractApi(client)
    logs_api = LogsApi(client)
    # Normally, the signal logic would be completely separate from the actual trading algorithm.
    # This is only done for simplicity purposes in this example.
    signals_api = SignalsApi(client)

    LOGGER.info("Starting algo against {} with api_key {}*****".format(URL, API_KEY[:5]))
    LOGGER.info("Algorithm scheduled to run every: {}s".format(INTERVAL))
    # Initially we have to submit signals or the algorithm does not know what to do.
    signals()

    # Schedule the algorithm to run every 30 seconds (arbitrarily set).
    # PowerBot can handle multiple concurrent requests per second, allowing your algorithm to run highly efficiently.
    schedule.every(30).seconds.do(algorithm)

    # Every 5 minutes we want to update the signals.
    # Again, note that his is only done for showcase purposes.
    schedule.every(5).minutes.do(signals)
    while True:
        schedule.run_pending()
        time.sleep(1)
