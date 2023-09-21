import json

from application.lib.utils.singleton import ConstantSingleton


class BaseConfig(ConstantSingleton):
    pass


class JsonConfig(BaseConfig):
    def initialize(self, config_file):
        with open(config_file) as fp:
            config = json.load(fp)
        for k, v in config.items():
            setattr(self, k, v)


class DatabaseConfig(JsonConfig):
    connections = {}

    def initialize(self, config_file):
        with open(config_file) as fp:
            config = json.load(fp)
        for k, v in config.items():
            if k == "default":
                setattr(self, k, v)
            else:
                self.connections[k] = v


class ApplicationConfig(JsonConfig):
    pass
