import json
import logging
import os

logger = logging.getLogger(__name__)


def main():
    path = "config.json"
    config = ServiceConfig.read_config(path)
    print(config)


class Config(object):

    @classmethod
    def read_config(cls, path):
        logger.warning(f"Loading config from: {os.path.abspath(path)}")
        if not os.path.exists(path):
            raise Exception(f"Config not found at: {os.path.abspath(path)}")
        with open(path) as json_file:
            attributes = json.load(json_file)
        config = cls.load_attr(attributes)
        logger.debug(f"\n {json.dumps(attributes, indent=4)}")
        return config

    @classmethod
    def load_attr(cls, attributes):
        config = cls()
        for key, values in attributes.items():
            attr = getattr(config, key)
            if issubclass(attr.__class__, Config):
                object_value = attr.load_attr(values)
                setattr(config, key, object_value)
            else:
                setattr(config, key, values)
        config.init()
        return config

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def init(self):
        pass


class LoggingConfig(Config):
    def __init__(self):
        self.file_path = None
        self.level = logging.DEBUG

    def init(self):
        if self.level == "DEBUG":
            self.level = logging.DEBUG
        elif self.level == "INFO":
            self.level = logging.INFO
        elif self.level == "WARN":
            self.level = logging.WARN
        elif self.level == "ERROR":
            self.level = logging.ERROR


class ServiceConfig(Config):
    def __init__(self):
        self.logging = LoggingConfig()
        self.nn_config = NNConfig()
        self.filename = ""
        self.cam_width = 640
        self.cam_height = 480

    def init(self):
        logging.basicConfig(filename=self.logging.file_path,
                            level=self.logging.level,
                            format='%(asctime)s-%(name)s-%(levelname)s:%(message)s')


class NNConfig(Config):
    def __init__(self):
        self.image_width = 300
        self.image_height = 300
        self.model_xml_path = ""
        self.target_label = 1



if __name__ == '__main__':
    main()
