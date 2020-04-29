from pathlib import Path
import yaml

curr_path = str(Path.cwd()).split("\\")
config_path = ("\\").join(curr_path[:curr_path.index('powerbot_samples_python') + 1]) + "/configuration/config.yaml"
with open(config_path, "r") as configfile:
    config = yaml.full_load(configfile)
