import time
import stomper
import logging
import uuid
import websocket
import _thread as thread  # Python 3 version of 'thread'
from datetime import datetime


class PowerBotWebSocket():

    def __init__(self, api_key, base_url, subscriptions, data_queue):
        self.__logger = logging.getLogger("PowerBotWebSocketClass")
        self.__logger.setLevel(logging.INFO)
        self.__active = False
        self.__wss = base_url + "?api_key=" + api_key
        self.__subscriptions = subscriptions
        self.__receipt = uuid.uuid4()

        self.__websocket = websocket.WebSocketApp(self.__wss,
                                                  on_close=lambda w: self.__on_close(w),
                                                  on_error=lambda w, e: self.__on_error(w, e),
                                                  on_open=lambda w: self.__on_open(w),
                                                  on_message=lambda w, m: self.__on_message(w, m, data_queue))

    @property
    def is_active(self):
        return self.__active

    def start(self):
        thread.start_new_thread(self.__websocket.run_forever, ())
        # It takes some time before the connection is established.
        time.sleep(3)

    def close(self):
        self.__active = False
        self.__websocket.send(stomper.disconnect(self.__receipt))

    def __on_message(self, ws, message, data_queue):
        if message == "\n":
            self.__logger.info("<<< PONG: {}".format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")))
        else:
            message = stomper.unpack_frame(message)

            if message["cmd"] == "CONNECTED":
                for sub_id, subscription in self.__subscriptions.items():
                    sub = stomper.subscribe(subscription, sub_id)
                    self.__logger.info(sub)
                    ws.send(sub)

            elif message["cmd"] == "MESSAGE":
                data_queue.put(message)

            elif message["cmd"] == "RECEIPT":
                if self.__receipt == message["headers"]["receipt-id"]:
                    ws.close()
                    self.__logger.info("CONNECTION CLOSED")
                else:
                    self.__logger.warning("ERROR WHEN CLOSING CONNECTION! RECEIPT-ID DOES NOT MATCH. {} != {}".format(self.__receipt, message["headers"]["receipt-id"]))

    def __on_error(self, ws, error):
        self.__logger.warning("AN ERROR OCCURRED: {}".format(error))

    def __on_close(self, ws):
        self.__logger.info("CONNECTION CLOSED")

    def __on_open(self, ws):

        def run():
            connect = stomper.Frame()
            connect.setCmd("CONNECT")
            connect.headers = {"accept-version": "1.1", "heart-beat": "10000,10000"}
            ws.send(connect.pack())

            while self.__active:
                self.__websocket.send("\n")
                self.__logger.info(">>> PING: {}".format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")))
                time.sleep(10)

        self.__active = True
        thread.start_new_thread(run, ())
