import configparser
import json
import random

from swagger_client import Configuration, ApiClient, OrdersApi, ContractApi, OrderEntry
from swagger_client.rest import ApiException

# relative path to the config file; this file should contain all
CONF_FILE_PATH = "configuration/conf.ini"

# the folder "swagger_client", which contains all the functionality for interacting with powerbot via rest, can be
# created from the swagger-editor, selecting "Generate Client"->"python"
# the created zip-file contains the folder "swagger_client"

# to run this example, please specify your exchange-url/api-key and a coresponding portfolio-id/delivery-area for this api-key
# at the "conf.ini"-file
# for this api-key, the values "can_read" and "can_trade" must be "true",
# as this example will read the current contracts and post a new order
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
        # the Orders-API to place an order (both defined in the swagger_client)
        #
        contract_api = ContractApi(client)
        order_api = OrdersApi(client)

        # get the currently active contracts from the Contract-API
        order_book = contract_api.get_order_books(delivery_area=delivery_area, portfolio_id=portfolio_id)

        # we select a random contract for which we want to place a new order
        selected_contract = random.choice(order_book.contracts)

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
        response = order_api.add_order(order)

        # summary of the posted order is printed to the console
        print("------------ORDER ADDED------------")
        print(response)
    except ApiException as ex:
        pass
