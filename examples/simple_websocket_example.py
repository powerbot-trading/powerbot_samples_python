from queue import Queue
from pathlib import Path
import json
from helpers.websocket_helper import PowerBotWebSocket
"""
This example does the following by using webservice-events provided by PowerBot:
1) Specify to which events you want to subscribe
2) Initialize a queue and start listening for events
3) React to events
"""
# todo add swagger_client, install required packages and configure the file config.json with your api-key and portfolio

# relative path to the config file; this file should contain all parameters
curr_path = str(Path.cwd()).split("\\")
config_path = ("\\").join(curr_path[:curr_path.index('powerbot-samples') + 1]) + "/configuration/config.json"

# the folder "swagger_client", which contains all the functionality for interacting with PowerBot via rest, can be
# created from the swagger-editor, selecting "Generate Client"->"python"
# the created zip-file contains the folder "swagger_client"

# to run this example, please specify your exchange-url/api-key and
# a corresponding portfolio-id/delivery-area for this api-key in the "config.json"-file
# for this api-key, the values "can_read" and "can_trade" must be "true",
# as this example will read the current contracts and post a new order
if __name__ == '__main__':

    # read from the specified configuration file
    # this configuration file contains all necessary information for interacting with PowerBot
    with open(config_path, "r") as configfile:
        config = json.load(configfile)

    # the configuration is read from the configuration file and the values are stored in local variables
    host_url = config["CLIENT_DATA"]["HOST"]
    api_key = config["CLIENT_DATA"]["API_KEY"]
    portfolio_id = config["CONTRACT_DATA"]["PORTFOLIO"]

    # we specify a subscriptions-json, which contains key-value pairs for events we want to subscribe to
    subscription_id = f"orderbook_event_{portfolio_id}"
    subscription_url = f"/topic/orderbookchangedevent-epex.{portfolio_id}"
    subscriptions = {subscription_id: subscription_url}

    # the changed objects are stored into a queue
    queue = Queue()
    # we use this helper class to take away complexity, so we can simply start the websocket-connection and
    # wait for changes
    websocket = PowerBotWebSocket(api_key=api_key, base_url=host_url, subscriptions=subscriptions,
                                  data_queue=queue)
    websocket.start()

    # the script is running as long as the websocket-connection is active, so practically it is running until
    # the script is stopped
    while websocket.is_active:
        # when there are changes detected, they are added to the queue, so we can react to these changes
        if queue.qsize() > 0:
            # todo here goes the logic which should be executed on the websocket event
            print("Event happened")
