import configparser
from queue import Queue

from helpers.websocket_helper import PowerBotWebSocket

# todo add swagger_client, install required packages and configure the file conf.ini with your api-key and portfolio

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
    conf_file = configparser.ConfigParser()
    conf_file.read(CONF_FILE_PATH)

    # the configuration is read from the configuration file and the values are stored in local variables
    api_key = conf_file["Exchange_Detail"]["api_key"]
    websocket_base_url = conf_file["Exchange_Detail"]["websocket_base_url"]
    portfolio_id = conf_file["Exchange_Detail"]["portfolio_id"]

    # we specify a subscriptions-json, which contains key-value pairs for events we want to subscribe to
    subscription_id = f"orderbook_event_{portfolio_id}"
    subscription_url = f"/topic/orderbookchangedevent-epex.{portfolio_id}"
    subscriptions = {subscription_id: subscription_url}

    # the changed objects are stored into a queue
    queue = Queue()
    # we use this helper class to take away complexity, so we can simply start the websocket-connection and
    # wait for changes
    websocket = PowerBotWebSocket(api_key=api_key, base_url=websocket_base_url, subscriptions=subscriptions,
                                  data_queue=queue)
    websocket.start()

    # the script is running as long as the websocket-connection is active, so practically it is running until
    # the script is stopped
    while websocket.is_active:
        # when there are changes detected, they are added to the queue, so we can react to these changes
        if queue.qsize() > 0:
            # todo here goes the logic which should be executed on the websocket event
            print("Event happened")
