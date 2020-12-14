"""
PowerBot demo algo script.
(c) 2020 PowerBot GmbH

This example algorithm will try to close the open position for the quarter hour contracts of the next
three upcoming hours. The algorithm won't place orders for the entire imbalance immediately, but rather
increase the quantity of each order over time. It first will try to place orders as originator, however,
if these orders have not been executed after 15min, it will act as aggressor (execute orders for the
current market price).
"""

import logging, schedule, time, json
from pathlib import Path
from helpers.advanced_algo_helper import create_signals, get_signal_value, get_imbalance
from datetime import datetime, timedelta
from dateutil import tz
from swagger_client import Configuration, ApiClient, rest
from swagger_client.api import MarketApi, ContractApi, OrdersApi, SignalsApi, LogsApi
from swagger_client.models import OrderModify, OrderEntry
# Load Config File
from configuration import config


# Logging setup
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()


def run():
    """
    The main method that calls our algorithm method, which holds the trading logic.
    It is used for error handling.
    """

    LOGGER.info("Starting new run...")
    retry = True
    retry_counter = 0

    # Every time this method is called, it will try to execute the trading logic.
    # In case the algorithm execution fails because of certain API exceptions, it will retry the execution up to 3 times.
    while retry and retry_counter < 3:
        try:
            if algorithm():
                LOGGER.info("Algorithm exited without errors.")
            else:
                LOGGER.warning("Algorithm exited with problems.")
            retry = False
        except rest.ApiException as api_exception:
            LOGGER.exception(api_exception)
            if api_exception.status in (400, 409):
                # 400: may occur when, an order we want to delete no longer exists.
                # 409: may occur when, the backend has another revision number then the one we submitted via OrdrModify
                # In this case retry the algorithm (max. 3 times).
                LOGGER.warning("Retrying algorithm after ApiException.")
                retry_counter += 1
            else:
                retry = False
        except Exception as e:
            LOGGER.exception(e)
            retry = False


def calc_trade_factor(time_to_delivery_start, offset=timedelta(minutes=30)):
    """
    Method to stepwise increase the traded quantity as the delivery start of a contract comes closer.

    :param time_to_delivery_start: Timedelta object (contract delivery start - now).
    :param offset: 30min before the delivery start we want the traded quantity to be 100%.
    :return: Trade factor indicating how much of the remaining open position will be placed on the market.
    """

    if time_to_delivery_start <= offset:
        trade_factor = 1.0
    elif time_to_delivery_start >= TRADING_WINDOW:
        trade_factor = 0.0
    else:
        remaining_quarter_hours = int(((time_to_delivery_start.total_seconds()-offset.total_seconds())/60)/15)
        trade_factor = (10 - remaining_quarter_hours) / 10
    return trade_factor


def algorithm():
    """
    Method that includes the main logic of the trading strategy.
    :return: True, if the algorithm exited without any problems; False if there were issues with the market.
    """

    # Retrieve the market status and only execute the trading logic if the market is up an running.
    market_status = market_api.get_status()
    if market_status.status != "OK":
        LOGGER.warning(f"Market status is not OK: {market_status}.")
        return False

    # Maximum limit of orders that can be retrieved with a single request is 500.
    # Therefore, a loop is used to ensure that all orders are fetched.
    more_orders = True
    all_own_orders = []
    offset = 0
    while more_orders:
        own_orders = orders_api.get_own_orders(portfolio_id=[PORTFOLIO_ID],
                                               delivery_area=DELIVERY_AREA,
                                               offset=offset,
                                               limit=500)
        all_own_orders.extend(own_orders)
        offset += 500
        more_orders = len(own_orders) == 500

    # Delete all currently active orders to ensure no changes of our net_pos occur, while we execute our trading logic.
    # In the process of retrieving all current orders and deleting them, the orders might get (partially) executed.
    # So these orders might no longer exist or have a changed revision number (happens if they get partially executed).
    # In this case deleting them won't work, because we are sending outdated information to the server.
    # An API exception is thrown and immediately triggers a rerun of the algorithm (up to 3 times).
    for own_order in all_own_orders:
        orders_api.modify_order(order_id=own_order.order_id, revision_no=own_order.revision_no, modifications=OrderModify(action="DELE"))

    # Limit the order book to the next 12 quarter hourly products.
    order_book = contract_api.get_order_books(product=",".join(QUARTER_HOUR_PRODUCTS),
                                              portfolio_id=[PORTFOLIO_ID],
                                              delivery_area=DELIVERY_AREA,
                                              limit=12)

    # Define a list object, in which we will store all our newly created orders.
    # This allows us to bulk submit them at the end, which increases the performance.
    to_be_placed = []

    for contract in order_book.contracts:
        # Calculate the remaining time till the delivery start of the contract.
        # We will use this to adjust the trading factor as well as to evaluate if the contract is within our predefined trading window.
        now = datetime.utcnow().replace(tzinfo=tz.tzutc())
        time_to_delivery_start = contract.delivery_start - now

        if time_to_delivery_start < TRADING_WINDOW:

            # Imbalance is the sum of position long/short signal submitted to PowerBot.
            imbalance = get_imbalance(contract)
            # The net position for a contract is based on the portfolio and is retrieved via the order book.
            net_pos = next(portfolio_info.net_pos for portfolio_info in contract.portfolio_information if portfolio_info.portfolio_id == PORTFOLIO_ID)

            # Every quarter hour 10 percent points are added to the trade factor.
            trade_factor = calc_trade_factor(time_to_delivery_start)
            # Aggressor imbalance
            agg_imbalance = imbalance * (trade_factor - 0.1) if trade_factor - 0.1 > 0 else 0
            # Originator imbalance
            orig_imbalance = imbalance * trade_factor if trade_factor > 0 else 0

            agg_open_pos = agg_imbalance + net_pos
            orig_open_pos = orig_imbalance - agg_imbalance

            if agg_open_pos >= 0 and orig_open_pos >= 0:
                side = "SELL"
            elif agg_open_pos <= 0 and orig_open_pos <= 0:
                side = "BUY"
            elif (agg_open_pos <= 0 and orig_open_pos >= 0) or (agg_open_pos >= 0 and orig_open_pos <= 0):
                # This case may occur when the imbalance signal has drastically changed.
                # We try to close the resulting gap as fast as possible with aggressor orders only.
                agg_open_pos += orig_open_pos
                orig_open_pos = 0
                side = "SELL" if agg_open_pos > 0 else "BUY"

            # Now that we have determined the "side" of our orders we can convert our open positions to absolute values.
            agg_open_pos = abs(round(agg_open_pos, 1))
            orig_open_pos = abs(round(orig_open_pos, 1))

            # Retrieve the maximum/minimum price (submitted as signals) we are willing to accept for the contract.
            max_price = get_signal_value(contract, "OptSystem", "max_price")
            min_price = get_signal_value(contract, "OptSystem", "min_price")

            if agg_open_pos != 0:
                # Calculate the spread if there are Bids and Asks on the market.
                if contract.best_ask_price and contract.best_bid_price:
                    spread = contract.best_ask_price - contract.best_bid_price
                else:
                    spread = None

                max_spread = get_signal_value(contract, "OptSystem", "max_spread")
                if spread and spread < max_spread:
                    # Retrieve all public orders for the contract.
                    public_orders = contract_api.get_orders(contract_id=contract.contract_id,
                                                            delivery_area=DELIVERY_AREA)

                    # The retrieved public orders are unsorted.
                    # We have to sort the orders by price in ascending/descending order, depending on whether we want to buy or sell.
                    sorted_orders = []
                    if side == "BUY":
                        # Ascending order -> start with the lowest price
                        sorted_orders = sorted(public_orders.ask, key=lambda x: x.price)
                    elif side == "SELL":
                        # Descending order -> start with the highest price
                        sorted_orders = sorted(public_orders.bid, key=lambda x: x.price, reverse=True)

                    # Check if the list of orders is empty. If it is, we cannot act as aggressor.
                    if len(sorted_orders) > 0:
                        # Keep track of the quantity we already placed as aggressor.
                        total_aggressor_quantity = 0
                        # Now iterate over the list of sorted public orders (for the specified side) and create
                        # aggressor orders.
                        for o in sorted_orders:
                            # Stop the iteration if:
                            # - a buy order price exceeds the predefined max_price
                            # - a sell order price undercuts the predefined min_price
                            # - the sum of the quantity of the already created orders would exceed the predefined quantity we want to trade.
                            if ((side == "BUY" and o.price < max_price) or (side == "SELL" and o.price > min_price)) and total_aggressor_quantity < agg_open_pos:
                                # Determine the quantity for the aggressor order.
                                # We might have to place multiple orders to reach our desired quantity.
                                # Calculate the remaining open quantity (quantity - total_aggressor_quantity).
                                # Then take the minimum of the open quantity and the offered quantity.
                                aggressor_quantity = min(agg_open_pos - total_aggressor_quantity, o.quantity)

                                aggressor_order = OrderEntry(contract_id=o.contract_id,
                                                             portfolio_id=PORTFOLIO_ID,
                                                             delivery_area=DELIVERY_AREA,
                                                             clearing_acct_type="P",
                                                             ordr_exe_restriction="NON",
                                                             validity_res="GFS",
                                                             state="ACTI",
                                                             quantity=aggressor_quantity,
                                                             side=side,
                                                             price=o.price,
                                                             # Use the text field of an order to store a json encoded string holding meta information.
                                                             txt=json.dumps({"type": "aggressor",
                                                                             "algo_id": ALGO_ID}))

                                total_aggressor_quantity += aggressor_quantity
                                to_be_placed.append(aggressor_order)

                # Create orders for the open originator position.
                if orig_open_pos != 0:
                    margin = get_signal_value(contract, "OptSystem", "margin")

                    if side == "BUY" and contract.best_bid_price:
                        price = contract.best_bid_price + margin
                        price = min(price, max_price)
                    elif side == "SELL" and contract.best_ask_price:
                        price = contract.best_ask_price - margin
                        price = max(price, min_price)
                    else:
                        price = get_signal_value(contract, "OptSystem", "fair_value")

                    originator_order = OrderEntry(contract_id=contract.contract_id,
                                                  portfolio_id=PORTFOLIO_ID,
                                                  delivery_area=DELIVERY_AREA,
                                                  clearing_acct_type="P",
                                                  ordr_exe_restriction="NON",
                                                  validity_res="GFS",
                                                  state="ACTI",
                                                  quantity=orig_open_pos,
                                                  side=side,
                                                  price=price,
                                                  txt=json.dumps({"type": "originator",
                                                                  "algo_id": ALGO_ID}))

                    to_be_placed.append(originator_order)

    # Send our newly created orders to the exchange.
    orders_api.add_orders(to_be_placed, async_req=True)

    # Exit the algorithm and let the calling "run" method know that everything went fine.
    return True


if __name__ == "__main__":

    # Get parameters from config file
    API_KEY = config['CLIENT_DATA']['API_KEY']
    URL = config['CLIENT_DATA']['HOST']
    DELIVERY_AREA = config['CONTRACT_DATA']['DELIVERY_AREA']
    PORTFOLIO_ID = config['CONTRACT_DATA']['PORTFOLIO_ID']

    # Specify the list of products, for which the order book shall be retrieved.
    # Possible values for EPEX: Intraday_Hour_Power, XBID_Hour_Power, Intraday_Quarter_Hour_Power, XBID_Quarter_Hour_Power
    QUARTER_HOUR_PRODUCTS = ["Intraday_Quarter_Hour_Power", "XBID_Quarter_Hour_Power"]

    # Specify a time frame in which orders can be placed.
    # We only want to consider the next 12 upcoming quarter hour contracts.
    TRADING_WINDOW = timedelta(hours=3)

    # Specify an ID for the algorithm, so we can trace orders back to it.
    ALGO_ID = "ALGO1"

    # PowerBot api client setup
    config = Configuration()
    config.api_key["api_key"] = API_KEY
    config.host = URL

    client = ApiClient(config)
    market_api = MarketApi(client)
    contract_api = ContractApi(client)
    orders_api = OrdersApi(client)
    signals_api = SignalsApi(client)
    logs_api = LogsApi(client)

    # Schedule the execution of the example strategy to run every 15min.
    schedule.every().hour.at(":00").do(run)
    schedule.every().hour.at(":15").do(run)
    schedule.every().hour.at(":30").do(run)
    schedule.every().hour.at(":45").do(run)

    LOGGER.info("Starting algo against {} with api_key {}*****".format(URL, API_KEY[:5]))

    # Uncomment these two lines to send the proper signals to PowerBot
    signals = create_signals(0, 7.5, [DELIVERY_AREA], [PORTFOLIO_ID])
    signals_api.update_signals(signals)

    # Uncomment this line to run the example strategy directly, without waiting for the scheduled jobs (only runs once).
    run()

    # Start the scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)
