from pathlib import Path

curr_path = str(Path.cwd()).split("\\")
config_path = ("\\").join(curr_path[:curr_path.index('powerbot_samples') + 1]) + "/configuration/config.json"
with open(config_path, "r") as configfile:
    config = json.load(configfile)
