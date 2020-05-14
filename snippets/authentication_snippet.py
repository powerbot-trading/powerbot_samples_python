"""
This snippet is a collection of commands used to work with API keys in PowerBot
"""

from swagger_client import AuthenticationApi, NewApiKey
# Importing generated client from configuration
from configuration import client

"""
List API Keys
"""
AuthenticationApi(client).get_api_keys()


"""
Create API Key
"""
NEW_API_KEY_OBJECT = NewApiKey(name="KEY_NAME",
                    description="KEY_DESC",
                    portfolio_ids=["PORTFOLIO_ID"],
                    type="KEY_TYPE",
                    tenant_id="TENANT_ID",
                    can_read=True,
                    can_trade=True,
                    can_signal=True)

# If on Prod and using Master API Key
AuthenticationApi(client).add_api_key(value=NEW_API_KEY_OBJECT, x_exchange_password="EXCHANGE_PASSWORD")
# Else
AuthenticationApi(client).add_api_key(value=NEW_API_KEY_OBJECT)


"""
Update API Key Name
"""
AuthenticationApi(client).update_api_key(name="API_KEY_NAME", value="NEW_API_KEY_NAME")


"""
Update API Key Portfolios
"""
AuthenticationApi(client).update_api_key_portfolios(name="API_KEY_NAME", portfolio_ids=["PORTFOLIO_ID"])


"""
Get current API Key's Portfolios
"""
AuthenticationApi(client).get_current_api_key_portfolios()


"""
Delete API Key
"""
AuthenticationApi(client).delete_api_key(name="API_KEY_NAME")