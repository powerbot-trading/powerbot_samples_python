 ![PowerBot Logo](https://www.powerbot-trading.com/wp-content/uploads/2018/03/PowerBot_Weblogo.png "PowerBot")
# **PowerBot Tools**
 *Sample scripts and documentation for PowerBot*

***Hint:*** *set your configuration in the config.ini!*
***
####Content:
1. Simple Sample for REST
2. Simple Sample for websocket
***
####1. Simple Sample for REST
This sample does the following:
First it reads the necessary information from the config-file. These config-file needs to contain the powerbot-url, a 
valid api-key and a corresponding portfolio-id/delivery-area.

For beeing able to comunicate with powerbot, the swagger_client needs to be configured.

The first interaction with powerbot is checking the market status. Only if the market status is ok, the execution should
proceed. Otherwise the script will stop. 

If the market status is "OK", the script reads the order-book, which contains all active contracts. A random contract is
selected, a signal is posted and and order is placed.  
***
####2. Simple Sample for websocket
This example focuses on establishing a websocket-connection and continuously waits for new events. 
First it reads the necessary information from the config-file. These config-file needs to contain the 
powerbot-websocket-url, a valid api-key and a corresponding portfolio-id.

The example subscribes to the "orderbookchangedevent", so every time something is changing in the order book, the 
change gets added to a queue and the script can react to this change.
***