import configparser
import json
import random

from swagger_client import Configuration, ApiClient, OrdersApi, ContractApi, OrderEntry, MarketApi, BulkSignal, \
    SignalsApi
from swagger_client.rest import ApiException

"""
This example does the following by using REST-Methods provided by PowerBot:
1) Check if the market status is ok
2) Get the current order-book
3) Select a random contract from the order-book
4) Post signal-information for the selected contract
5) Post an order for the selected contract
"""

# todo add swagger_client, install required packages and configure the file conf.ini with your api-key and portfolio

# relative path to the config file; this file should contain all
CONF_FILE_PATH = "configuration/conf.ini"

# the folder "swagger_client", which contains all the functionality for interacting with powerbot via rest, can be
# created from the swagger-editor, selecting "Generate Client"->"python"
# the created zip-file contains the folder "swagger_client"

# to run this example, please specify your exchange-url/api-key and
# a corresponding portfolio-id/delivery-area for this api-key at the "conf.ini"-file
# for this api-key, the values "can_read" and "can_trade" must be "true"
if __name__ == '__main__':

    # set up the configparser to read from the specified configuration file
    # this configuration file contains all necessary information for interacting with powerbot
    conf_file = configparser.ConfigParser(allow_no_value=True)
    conf_file.read(CONF_FILE_PATH)

    # the configuration is read from the configuration file and the values are stored in local variables
    # the exchange_url and the api_key are needed for configuring the APIs

    # the portfolio_id and the delivery are are needed for retriving the currently active contracts and
    # for placing an order
    exchange_url = conf_file["Exchange_Detail"]["exchange_url"]
    api_key = conf_file["Exchange_Detail"]["api_key"]
    portfolio_id = conf_file["Exchange_Detail"]["portfolio_id"]
    delivery_area = conf_file["Exchange_Detail"]["delivery_area"]

    # we surround all the code which interacts
    try:
        # setting up an configuration object (defined in the swagger_client)
        # the exchange_url and api_key are passed to this configuration object
        config = Configuration()
        config.api_key["api_key"] = api_key
        config.host = exchange_url

        # we need this configuration object to set up the API-Client (defined in the swagger_client)
        # this API-Client can be passed to whatever API is needed
        client = ApiClient(config)

        # in this example, we need the Contract-API to retrieve the currently active contracts and
        # the Orders-API to place an order and
        # the Signals-Api to post signals and
        # the Market-API to for checking the market status(all defined in the swagger_client)
        contract_api = ContractApi(client)
        order_api = OrdersApi(client)
        signal_api = SignalsApi(client)
        market_api = MarketApi(client)

        # we get the current market status and check if the market status is OK, otherwise we raise an exception and
        # the script stops
        market_status = market_api.get_status()

        if market_status.status != "OK":
            raise ApiException(status=f"Execution stopped: Market status is {market_status.status}")

        # get the currently active contracts from the Contract-API
        order_book = contract_api.get_order_books(delivery_area=delivery_area, portfolio_id=portfolio_id)

        # we select a random contract for which we want to place a new order
        selected_contract = random.choice(order_book.contracts)

        # define a new signal which we want to post for the selected contract
        # please note that signals are posted for a particular delivery_start and delivery_and time
        # you cannot specify a particular contract_id
        signal = BulkSignal(
            source="TestSource",
            portfolio_ids=[portfolio_id],
            delivery_areas=[delivery_area],
            delivery_start=selected_contract.delivery_start,
            delivery_end=selected_contract.delivery_end,
            value={
                "position_long": 10,
                "position_short": 10
            }
        )

        # we post the created signal to the contract and retrieve the response
        # the field "status" in the response indicates if everything was posted correctly
        signal_response = signal_api.update_signals([signal])

        # summary of the posted order is printed to the console
        print("------------SIGNAL ADDED------------")
        print(signal_response)

        # define the new order which we want to place for the selected contract
        # the order-entry-object is defined in the swagger_client
        order = OrderEntry(
            contract_id=selected_contract.contract_id,
            delivery_area=delivery_area,
            portfolio_id=portfolio_id,
            clearing_acct_type="P",
            quantity=10,
            type="O",
            ordr_exe_restriction="NON",
            validity_res="GFS",
            state="ACTI",
            side="SELL",
            price=100,
            txt=json.dumps({"REST_Example": "Simple Sell Order"})
        )

        # we post the created order to the market and retrieve the response
        # the field "action" in the response specifies what happend to the posted order
        order_response = order_api.add_order(order)

        # summary of the posted order is printed to the console
        print("------------ORDER ADDED------------")
        print(order_response)

    # if there is any problem with a request or if the market status is not ok, the swagger-client will throw an
    # Api-Exception which can be handled here
    except ApiException as ex:
        print(ex)
