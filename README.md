 ![PowerBot Logo](https://www.powerbot-trading.com/wp-content/uploads/2018/03/PowerBot_Weblogo.png "PowerBot")
# **PowerBot Samples**
 ***A collection of example scripts for PowerBot***
 
***A more detailed description can be found [here](https://github.com/powerbot-trading/powerbot_samples_python/wiki)***

***Hint:*** *set your general configuration in configuration\config.yaml!*
***
### Content:
1. [Introduction & Setup](#introduction--setup)
2. [Simple Example of a REST call](#simple-example-of-a-rest-call)
3. [Simple Example of a Websocket](#simple-example-of-a-websocket)
4. [Simple Example of an Algorithm](#simple-example-of-an-algorithm)
5. [Advanced Example of an Algorithm](#advanced-example-of-an-algorithm)
***
### Introduction & Setup
The example scripts expect the libraries necessary for the client (listed in requirements.txt) to be installed in the environment you run it in.
To install the requirements in a virtual environment, simply use the provided pipfile to create a new pipenv.

To install them system-wide, open a shell with admin privileges in this folder and run:

	pip install -r requirements.txt

In case you do not have admin privileges simply run:

	pip install -r requirements.txt --user

Additionally, the swagger_client library is required to be in the main directory of the project. 

The client can be generated from https://staging.powerbot-trading.com/playground/epex/v2/admin/editor?url=../swagger-spec
by clicking on "Generate Client" and picking Python. The required folder from the downloaded file is called "swagger_client" and shall be placed in the top directory of the project.

If the client becomes defunct due to API changes, regenerate it in the swagger editor
and replace "swagger_client" folder from the downloaded archive.

To run the run algorithm, the API specifications you should have received have to be provided in the config.yaml in the configuration directory.

Required data:

	API_KEY
	URL
	DELIVERY_AREA
	PORTFOLIO_ID
***
### Simple Example of a REST call
This sample does the following:
First it reads the necessary information from the config-file. This config-file needs to contain the powerbot-url, a 
valid api-key and a corresponding portfolio-id/delivery-area.

The first interaction with PowerBot is checking the market status. Only if the market status is "OK", the execution should
proceed. Otherwise the script will stop. 

If the market status is "OK", the script reads the order-book, which contains all active contracts. A random contract is
selected, a signal is posted and and order is placed.  
***
### Simple Example of a Websocket
This example focuses on establishing a websocket-connection and continuously waits for new events. 
First it reads the necessary information from the config-file.

The example subscribes to the "orderbookchangedevent", so every time something is changing in the order book, the 
change gets added to a queue and the script can react to this change.
***
### Simple Example of an Algorithm
This example algorithm will try close the open position for the next 6 upcoming hourly contracts.
For this purpose the current order book is fetched. The algorithm then iterates over every contract,
extracts the relevant signal information (which is updated ever 5 minutes) from it and places new orders
accordingly.
***
### Advanced Example of an Algorithm
This example algorithm will try to close the open position for the quarter hour contracts of the next
three upcoming hours. The algorithm won't place orders for the entire imbalance immediately, but rather
increase the quantity of each order over time. It first will try to place orders as originator, however,
if these orders have not been executed after 15min, it will act as aggressor (execute orders for the
current market price).
***
