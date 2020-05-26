from swagger_client import Configuration, ApiClient
from pathlib import Path
import yaml

curr_path = str(Path.cwd()).split("\\")
config_path = ("\\").join(curr_path[:curr_path.index('powerbot_samples_python') + 1]) + "/configuration/config.yml"
with open(config_path, "r") as configfile:
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

client = init_client(config["API_KEY"], config["HOST"])