from swagger_client import Configuration, ApiClient
from pathlib import Path
import yaml

with open(Path(__file__).resolve().parent.joinpath("config.yml"), "r") as configfile:
    config = yaml.full_load(configfile)

# Initializing the client with data from config.yml
def init_client(api_key: str, host: str) -> ApiClient:
    """
    Initializes PowerBot Client to enable data requests by the API.

    Args:
        api_key (str): API Key for PowerBot
        host (str): Host URL for PowerBot

    Returns:
        PowerBot ApiClient Object
    """
    config = Configuration()
    config.api_key['api_key'] = api_key
    config.host = host
    return ApiClient(config)


client = init_client(config['CLIENT_DATA']['API_KEY'], config['CLIENT_DATA']['HOST'])