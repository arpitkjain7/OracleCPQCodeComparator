import yaml
import os

path = os.path.join(os.getcwd(), "config.yml")
loader = yaml.SafeLoader


def get_config_data(env: str):
    with open(path) as conf_data:
        config = yaml.load(conf_data, Loader=loader)
        return config.get(env)
