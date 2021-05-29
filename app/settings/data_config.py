import yaml
from dotmap import DotMap

from models.singleton import Singleton


class Config(metaclass=Singleton):
    instance = None

    def __init__(self, config_file_path, loaded=False):
        global instance
        if loaded:
            data = loaded
        else:
            stream = open(config_file_path, 'r')
            data = yaml.load(stream, Loader=yaml.FullLoader)
        data = DotMap(data)
        instance = data

    @staticmethod
    def get_instance():
        if instance is None:
            raise ValueError('Config accessed before being initialised')
        return instance
