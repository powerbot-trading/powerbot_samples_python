 ![PowerBot Logo](https://www.powerbot-trading.com/wp-content/uploads/2018/03/PowerBot_Weblogo.png "PowerBot")
# **PowerBot Samples**
 *Sample scripts and documentation for PowerBot*

***Hint:*** *set your configuration in the config.json!*
***
####Content:
1. Simple Example of a REST call
2. Simple Example of a websocket
3. Simple Example of an Algorithm
4. Advanced Example of an Algorithm
***
####1. Simple Example of a REST call
This sample does the following:
First it reads the necessary information from the config-file. These config-file needs to contain the powerbot-url, a 
valid api-key and a corresponding portfolio-id/delivery-area.

For being able to communicate with PowerBot, the swagger_client needs to be configured.

The first interaction with PowerBot is checking the market status. Only if the market status is ok, the execution should
proceed. Otherwise the script will stop. 

If the market status is "OK", the script reads the order-book, which contains all active contracts. A random contract is
selected, a signal is posted and and order is placed.  
***
####2. Simple Example of a websocket
This example focuses on establishing a websocket-connection and continuously waits for new events. 
First it reads the necessary information from the config-file. The config-file needs to contain the 
powerbot-websocket-url, a valid api-key and a corresponding portfolio-id.

The example subscribes to the "orderbookchangedevent", so every time something is changing in the order book, the 
change gets added to a queue and the script can react to this change.
***
####3. Simple Example of an Algorithm
This example algorithm will try close the open position for the next 6 upcoming hourly contracts.
For this purpose the current order book is fetched. The algorithm then iterates over every contract,
extracts the relevant signal information (which is updated ever 5 minutes) from it and places new orders
accordingly.
***
####4. Advanced Example of an Algorithm
This example algorithm will try to close the open position for the quarter hour contracts of the next
three upcoming hours. The algorithm won't place orders for the entire imbalance immediately, but rather
increase the quantity of each order over time. It first will try to place orders as originator, however,
if these orders have not been executed after 15min, it will act as aggressor (execute orders for the
current market price).
***